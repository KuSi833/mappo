REGISTRY = {}

from .basic_agent import BasicAgentController
from .independent_agents import IndependentMultiagentController
from .coma_agents import COMAMultiAgentController, COMAAgentController
from .iac_agents import IACMultiAgentController, IACAgentController
from .pomace_agents import poMACEMultiagentController
from .mcce_agents import MCCEMultiagentController
from .coma_joint_agents import COMAJointMultiAgentController

REGISTRY["basic_ac"] = BasicAgentController
REGISTRY["coma_recursive_ac"] = COMAAgentController
REGISTRY["iac_recursive_ac"] = IACAgentController
REGISTRY["independent_mac"] = IndependentMultiagentController
REGISTRY["coma_mac"] = COMAMultiAgentController
REGISTRY["iac_mac"] = IACMultiAgentController
REGISTRY["pomace_mac"] = poMACEMultiagentController
REGISTRY["mcce_mac"] = MCCEMultiagentController
REGISTRY["coma_joint_mac"] = COMAJointMultiAgentController

from .vdn_agents import VDNMultiagentController
REGISTRY["vdn_mac"] = VDNMultiagentController

from .qmix_agents import QMIXMultiagentController
REGISTRY["qmix_mac"] = QMIXMultiagentController

from .mackrel_agents import MACKRELMultiagentController
from .mackrel_fo_agents import MACKRELMultiagentController as MACKRELFOMultiagentController
REGISTRY["mackrel_mac"] = MACKRELMultiagentController
REGISTRY["mackrel_fo_mac"] = MACKRELFOMultiagentController