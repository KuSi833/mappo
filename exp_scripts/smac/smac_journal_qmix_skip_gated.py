from run_experiment import extend_param_dicts

server_list = [
    ("gollum", [6,7], 3),
]

label = "journal_skip_gated_connections_test__24_June_2019_v1"
config = "qmix_smac"
env_config = "sc2"

n_repeat = 6 # Just incase some die

parallel_repeat = 2

param_dicts = []

shared_params = {
    "t_max": 10 * 1000 * 1000 + 50 * 1000,
    "test_interval": 2000,
    "test_nepisode": 24,
    "test_greedy": True,
    "env_args.obs_own_health": True,
    "save_model": True,
    "save_model_interval": 2000 * 1000,
    "test_interval": 20000,
    "log_interval": 20000,
    "runner_log_interval": 20000,
    "learner_log_interval": 20000,
    "buffer_cpu_only": True, # 5k buffer is too big for VRAM!
}


maps = []
maps += ["25m", "micro_retarget", "3s5z"]

for map_name in maps:
    name = "qmix_skip_gate__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "skip_connections": True,
            "gated": True,
        },
        repeats=parallel_repeat)