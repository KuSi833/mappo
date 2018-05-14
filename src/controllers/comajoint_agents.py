import numpy as np
from torch.autograd import Variable
import torch as th

from components.action_selectors import REGISTRY as as_REGISTRY
from components import REGISTRY as co_REGISTRY
from components.scheme import Scheme
from components.episode_buffer import BatchEpisodeBuffer
from components.transforms import _build_model_inputs, _join_dicts, _generate_scheme_shapes, _generate_input_shapes
from models import REGISTRY as m_REGISTRY


class poMACEMultiagentController():
    """
    container object for a set of independent agents
    TODO: may need to propagate test_mode in here as well!
    """

    def __init__(self, runner, n_agents, n_actions, action_selector=None, args=None):
        self.args = args
        self.runner = runner
        self.n_agents = n_agents
        self.n_actions = n_actions
        self.agent_str = args.agent
        self.use_agent_observations = self.args.use_agent_observations
        assert self.args.agent_output_type in ["policies"], "agent_output_type has to be set to 'policies' for coma - makes no sense with other methods!"
        self.agent_output_type = "policies"

        # Set up action selector
        if action_selector is None:
            self.action_selector = as_REGISTRY[args.action_selector](args=self.args)
        else:
            self.action_selector = action_selector

        # self.lambda_network_scheme = Scheme([dict(name="pomace_epsilons",
        #                                           scope="episode",
        #                                           requires_grad=False,
        #                                           switch=self.args.multiagent_controller in ["pomace_mac"] and \
        #                                                  not self.args.pomace_use_epsilon_seed),
        #                                          dict(name="pomace_epsilon_seeds",
        #                                               scope="episode",
        #                                               requires_grad=False,
        #                                               switch=self.args.multiagent_controller in ["pomace_mac"] and \
        #                                                      self.args.pomace_use_epsilon_seed),
        #                                          dict(name="pomace_epsilon_variances",
        #                                               scope="episode",
        #                                               requires_grad=False,
        #                                               switch=self.args.multiagent_controller in ["pomace_mac"]),
        #                                          dict(name="state"),
        #                                          dict(name="agent_id",
        #                                               select_agent_ids=list(range(self.n_agents)))
        #                                          ])

        self.agent_scheme_fn = lambda _agent_id: Scheme([dict(name="agent_id",
                                                       transforms=[("one_hot", dict(range=(0, self.n_agents-1)))],
                                                       select_agent_ids=[_agent_id],),
                                                       dict(name="observations",
                                                           rename="agent_observation",
                                                           select_agent_ids=[_agent_id]),
                                                       dict(name="agent_id", rename="agent_id__flat", select_agent_ids=[_agent_id])])

        # Set up schemes
        self.schemes = {}
        for _agent_id in range(self.n_agents):
            self.schemes["agent_input__agent{}".format(_agent_id)] = self.agent_scheme_fn(_agent_id).agent_flatten()
        self.schemes["coma_joint_network"] = self.coma_joint_network_scheme
        # create joint scheme from the agents schemes and coma_joint_network_scheme
        self.joint_scheme_dict = _join_dicts(self.schemes)

        # construct model-specific input regions
        self.input_columns = {}
        for _agent_id in range(self.n_agents):
            self.input_columns["agent_input__agent{}".format(_agent_id)] = {}
            self.input_columns["agent_input__agent{}".format(_agent_id)]["main"] = \
                Scheme([dict(name="agent_observation", select_agent_ids=[_agent_id]),
                        dict(name="agent_id", select_agent_ids=[_agent_id])],
                       switch=args.use_agent_observations)
            # self.input_columns["agent_input__agent{}".format(_agent_id)]["agent_ids"] = \
            #     Scheme([dict(name="agent_id", select_agent_ids=[_agent_id])])

        self.input_columns["state"] = {}
        self.input_columns["state"]["main"] = Scheme([dict(name="state")])
        # for _agent_id in range(self.n_agents):
        #     self.input_columns["coma_joint_network"]["agent_ids__agent{}".format(_agent_id)] = \
        #         Scheme([dict(name="agent_id",
        #                      select_agent_ids=[_agent_id])])

        pass

    def get_parameters(self):
        parameters = self.coma_joint_network_model.parameters()
        return parameters

    def select_actions(self, inputs, avail_actions, tformat, info, test_mode=False):
        selected_actions, modified_inputs, selected_actions_format = \
            self.action_selector.select_action(inputs,
                                               avail_actions=avail_actions,
                                               tformat=tformat,
                                               test_mode=test_mode)
        return selected_actions, modified_inputs, selected_actions_format

    def create_model(self, transition_scheme):

        self.scheme_shapes = _generate_scheme_shapes(transition_scheme=transition_scheme,
                                                     dict_of_schemes=self.schemes)

        self.input_shapes = _generate_input_shapes(input_columns=self.input_columns,
                                                   scheme_shapes=self.scheme_shapes)

        # set up lambda network
        self.coma_joint_network_model = m_REGISTRY[self.args.pomace_multiagent_network](input_shapes=self.input_shapes,
                                                                                    n_actions=self.n_actions,
                                                                                    n_agents=self.n_agents,
                                                                                    args=self.args)

        if self.args.use_cuda:
            self.coma_joint_network_model = self.coma_joint_network_model.cuda()
        return

    def generate_initial_hidden_states(self, batch_size):
        """
        generates initial hidden states for each agent
        TODO: would be nice to expand for use with recurrency in lambda (could just be last first slice of hidden states though, \
        or dict element
        """
        agent_hidden_states = th.stack([Variable(th.zeros(batch_size, 1, self.args.agents_hidden_state_size)) for _
                                        in range(self.n_agents)])
        agent_hidden_states = agent_hidden_states.cuda() if self.args.use_cuda else agent_hidden_states.cpu()
        return agent_hidden_states, "a*bs*t*v"

    def share_memory(self):
        self.coma_joint_network_model.share_memory()
        pass

    def get_outputs(self, inputs, hidden_states, tformat, loss_fn=None, **kwargs):
        assert isinstance(inputs, dict) and \
               isinstance(inputs["agent_input__agent0"], BatchEpisodeBuffer), "wrong format (inputs)"
        if self.args.share_agent_params:
            inputs, inputs_tformat = _build_model_inputs(self.input_columns,
                                                         inputs,
                                                         to_variable=True,
                                                         inputs_tformat=tformat)

            out, hidden_states, losses, tformat = self.coma_joint_network_model(inputs,
                                                                            hidden_states=hidden_states,
                                                                            loss_fn=loss_fn,
                                                                            tformat=inputs_tformat,
                                                                            **kwargs)
            ret = {"hidden_states": hidden_states,
                   "losses": losses,
                   "format": tformat}

            out_key = self.agent_output_type
            ret[out_key] = out

            return ret, tformat
        else:
            assert False, "Not yet implemented."

    def save_models(self, path, token, T):
        if self.args.share_agent_params:
            th.save(self.agent_model.state_dict(),
                    "results/models/{}/{}_agentsp__{}_T.weights".format(token, self.args.learner, T))
        else:
            for _agent_id in range(self.args.n_agents):
                th.save(self.agent_models["agent__agent{}".format(_agent_id)].state_dict(),
                        "results/models/{}/{}_agent{}__{}_T.weights".format(token, self.args.learner, _agent_id, T))

        th.save(self.coma_joint_network_model.state_dict(),
                        "results/models/{}/{}_coma_joint_network{}__T.weights".format(token, self.args.learner, T))

        pass

    pass




# from components.scheme import Scheme
# from controllers.basic_agent import BasicAgentController
# from controllers.independent_agents import IndependentMultiagentController
#
# class COMAAgentController(BasicAgentController):
#
#     def __init__(self, n_agents, n_actions, args, agent_id=None, model=None, output_type="policies", scheme=None):
#
#         scheme_fn = lambda _agent_id: Scheme([dict(name="agent_id",
#                                                    transforms=[("one_hot",dict(range=(0, n_agents-1)))],
#                                                    select_agent_ids=[_agent_id],),
#                                                    # better to have ON all the time as shared_params
#                                                    #switch=self.args.obs_agent_id),
#                                               dict(name="observations",
#                                                    rename="agent_observation",
#                                                    select_agent_ids=[_agent_id]),
#                                               dict(name="actions",
#                                                    rename="past_action",
#                                                    select_agent_ids=[_agent_id],
#                                                    transforms=[("shift", dict(steps=1)),
#                                                                ("one_hot", dict(range=(0, n_actions-1)))], # DEBUG!
#                                                    switch=args.obs_last_action),
#                                               dict(name="coma_epsilons",
#                                                    rename="epsilons",
#                                                    scope="episode"),
#                                               dict(name="avail_actions",
#                                                    select_agent_ids=[_agent_id])
#                                              ]).agent_flatten()
#
#         input_columns = {}
#         input_columns["main"] = {}
#         input_columns["main"]["avail_actions"] = Scheme([dict(name="avail_actions", select_agent_ids=[agent_id])]).agent_flatten()
#         input_columns["main"]["epsilons"] = Scheme([dict(name="epsilons", scope="episode")]).agent_flatten()
#         input_columns["main"]["main"] = Scheme([dict(name="state", select_agent_ids=[agent_id])]).agent_flatten()
#
#         if model is not None:
#             assert model in ["coma_recursive", "coma_non_recursive"], "wrong COMA model set!"
#
#         super().__init__(n_agents=n_agents,
#                          n_actions=n_actions,
#                          args=args,
#                          agent_id=agent_id,
#                          model=model,
#                          scheme_fn=scheme_fn,
#                          input_columns=input_columns)
#         pass
#
# class COMAMultiAgentController(IndependentMultiagentController):
#
#     def __init__(self, runner, n_agents, n_actions, action_selector=None, args=None, **kwargs):
#         assert args.action_selector in ["multinomial"], "wrong COMA action selector set!"
#         assert args.agent in ["coma_recursive_ac", "coma_non_recursive_ac"], "wrong COMA model set!"
#
#         super().__init__(runner=runner,
#                          n_agents=n_agents,
#                          n_actions=n_actions,
#                          action_selector=action_selector,
#                          args=args,
#                          **kwargs)
#         pass


