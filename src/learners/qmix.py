from copy import deepcopy
from functools import partial
import torch as th
from torch import nn
from torch.autograd import Variable
from torch.optim import RMSprop

from components.scheme import Scheme
from components.transforms import _adim, _bsdim, _tdim, _vdim, \
    _generate_input_shapes, _generate_scheme_shapes, _build_model_inputs, \
    _join_dicts, _seq_mean, _copy_remove_keys, _make_logging_str, _underscore_to_cap
from models import REGISTRY as m_REGISTRY

from debug.debug import IS_PYCHARM_DEBUG

class QMIXLoss(nn.Module):

    def __init__(self):
        super(QMIXLoss, self).__init__()
    def forward(self, q_tot_values, target, tformat):
        """
        calculate sum_i ||r_{t+1} + max_a Q^i(s_{t+1}, a) - Q^i(s_{t}, a_{t})||_2^2
        where i is agent_id

        inputs: qvalues, actions and targets
        """

        assert tformat in ["a*bs*t*v"], "invalid input format!"

        # targets may legitimately have NaNs - want to zero them out, and also zero out inputs at those positions
        nans = (target != target)
        target[nans] = 0.0
        q_tot_values[nans] = 0.0

        # calculate mean-square loss
        ret = (q_tot_values - target.detach())**2

        # average over whole sequences
        ret = ret.mean(dim=_tdim(tformat), keepdim=True)

        # average over agents
        ret = ret.mean(dim=_adim(tformat), keepdim=True)

        # average over batches
        ret = ret.mean(dim=_bsdim(tformat), keepdim=True)

        output_tformat = "s" # scalar
        return ret, output_tformat

class QMIXLearner():

    def __init__(self, multiagent_controller, logging_struct=None, args=None):
        self.args = args
        self.multiagent_controller = multiagent_controller
        self.n_agents = self.multiagent_controller.n_agents
        self.n_actions = self.multiagent_controller.n_actions
        self.T_q = 0
        self.target_update_interval=args.target_update_interval
        self.stats = {}
        self.logging_struct = logging_struct
        self.last_target_update_T = 0

        self.args_sanity_check()
        pass

    def args_sanity_check(self):
        """
        :return:
        """
        if self.args.td_lambda != 0:
            self.logging_struct.py_logger.warning("For original QMIX, td_lambda should be 0!")
        pass


    def create_models(self, transition_scheme):

        self.network_parameters = self.multiagent_controller.get_parameters()
        self.network_optimiser =  RMSprop(self.network_parameters, lr=self.args.lr_q)

        # calculate a grand joint scheme
        self.joint_scheme_dict = self.multiagent_controller.joint_scheme_dict
        pass

    def train(self, batch_history, T_global=None):
        # ------------------------------------------------------------------------------
        # |  We follow the algorithmic description of COMA as supplied in Algorithm 1  |
        # |  (Counterfactual Multi-Agent Policy Gradients, Foerster et al 2018)        |
        # ------------------------------------------------------------------------------

        # Update target if necessary
        if (self.T_q - self.last_target_update_T) / self.target_update_interval > 1.0:
            self.update_target_nets()
            self.last_target_update_T = self.T_q
            print("updating target net!")

        # create one single batch_history view suitable for all
        data_inputs, data_inputs_tformat = batch_history.view(dict_of_schemes=self.joint_scheme_dict,
                                                              to_cuda=self.args.use_cuda,
                                                              to_variable=True,
                                                              bs_ids=None,
                                                              fill_zero=True)
        # get target outputs for q_tot
        hidden_states, hidden_states_tformat = self.multiagent_controller.generate_initial_hidden_states(
            len(batch_history))

        target_mac_output, \
        target_mac_output_tformat = self.multiagent_controller.get_outputs(data_inputs,
                                                                           hidden_states=hidden_states,
                                                                           loss_fn=None,
                                                                           tformat=data_inputs_tformat,
                                                                           test_mode=True, # irrelevant, as no action selection
                                                                           target_mode=True, # use target network
                                                                           actions="greedy",
                                                                           )
        q_tot = target_mac_output["q_tot"].detach()

        # calculate q_tot targets
        td_targets, \
        td_targets_tformat = batch_history.get_stat("td_lambda_targets",
                                                    bs_ids=None,
                                                    td_lambda=self.args.td_lambda,
                                                    gamma=self.args.gamma,
                                                    value_function_values=q_tot,
                                                    n_agents=1, # have only 1, "central" agent
                                                    to_variable=True,
                                                    to_cuda=self.args.use_cuda)

        # now calculate q_tot from non-target network according to the actions that were actually taken
        actions, actions_tformat = batch_history.get_col(col="actions",
                                                         agent_ids=list(range(self.n_agents)))

        vdl_loss_fn = partial(QMIXLoss(),
                              target=Variable(td_targets, requires_grad=False),)

        hidden_states, hidden_states_tformat = self.multiagent_controller.generate_initial_hidden_states(len(batch_history))

        mac_output, \
        mac_output_tformat = self.multiagent_controller.get_outputs(data_inputs,
                                                                    hidden_states=hidden_states,
                                                                    loss_fn=vdl_loss_fn,
                                                                    tformat=data_inputs_tformat,
                                                                    test_mode=True, # irrelevant, as no action selection!
                                                                    target_mode=False,
                                                                    actions=Variable(actions, requires_grad=False), # setting the actions actually means:
                                                                                     # do not select them again!
                                                                    )

        QMIX_loss = mac_output["losses"]
        QMIX_loss = QMIX_loss.mean()

        # carry out optimization for agents
        self.network_optimiser.zero_grad()
        QMIX_loss.backward()

        policy_grad_norm = th.nn.utils.clip_grad_norm(self.network_parameters, 50)
        self.network_optimiser.step()

        # increase episode counter
        self.T_q += len(batch_history) * batch_history._n_t

        # Calculate statistics
        self._add_stat("q_tot_loss", QMIX_loss.data.cpu().numpy())
        self._add_stat("target_q_mean", target_mac_output["qvalues"].data.cpu().numpy().mean())
        self._add_stat("target_q_tot_mean", target_mac_output["q_tot"].data.cpu().numpy().mean())

        pass

    def update_target_nets(self):
        self.multiagent_controller.update_target()
        pass

    def _add_stat(self, name, value):
        if not hasattr(self, "_stats"):
            self._stats = {}
        if name not in self._stats:
            self._stats[name] = []
            self._stats[name+"_T"] = []
        self._stats[name].append(value)
        self._stats[name+"_T"].append(self.T_q)

        if hasattr(self, "max_stats_len") and len(self._stats) > self.max_stats_len:
            self._stats[name].pop(0)
            self._stats[name+"_T"].pop(0)

        return

    def get_stats(self):
        if hasattr(self, "_stats"):
            return self._stats
        else:
            return []

    def log(self, log_directly = True):
        """
        Each learner has it's own logging routine, which logs directly to the python-wide logger if log_directly==True,
        and returns a logging string otherwise

        Logging is triggered in run.py
        """

        stats = self.get_stats()
        logging_dict =  dict(q_loss = _seq_mean(stats["q_tot_loss"]),
                             target_q_tot_mean=_seq_mean(stats["target_q_tot_mean"]),
                             target_q_mean = _seq_mean(stats["target_q_mean"]),
                             T_q=self.T_q
                            )
        logging_str = "T_q={:g}, ".format(logging_dict["T_q"])
        logging_str += _make_logging_str(_copy_remove_keys(logging_dict, ["T_q"]))

        if log_directly:
            self.logging_struct.py_logger.info("{} LEARNER INFO: {}".format(self.args.learner.upper(), logging_str))

        return logging_str, logging_dict

    def _log(self):
        pass
