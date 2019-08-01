from run_experiment import extend_param_dicts

server_list = [
    ("gollum", [5,6,7,7,7,5,6,4], 1),
]

label = "hypernet_test__22_July_2019_v1"
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
    "save_model_interval": 2000 * 1000,
    "test_interval": 10000,
    "log_interval": 10000,
    "runner_log_interval": 10000,
    "learner_log_interval": 10000,
    "buffer_cpu_only": True, # 5k buffer is too big for VRAM!
}


maps = []
maps += ["2c_vs_64zg"]

for map_name in maps:
    name = "qmix__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "skip_connections": [True, False],
            "gated": False,
            "mixing_embed_dim": [32, 128],
            "hypernet_layers": [1, 2]
        },
        repeats=parallel_repeat)
