import numpy as np
import torch as th
import torch.nn as nn
import torch.nn.functional as F

from components.transforms import _check_inputs_validity, _to_batch, _from_batch, _adim, _bsdim, _tdim, _vdim
from models.basic import RNN as RecurrentAgent, DQN as NonRecurrentAgent
from utils.xxx import _n_agent_pairings

class XXXQFunctionLevel1(nn.Module):
    # modelled after https://github.com/oxwhirl/hardercomns/blob/master/code/model/StarCraftMicro.lua 5e00920

    def __init__(self, input_shapes, output_shapes={}, layer_args={}, n_actions=None, args=None):

        super(XXXQFunctionLevel1, self).__init__()

        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        assert set(input_shapes.keys()) == {"main"}, \
            "set of input_shapes does not coincide with model structure!"
        self.input_shapes.update(input_shapes)

        # Set up output_shapes automatically if required
        self.output_shapes = {}
        self.output_shapes["qvalues"] = int(self.n_actions*(self.n_actions-1) / 2) # qvals
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["fc1"] = {"in":self.input_shapes["main"], "out":64}
        self.layer_args["fc2"] = {"in":self.layer_args["fc1"]["out"], "out":self.output_shapes["qvalues"]}
        self.layer_args.update(layer_args)

        # Set up network layers
        self.fc1 = nn.Linear(self.layer_args["fc1"]["in"], self.layer_args["fc1"]["out"])
        self.fc2 = nn.Linear(self.layer_args["fc2"]["in"], self.layer_args["fc2"]["out"])

        # DEBUG
        # self.fc2.weight.data.zero_()
        # self.fc2.bias.data.zero_()

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat):
        # _check_inputs_validity(inputs, self.input_shapes, tformat, allow_nonseq=True)

        main, params, tformat = _to_batch(inputs.get("main"), tformat)
        x = F.relu(self.fc1(main))
        qvalues = self.fc2(x)
        return _from_batch(qvalues, params, tformat)

class XXXQFunctionLevel2(nn.Module):
    # modelled after https://github.com/oxwhirl/hardercomns/blob/master/code/model/StarCraftMicro.lua 5e00920

    def __init__(self, input_shapes, output_shapes={}, layer_args={}, n_actions=None, args=None):

        super(XXXQFunctionLevel2, self).__init__()

        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        assert set(input_shapes.keys()) == {"main"}, \
            "set of input_shapes does not coincide with model structure!"
        self.input_shapes.update(input_shapes)

        # Set up output_shapes automatically if required
        self.output_shapes = {}
        self.output_shapes["qvalues"] = 1 + self.n_actions*self.n_actions # qvals
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["fc1"] = {"in":self.input_shapes["main"], "out":64}
        self.layer_args["fc2"] = {"in":self.layer_args["fc1"]["out"], "out":self.output_shapes["qvalues"]}
        self.layer_args.update(layer_args)

        # Set up network layers
        self.fc1 = nn.Linear(self.layer_args["fc1"]["in"], self.layer_args["fc1"]["out"])
        self.fc2 = nn.Linear(self.layer_args["fc2"]["in"], self.layer_args["fc2"]["out"])

        # DEBUG
        # self.fc2.weight.data.zero_()
        # self.fc2.bias.data.zero_()

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat):
        # _check_inputs_validity(inputs, self.input_shapes, tformat, allow_nonseq=True)

        main, params, tformat = _to_batch(inputs.get("main"), tformat)
        x = F.relu(self.fc1(main))
        qvalues = self.fc2(x)
        return _from_batch(qvalues, params, tformat)

class XXXQFunctionLevel3(nn.Module):
    # modelled after https://github.com/oxwhirl/hardercomns/blob/master/code/model/StarCraftMicro.lua 5e00920

    def __init__(self, input_shapes, output_shapes={}, layer_args={}, n_actions=None, args=None):

        super(XXXQFunctionLevel3, self).__init__()

        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        assert set(input_shapes.keys()) == {"main"}, \
            "set of input_shapes does not coincide with model structure!"
        self.input_shapes.update(input_shapes)

        # Set up output_shapes automatically if required
        self.output_shapes = {}
        self.output_shapes["qvalues"] = self.n_actions # qvals
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["fc1"] = {"in":self.input_shapes["main"], "out":64}
        self.layer_args["fc2"] = {"in":self.layer_args["fc1"]["out"], "out":self.output_shapes["qvalues"]}
        self.layer_args.update(layer_args)

        # Set up network layers
        self.fc1 = nn.Linear(self.layer_args["fc1"]["in"], self.layer_args["fc1"]["out"])
        self.fc2 = nn.Linear(self.layer_args["fc2"]["in"], self.layer_args["fc2"]["out"])

        # DEBUG
        # self.fc2.weight.data.zero_()
        # self.fc2.bias.data.zero_()

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat):
        # _check_inputs_validity(inputs, self.input_shapes, tformat, allow_nonseq=True)

        main, params, tformat = _to_batch(inputs.get("main"), tformat)
        x = F.relu(self.fc1(main))
        qvalues = self.fc2(x)
        return _from_batch(qvalues, params, tformat)


class XXXAdvantage(nn.Module):
    # modelled after https://github.com/oxwhirl/hardercomns/blob/master/code/model/StarCraftMicro.lua 5e00920

    def __init__(self, n_actions, input_shapes, output_shapes={}, layer_args={}, args=None):
        """
        This model contains no network layers
        """
        super(XXXAdvantage, self).__init__()
        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        assert set(input_shapes.keys()) == {"qvalues", "agent_action", "agent_policy", "avail_actions"},\
            "set of input_shapes does not coincide with model structure!"
        self.input_shapes.update(input_shapes)

        pass

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat, baseline = True): # DEBUG!!
        # _check_inputs_validity(inputs, self.input_shapes, tformat)

        qvalues, params_qv, tformat_qv = _to_batch(inputs.get("qvalues").clone(), tformat)
        agent_action, params_aa, tformat_aa = _to_batch(inputs.get("agent_action"), tformat)
        agent_policy, params_ap, tformat_ap = _to_batch(inputs.get("agent_policy"), tformat)

        if baseline:
        # Fuse to XXX advantage
            baseline = th.bmm(
                agent_policy.unsqueeze(1),
                qvalues.unsqueeze(2)).squeeze(2)
        else:
            baseline = 0

        _aa = agent_action.clone()
        _aa = _aa.masked_fill(_aa!=_aa, 0.0)
        Q = th.gather(qvalues, 1, _aa.long())
        Q = Q.masked_fill(agent_action!=agent_action, float("nan"))

        A = Q - baseline

        return _from_batch(A, params_qv, tformat_qv), _from_batch(Q, params_qv, tformat_qv), tformat


class XXXCriticLevel1(nn.Module):

    """
    Concats XXXQFunction and XXXAdvantage together to an advantage and qvalue function
    """

    def __init__(self, input_shapes, n_actions, output_shapes={}, layer_args={}, args=None):
        """
        This model contains no network layers but only sub-models
        """

        super(XXXCriticLevel1, self).__init__()
        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        self.input_shapes["avail_actions"] = self.n_actions
        self.input_shapes.update(input_shapes)

        # Set up output_shapes automatically if required
        self.output_shapes = {}
        self.output_shapes["advantage"] = 1
        self.output_shapes["qvalue"] = 1
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["qfunction"] = {}
        self.layer_args.update(layer_args)

        self.XXXQFunction = XXXQFunctionLevel1(input_shapes={"main":self.input_shapes["qfunction"]},
                                               output_shapes={},
                                               layer_args={"main":self.layer_args["qfunction"]},
                                               n_actions = self.n_actions,
                                               args=self.args)

        self.XXXAdvantage = XXXAdvantage(input_shapes={"avail_actions":self.input_shapes["avail_actions"],
                                                       "qvalues":self.XXXQFunction.output_shapes["qvalues"],
                                                       "agent_action":self.input_shapes["agent_action"],
                                                       "agent_policy":self.input_shapes["agent_policy"]},
                                         output_shapes={},
                                         n_actions=self.n_actions,
                                         args=self.args)

        pass

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat, baseline=True):
        #_check_inputs_validity(inputs, self.input_shapes, tformat)

        qvalues = self.XXXQFunction(inputs={"main":inputs["qfunction"]},
                                    tformat=tformat)

        advantage, qvalue, _ = self.XXXAdvantage(inputs={"avail_actions":qvalues.clone().fill_(1.0),
                                                         # critic level1 has all actions available forever
                                                         "qvalues":qvalues,
                                                         "agent_action":inputs["agent_action"],
                                                         "agent_policy":inputs["agent_policy"]},
                                                  tformat=tformat,
                                                  baseline=baseline)
        return {"advantage": advantage, "qvalue": qvalue}, tformat

class XXXCriticLevel2(nn.Module):

    """
    Concats XXXQFunction and XXXAdvantage together to an advantage and qvalue function
    """

    def __init__(self, input_shapes, n_actions, output_shapes={}, layer_args={}, args=None):
        """
        This model contains no network layers but only sub-models
        """

        super(XXXCriticLevel2, self).__init__()
        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        self.input_shapes.update(input_shapes)

        # Set up output_shapes automatically if required
        self.output_shapes = {}
        self.output_shapes["advantage"] = 1
        self.output_shapes["qvalue"] = 1
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["qfunction"] = {}
        self.layer_args.update(layer_args)

        self.XXXQFunction = XXXQFunctionLevel2(input_shapes={"main":self.input_shapes["qfunction"]},
                                                       output_shapes={},
                                                       layer_args={"main":self.layer_args["qfunction"]},
                                                       n_actions = self.n_actions,
                                                       args=self.args)

        self.XXXAdvantage = XXXAdvantage(input_shapes={"avail_actions":(1 + self.input_shapes["avail_actions_id1"]*self.input_shapes["avail_actions_id2"]),
                                                         "qvalues":self.XXXQFunction.output_shapes["qvalues"],
                                                         "agent_action":self.input_shapes["agent_action"],
                                                         "agent_policy":self.input_shapes["agent_policy"]},
                                         output_shapes={},
                                         n_actions=self.n_actions,
                                         args=self.args)

        pass

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat, baseline=True):
        #_check_inputs_validity(inputs, self.input_shapes, tformat)

        qvalues = self.XXXQFunction(inputs={"main":inputs["qfunction"]},
                                     tformat=tformat)

        advantage, qvalue, _ = self.XXXAdvantage(inputs={"avail_actions":inputs["avail_actions"],
                                                          "qvalues":qvalues,
                                                          "agent_action":inputs["agent_action"],
                                                          "agent_policy":inputs["agent_policy"]},
                                                  tformat=tformat,
                                                  baseline=baseline)
        return {"advantage": advantage, "qvalue": qvalue}, tformat

class XXXCriticLevel3(nn.Module):

    """
    Concats XXXQFunction and XXXAdvantage together to an advantage and qvalue function
    """

    def __init__(self, input_shapes, n_actions, output_shapes={}, layer_args={}, args=None):
        """
        This model contains no network layers but only sub-models
        """

        super(XXXCriticLevel3, self).__init__()
        self.args = args
        self.n_actions = n_actions

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        self.input_shapes.update(input_shapes)

        # Set up output_shapes automatically if required
        self.output_shapes = {}
        self.output_shapes["advantage"] = 1
        self.output_shapes["qvalue"] = 1
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["qfunction"] = {}
        self.layer_args.update(layer_args)

        self.XXXQFunction = XXXQFunctionLevel3(input_shapes={"main":self.input_shapes["qfunction"]},
                                           output_shapes={},
                                           layer_args={"main":self.layer_args["qfunction"]},
                                           n_actions = self.n_actions,
                                           args=self.args)

        self.XXXAdvantage = XXXAdvantage(input_shapes={"avail_actions":self.input_shapes["avail_actions"],
                                                         "qvalues":self.XXXQFunction.output_shapes["qvalues"],
                                                         "agent_action":self.input_shapes["agent_action"],
                                                         "agent_policy":self.input_shapes["agent_policy"]},
                                         output_shapes={},
                                         n_actions=self.n_actions,
                                         args=self.args)

        pass

    def init_hidden(self):
        """
        There's no hidden state required for this model.
        """
        pass


    def forward(self, inputs, tformat, baseline=True):
        #_check_inputs_validity(inputs, self.input_shapes, tformat)

        qvalues = self.XXXQFunctionLevel3(inputs={"main":inputs["qfunction"]},
                                     tformat=tformat)

        advantage, qvalue, _ = self.XXXAdvantage(inputs={"avail_actions":inputs["avail_actions"],
                                                          "qvalues":qvalues,
                                                          "agent_action":inputs["agent_action"],
                                                          "agent_policy":inputs["agent_policy"]},
                                                  tformat=tformat,
                                                  baseline=baseline)
        return {"advantage": advantage, "qvalue": qvalue}, tformat


class XXXNonRecurrentAgentLevel1(NonRecurrentAgent):

    def forward(self, inputs, tformat, loss_fn=None, hidden_states=None, **kwargs):
        test_mode = kwargs["test_mode"]

        avail_actions, params_aa, tformat_aa = _to_batch(inputs["avail_actions"], tformat)
        x, params, tformat = _to_batch(inputs["main"], tformat)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = F.softmax(x, dim=1)

        # mask policy elements corresponding to unavailable actions
        n_available_actions = avail_actions.detach().sum(dim=1, keepdim=True)
        x = th.exp(x)
        x = x.masked_fill(avail_actions == 0, float(np.finfo(np.float32).tiny))
        x = th.div(x, x.sum(dim=1, keepdim=True))

        # add softmax exploration (if switched on)
        if self.args.coma_exploration_mode in ["softmax"] and not test_mode:
            epsilons = inputs["epsilons"].unsqueeze(_tdim(tformat))
            epsilons, _, _ = _to_batch(epsilons, tformat)
            x = avail_actions * epsilons / n_available_actions + x * (1 - epsilons)

        x = _from_batch(x, params, tformat)

        if loss_fn is not None:
            losses, _ = loss_fn(x, tformat=tformat)

        return x, hidden_states, losses, tformat

class MLPEncoder(nn.Module):
    def __init__(self, input_shapes, output_shapes={}, layer_args={}, args=None):
        super(MLPEncoder, self).__init__()
        self.args = args

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        assert set(input_shapes.keys()) == {"main"}, \
            "set of input_shapes does not coincide with model structure!"
        self.input_shapes.update(input_shapes)

        # Set up layer_args automatically if required
        self.output_shapes = {}
        self.output_shapes["fc1"] = 64 # output
        self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["fc1"] = {"in":input_shapes["main"], "out":output_shapes["main"]}
        self.layer_args.update(layer_args)

        #Set up network layers
        self.fc1 = nn.Linear(self.input_shapes["main"], self.output_shapes["main"])
        pass

    def forward(self, inputs, tformat):

        x, n_seq, tformat = _to_batch(inputs["main"], tformat)
        x = F.relu(self.fc1(x))
        return _from_batch(x, n_seq, tformat), tformat


class XXXRecurrentAgentLevel1(nn.Module):

    def __init__(self, input_shapes, n_agents, output_type=None, output_shapes={}, layer_args={}, args=None, **kwargs):
        super(XXXRecurrentAgentLevel1, self).__init__()

        self.args = args
        self.n_agents = n_agents
        assert output_type is not None, "you have to set an output_type!"
        # self.output_type=output_type

        # Set up input regions automatically if required (if sensible)
        self.input_shapes = {}
        # assert set(input_shapes.keys()) == {"main"}, \
        #     "set of input_shapes does not coincide with model structure!"
        self.input_shapes.update(input_shapes)

        # Set up layer_args automatically if required
        self.output_shapes = {}
        self.output_shapes["output"] = _n_agent_pairings(self.n_agents) # output
        if self.output_shapes is not None:
            self.output_shapes.update(output_shapes)

        # Set up layer_args automatically if required
        self.layer_args = {}
        self.layer_args["encoder"] = {"in":self.input_shapes["main"], "out":64}
        self.layer_args["gru"] = {"in":self.layer_args["encoder"]["out"], "hidden":64}
        self.layer_args["output"] = {"in":self.layer_args["gru"]["hidden"], "out":self.output_shapes["output"]}
        self.layer_args.update(layer_args)

        # Set up network layers
        self.encoder = MLPEncoder(input_shapes=dict(main=self.layer_args["encoder"]["in"]),
                                    output_shapes=dict(main=self.layer_args["encoder"]["out"]))
        self.gru = nn.GRUCell(self.layer_args["gru"]["in"], self.layer_args["gru"]["hidden"])
        self.output = nn.Linear(self.layer_args["output"]["in"], self.layer_args["output"]["out"])

    def forward(self, inputs, hidden_states, tformat, loss_fn=None, **kwargs):
        _check_inputs_validity(inputs, self.input_shapes, tformat)

        test_mode = kwargs["test_mode"]
        n_agents = kwargs["n_agents"]

        _inputs = inputs["main"].unsqueeze(0) # as agent dimension is lacking
        #_inputs_aa = inputs["avail_actions"]

        loss = None
        t_dim = _tdim(tformat)
        assert t_dim == 2, "t_dim along unsupported axis"
        t_len = _inputs.shape[t_dim]

        x_list = []
        h_list = [hidden_states]

        for t in range(t_len):

            x = _inputs[:, :, slice(t, t + 1), :].contiguous()
            #avail_actions = _inputs_aa[:, :, slice(t, t + 1), :].contiguous()
            x, tformat = self.encoder({"main":x}, tformat)

            x, params_x, tformat_x = _to_batch(x, tformat)
            #avail_actions, params_aa, tformat_aa = _to_batch(avail_actions, tformat)
            h, params_h, tformat_h = _to_batch(h_list[-1], tformat)

            h = self.gru(x, h)
            x = self.output(h)

            # mask policy elements corresponding to unavailable actions
            #n_available_actions = avail_actions.detach().sum(dim=1, keepdim=True)
            x = th.exp(x)
            #x = x.masked_fill(avail_actions == 0, float(np.finfo(np.float32).tiny))
            x = th.div(x, x.sum(dim=1, keepdim=True))

            # Alternative variant
            #x = th.nn.functional.softmax(x).clone()
            #x.masked_fill_(avail_actions.long() == 0, float(np.finfo(np.float32).tiny))
            #x = th.div(x, x.sum(dim=1, keepdim=True))

            # add softmax exploration (if switched on)
            if self.args.xxx_exploration_mode_level1 in ["softmax"] and not test_mode:
               epsilons = inputs["epsilons_central_level1"].unsqueeze(_tdim(tformat)).unsqueeze(0)
               epsilons, _, _ = _to_batch(epsilons, tformat)
               x =  epsilons / _n_agent_pairings(n_agents) + x * (1 - epsilons)

            h = _from_batch(h, params_h, tformat_h)
            x = _from_batch(x, params_x, tformat_x)

            h_list.append(h)
            x_list.append(x)

        if loss_fn is not None:
            _x = th.cat(x_list, dim=_tdim(tformat))
            loss = loss_fn(_x, tformat=tformat)[0]

        return th.cat(x_list, t_dim), \
               th.cat(h_list[1:], t_dim), \
               loss, \
               tformat

class XXXNonRecurrentAgentLevel2(NonRecurrentAgent):

    def forward(self, inputs, tformat, loss_fn=None, hidden_states=None, **kwargs):
        test_mode = kwargs["test_mode"]

        avail_actions, params_aa, tformat_aa = _to_batch(inputs["avail_actions"], tformat)
        x, params, tformat = _to_batch(inputs["main"], tformat)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = F.softmax(x, dim=1)

        # mask policy elements corresponding to unavailable actions
        n_available_actions = avail_actions.detach().sum(dim=1, keepdim=True)
        x = th.exp(x)
        x = x.masked_fill(avail_actions == 0, float(np.finfo(np.float32).tiny))
        x = th.div(x, x.sum(dim=1, keepdim=True))

        # add softmax exploration (if switched on)
        if self.args.coma_exploration_mode in ["softmax"] and not test_mode:
            epsilons = inputs["epsilons"].unsqueeze(_tdim(tformat))
            epsilons, _, _ = _to_batch(epsilons, tformat)
            x = avail_actions * epsilons / n_available_actions + x * (1 - epsilons)

        x = _from_batch(x, params, tformat)

        if loss_fn is not None:
            losses, _ = loss_fn(x, tformat=tformat)

        return x, hidden_states, losses, tformat

class XXXRecurrentAgentLevel2(RecurrentAgent):

    def forward(self, inputs, hidden_states, tformat, loss_fn=None, **kwargs):
        _check_inputs_validity(inputs, self.input_shapes, tformat)

        test_mode = kwargs["test_mode"]

        _inputs = inputs["main"]
        _inputs_aa = inputs["avail_actions"]

        loss = None
        t_dim = _tdim(tformat)
        assert t_dim == 2, "t_dim along unsupported axis"
        t_len = _inputs.shape[t_dim]

        x_list = []
        h_list = [hidden_states]

        for t in range(t_len):

            x = _inputs[:, :, slice(t, t + 1), :].contiguous()
            avail_actions = _inputs_aa[:, :, slice(t, t + 1), :].contiguous()
            x, tformat = self.encoder({"main":x}, tformat)

            x, params_x, tformat_x = _to_batch(x, tformat)
            avail_actions, params_aa, tformat_aa = _to_batch(avail_actions, tformat)
            h, params_h, tformat_h = _to_batch(h_list[-1], tformat)

            h = self.gru(x, h)
            x = self.output(h)

            # mask policy elements corresponding to unavailable actions
            n_available_actions = avail_actions.detach().sum(dim=1, keepdim=True)
            x = th.exp(x)
            x = x.masked_fill(avail_actions == 0, float(np.finfo(np.float32).tiny))
            x = th.div(x, x.sum(dim=1, keepdim=True))

            # Alternative variant
            #x = th.nn.functional.softmax(x).clone()
            #x.masked_fill_(avail_actions.long() == 0, float(np.finfo(np.float32).tiny))
            #x = th.div(x, x.sum(dim=1, keepdim=True))

            # add softmax exploration (if switched on)
            if self.args.coma_exploration_mode in ["softmax"] and not test_mode:
               epsilons = inputs["epsilons"].unsqueeze(_tdim(tformat))
               epsilons, _, _ = _to_batch(epsilons, tformat)
               x = avail_actions * epsilons / n_available_actions + x * (1 - epsilons)

            h = _from_batch(h, params_h, tformat_h)
            x = _from_batch(x, params_x, tformat_x)

            h_list.append(h)
            x_list.append(x)

        if loss_fn is not None:
            _x = th.cat(x_list, dim=_tdim(tformat))
            loss = loss_fn(_x, tformat=tformat)[0]

        return th.cat(x_list, t_dim), \
               th.cat(h_list[1:], t_dim), \
               loss, \
               tformat

class XXXNonRecurrentAgentLevel3(NonRecurrentAgent):

    def forward(self, inputs, tformat, loss_fn=None, hidden_states=None, **kwargs):
        test_mode = kwargs["test_mode"]

        avail_actions, params_aa, tformat_aa = _to_batch(inputs["avail_actions"], tformat)
        x, params, tformat = _to_batch(inputs["main"], tformat)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = F.softmax(x, dim=1)

        # mask policy elements corresponding to unavailable actions
        n_available_actions = avail_actions.detach().sum(dim=1, keepdim=True)
        x = th.exp(x)
        x = x.masked_fill(avail_actions == 0, float(np.finfo(np.float32).tiny))
        x = th.div(x, x.sum(dim=1, keepdim=True))

        # add softmax exploration (if switched on)
        if self.args.coma_exploration_mode in ["softmax"] and not test_mode:
            epsilons = inputs["epsilons"].unsqueeze(_tdim(tformat))
            epsilons, _, _ = _to_batch(epsilons, tformat)
            x = avail_actions * epsilons / n_available_actions + x * (1 - epsilons)

        x = _from_batch(x, params, tformat)

        if loss_fn is not None:
            losses, _ = loss_fn(x, tformat=tformat)

        return x, hidden_states, losses, tformat

class XXXRecurrentAgentLevel3(RecurrentAgent):

    def forward(self, inputs, hidden_states, tformat, loss_fn=None, **kwargs):
        _check_inputs_validity(inputs, self.input_shapes, tformat)

        test_mode = kwargs["test_mode"]

        _inputs = inputs["main"]
        _inputs_aa = inputs["avail_actions"]

        loss = None
        t_dim = _tdim(tformat)
        assert t_dim == 2, "t_dim along unsupported axis"
        t_len = _inputs.shape[t_dim]

        x_list = []
        h_list = [hidden_states]

        for t in range(t_len):

            x = _inputs[:, :, slice(t, t + 1), :].contiguous()
            avail_actions = _inputs_aa[:, :, slice(t, t + 1), :].contiguous()
            x, tformat = self.encoder({"main":x}, tformat)

            x, params_x, tformat_x = _to_batch(x, tformat)
            avail_actions, params_aa, tformat_aa = _to_batch(avail_actions, tformat)
            h, params_h, tformat_h = _to_batch(h_list[-1], tformat)

            h = self.gru(x, h)
            x = self.output(h)

            # mask policy elements corresponding to unavailable actions
            n_available_actions = avail_actions.detach().sum(dim=1, keepdim=True)
            x = th.exp(x)
            x = x.masked_fill(avail_actions == 0, float(np.finfo(np.float32).tiny))
            x = th.div(x, x.sum(dim=1, keepdim=True))

            # Alternative variant
            #x = th.nn.functional.softmax(x).clone()
            #x.masked_fill_(avail_actions.long() == 0, float(np.finfo(np.float32).tiny))
            #x = th.div(x, x.sum(dim=1, keepdim=True))

            # add softmax exploration (if switched on)
            if self.args.coma_exploration_mode in ["softmax"] and not test_mode:
               epsilons = inputs["epsilons"].unsqueeze(_tdim(tformat))
               epsilons, _, _ = _to_batch(epsilons, tformat)
               x = avail_actions * epsilons / n_available_actions + x * (1 - epsilons)

            h = _from_batch(h, params_h, tformat_h)
            x = _from_batch(x, params_x, tformat_x)

            h_list.append(h)
            x_list.append(x)

        if loss_fn is not None:
            _x = th.cat(x_list, dim=_tdim(tformat))
            loss = loss_fn(_x, tformat=tformat)[0]

        return th.cat(x_list, t_dim), \
               th.cat(h_list[1:], t_dim), \
               loss, \
               tformat
