from modules.agents import REGISTRY as agent_REGISTRY
from components.action_selectors import REGISTRY as action_REGISTRY
from components.running_mean_std import RunningMeanStd
import torch as th


# This multi-agent controller shares parameters between agents
class BasicMAC:
    def __init__(self, scheme, groups, args):
        self.n_agents = args.n_agents
        self.args = args
        input_shape = self._get_input_shape(scheme)

        if getattr(args, "is_observation_normalized", None):
            self.is_obs_normalized = True
            self.obs_rms = RunningMeanStd(shape=input_shape)
        else:
            self.is_obs_normalized = False

        self.framestack_num = self.args.env_args.get("framestack_num", None)
        if self.framestack_num:
            assert input_shape % self.framestack_num == 0
            input_shape = (self.framestack_num, input_shape // self.framestack_num) # channels come first
        self._build_agents(input_shape)
        self.agent_output_type = args.agent_output_type
        self.need_agent_logits = getattr(args, "need_agent_logits", False)

        self.action_selector = action_REGISTRY[args.action_selector](args)

        self.hidden_states = None
        self.other_outs = None

    def select_actions(self, ep_batch, t_ep, t_env, bs=slice(None), test_mode=False):
        # Only select actions for the selected batch elements in bs
        avail_actions = ep_batch["avail_actions"][:, t_ep]
        agent_outputs = self.forward(ep_batch, t_ep, test_mode=test_mode)
        chosen_actions = self.action_selector.select_action(agent_outputs[bs], avail_actions[bs], t_env, test_mode=test_mode)
        return chosen_actions

    def update_rms(self, batch_obs):
        self.obs_rms.update(batch_obs)

    def forward_obs(self, obs):
        # obs.shape: num_transitions * num_features
        agent_inputs = obs
        if self.is_obs_normalized:
            agent_inputs = (agent_inputs - self.obs_rms.mean) / (th.sqrt(self.obs_rms.var + 1e-5))
            # agent_inputs = th.clamp(agent_inputs, min=-5.0, max=5.0) # clip to range

        agent_outs, other_outs = self.agent(agent_inputs, self.hidden_states)

        if isinstance(other_outs, dict):
            self.hidden_states = other_outs.pop("hidden_states")
            self.other_outs = other_outs
        else:
            self.hidden_states = other_outs

        if self.agent_output_type == "pi_logits":
            agent_outs = th.nn.functional.log_softmax(agent_outs, dim=-1)

        elif self.agent_output_type == "gaussian_mean":
            raise NotImplementedError

        return agent_outs


    def forward(self, ep_batch, t, test_mode=False):
        agent_inputs = self._build_inputs(ep_batch, t)
        if self.is_obs_normalized:
            agent_inputs = (agent_inputs - self.obs_rms.mean) / th.sqrt(self.obs_rms.var)
            # agent_inputs = th.clamp(agent_inputs, min=-5.0, max=5.0) # clip to range

        avail_actions = ep_batch["avail_actions"][:, t]
        agent_outs, other_outs = self.agent(agent_inputs, self.hidden_states)

        if isinstance(other_outs, dict):
            self.hidden_states = other_outs.pop("hidden_states")
            self.other_outs = other_outs
        else:
            self.hidden_states = other_outs

        if self.agent_output_type == "pi_logits":

            if getattr(self.args, "mask_before_softmax", True):
                # Make the logits for unavailable actions very negative to minimise their affect on the softmax
                reshaped_avail_actions = avail_actions.reshape(ep_batch.batch_size * self.n_agents, -1)
                agent_outs[reshaped_avail_actions == 0] = -1e10

            agent_outs = th.nn.functional.softmax(agent_outs, dim=-1)
            # if not test_mode:
            #     # Epsilon floor
            #     epsilon_action_num = agent_outs.size(-1)
            #     if getattr(self.args, "mask_before_softmax", True):
            #         # With probability epsilon, we will pick an available action uniformly
            #         epsilon_action_num = reshaped_avail_actions.sum(dim=1, keepdim=True).float()

            #     agent_outs = ((1 - self.action_selector.epsilon) * agent_outs
            #                    + th.ones_like(agent_outs) * self.action_selector.epsilon/epsilon_action_num)

            #     if getattr(self.args, "mask_before_softmax", True):
            #         # Zero out the unavailable actions
            #         agent_outs[reshaped_avail_actions == 0] = 0.0

        elif self.agent_output_type == "gaussian_mean":
            raise NotImplementedError

        return agent_outs.view(ep_batch.batch_size, self.n_agents, -1)

    def init_hidden(self, batch_size):
        if self.args.agent != "rnn":
            # only rnn needs to initialize hidden states
            return
        self.hidden_states = self.agent.init_hidden().unsqueeze(0).expand(batch_size, self.n_agents, -1)  # bav

    def parameters(self):
        return self.agent.parameters()

    def load_state(self, other_mac):
        self.agent.load_state_dict(other_mac.agent.state_dict())

    def cuda(self):
        self.agent.cuda()

    def save_models(self, path):
        th.save(self.agent.state_dict(), "{}/agent.th".format(path))

    def load_models(self, path):
        self.agent.load_state_dict(th.load("{}/agent.th".format(path), map_location=lambda storage, loc: storage))

    def _build_agents(self, input_shape):
        self.agent = agent_REGISTRY[self.args.agent](input_shape, self.args)

    def _build_inputs(self, batch, t):
        # Assumes homogenous agents with flat observations.
        # Other MACs might want to e.g. delegate building inputs to each agent
        bs = batch.batch_size
        inputs = []
        inputs.append(batch["obs"][:, t])  # b1av
        if self.args.obs_last_action:
            if t == 0:
                inputs.append(th.zeros_like(batch["actions_onehot"][:, t]))
            else:
                inputs.append(batch["actions_onehot"][:, t-1])
        if self.args.obs_agent_id:
            inputs.append(th.eye(self.n_agents, device=batch.device).unsqueeze(0).expand(bs, -1, -1))

        inputs = th.cat([x.reshape(bs*self.n_agents, -1) for x in inputs], dim=1)
        return inputs

    def _get_input_shape(self, scheme):
        input_shape = scheme["obs"]["vshape"]
        if self.args.obs_last_action:
            input_shape += scheme["actions_onehot"]["vshape"][0]
        if self.args.obs_agent_id:
            input_shape += self.n_agents

        return input_shape
