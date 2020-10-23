critic_REGISTRY = {}

from .centralV import CentralVCritic
from .conv1d_critic import Conv1dCritic
from .vanilla_critic import VanillaCritic

critic_REGISTRY["vanilla"] = VanillaCritic
critic_REGISTRY["central_v"] = CentralVCritic
critic_REGISTRY["conv1d_critic"] = Conv1dCritic
