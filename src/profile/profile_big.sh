P=`pwd`
cd ../../../

python3 -m cProfile -o $P/blitzz128.out main.py with env=pred_prey n_agents=4 t_max=2400 epsilon_time_length=60 learner=coma t_max=2400 env_args.prey_movement=escape "env_args.predator_prey_shape=(3,3)" env_args.nagent_capture_enabled=False tensorboard=True name="33pp_comatest" target_update_interval=100 agent_model=RNN model_name=predprey_rnnzz observe=True observe_db=True action_selector="multinomial" use_blitzz=True obs_last_action=True batch_size=96

python3 -m cProfile -o $P/blitzz64.out main.py with env=pred_prey n_agents=4 t_max=2400 epsilon_time_length=60 learner=coma t_max=2400 env_args.prey_movement=escape "env_args.predator_prey_shape=(3,3)" env_args.nagent_capture_enabled=False tensorboard=True name="33pp_comatest" target_update_interval=100 agent_model=RNN model_name=predprey_rnnzz observe=True observe_db=True action_selector="multinomial" use_blitzz=True obs_last_action=True batch_size=64


#python3 -m cProfile -o $P/blitzz32.out main.py with env=pred_prey n_agents=4 t_max=2400 epsilon_time_length=60 learner=coma t_max=2400 env_args.prey_movement=escape "env_args.predator_prey_shape=(3,3)" env_args.nagent_capture_enabled=False tensorboard=True name="33pp_comatest" target_update_interval=100 agent_model=RNN model_name=predprey_rnnzz observe=True observe_db=True action_selector="multinomial" use_blitzz=True obs_last_action=True batch_size=32

#python3 -m cProfile -o $P/blitzz4.out main.py with env=pred_prey n_agents=4 t_max=2400 epsilon_time_length=60 learner=coma t_max=2400 env_args.prey_movement=escape "env_args.predator_prey_shape=(3,3)" env_args.nagent_capture_enabled=False tensorboard=True name="33pp_comatest" target_update_interval=100 agent_model=RNN model_name=predprey_rnnzz observe=True observe_db=True action_selector="multinomial" use_blitzz=True obs_last_action=True batch_size=4

#python3 -m cProfile -o $P/blitzz1.out main.py with env=pred_prey n_agents=4 t_max=2400 epsilon_time_length=60 learner=coma t_max=2400 env_args.prey_movement=escape "env_args.predator_prey_shape=(3,3)" env_args.nagent_capture_enabled=False tensorboard=True name="33pp_comatest" target_update_interval=100 agent_model=RNN model_name=predprey_rnnzz observe=True observe_db=True action_selector="multinomial" use_blitzz=True obs_last_action=True batch_size=1

