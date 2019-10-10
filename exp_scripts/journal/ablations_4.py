from run_experiment import extend_param_dicts

server_list = [
    ("woma", [0,1,2,3,4,5,6,7], 2),
]

label = "ablations__13_Aug_2019__v1"
config = "qmix_journal"
env_config = "sc2"

n_repeat = 3 # Just incase some die

parallel_repeat = 1

param_dicts = []

shared_params = {
    "t_max": 2 * 1000 * 1000 + 50 * 1000,
    "test_interval": 2000,
    "test_nepisode": 32,
    "test_greedy": True,
    "env_args.obs_own_health": True,
    "save_model": True,
    "save_model_interval": 25 * 1000,
    "test_interval": 10000,
    "log_interval": 10000,
    "runner_log_interval": 10000,
    "learner_log_interval": 10000,
    "buffer_cpu_only": True, # 5k buffer is too big for VRAM!
}

# QMIX
maps = []
maps += ["2c_vs_64zg"]

for map_name in maps:

    # QMIX LIN SWITCH
    name = "qmix_linswitch__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "mixer": "qmixer_lin_switch",
            "skip_connections": [False],
            "gated": False,
            "mixing_embed_dim": [32],
            "hypernet_layers": [2]
        },
        repeats=2)

    # QMIX 2 Layers no non linearity
    name = "qmix_2lin__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
       {
           "name": name,
           "env_args.map_name": map_name,
           "mixer": "qmix_2layerlin",
           "skip_connections": [False],
           "gated": False,
           "mixing_embed_dim": [32],
           "hypernet_layers": [2]
       },
       repeats=1)


maps = []
maps += ["MMM2"]

for map_name in maps:

    # QMIX LIN SWITCH
    name = "qmix_linswitch__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "mixer": "qmixer_lin_switch",
            "skip_connections": [False],
            "gated": False,
            "mixing_embed_dim": [32],
            "hypernet_layers": [2]
        },
        repeats=2)
