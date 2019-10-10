from run_experiment import extend_param_dicts

server_list = [
    ("dgx1", [5,6,7], 1),
]

label = "qtran__6_Aug_2019_v1"
config = "qtran"
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

# Easy maps
# maps += ["2s3z"]
maps += ["3s5z"]
maps += ["2s_vs_1sc"]

# Medium difficulty
maps += ["3s_vs_5z"]
# maps += ["bane_vs_bane"]
# maps += ["2c_vs_64zg"]
# maps += ["5m_vs_6m"]

# Hard
# maps += ["3s5z_vs_3s6z"]
# maps += ["27m_vs_30m"]
# maps += ["corridor"]
# maps += ["6h_vs_8z"]
# maps += ["MMM2"]

for map_name in maps:
    name = "qtran__{}".format(map_name)
    extend_param_dicts(param_dicts, shared_params,
        {
            "name": name,
            "env_args.map_name": map_name,
            "network_size": "big",
            "mixing_embed_dim": 128,
            "opt_loss": [1], # td_error and these 2 optimise disjoint parameters, so only their relative scaling is important
            "nopt_min_loss": [10],
        },
        repeats=parallel_repeat)
