from run_experiment import extend_param_dicts

server_list = [
    ("woma", [0,1,2,3,4,6,7], 1),
]

label = "qmix_more_tests__16_Aug_2019_v1"
config = "qmix_journal"
env_config = "sc2"

n_repeat = 5 # Just incase some die

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

maps = []
maps += ["2c_vs_64zg"]

for map_name in maps:

    # For longer to see what mixing network ends up like
    name = "qmix__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "skip_connections": [False],
            "gated": False,
            "mixing_embed_dim": [32],
            "hypernet_layers": [2],
            "t_max": 10 * 1000 * 1000 + 50 * 1000,
            "save_model_interval": 250 * 1000,
        },
        repeats=parallel_repeat)

maps = []
maps += ["3s5z"] # Limited gpus, just try it on 3s5z
maps += ["2c_vs_64zg"]

for map_name in maps:

    # tanh
    name = "qmix_tanh__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "skip_connections": [False],
            "gated": False,
            "mixing_embed_dim": [32],
            "hypernet_layers": [2],
            "mixer_non_lin": "tanh",
        },
        repeats=parallel_repeat)

maps = []
maps += ["2s3z"]
maps += ["3s5z"]

for map_name in maps:
    # Longer epsilon anneal time
    name = "qmix__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
           {
               "name": name,
               "env_args.map_name": map_name,
               "skip_connections": [False],
               "gated": False,
               "mixing_embed_dim": [32],
               "hypernet_layers": [2],
               "epsilon_anneal_time": 2 * 1000 * 1000,
           },
           repeats=parallel_repeat)

    name = "vdn__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "mixer": "vdn",
             "epsilon_anneal_time": 2 * 1000 * 1000,
        },
        repeats=parallel_repeat)