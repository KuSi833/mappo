import datetime
from functools import partial
from math import ceil
import numpy as np
import os
import pprint
import tensorboard
if tensorboard:
    from tensorboard_logger import configure, log_value
import time
import threading
import torch as th
from types import SimpleNamespace as SN
from utils.dict2namedtuple import convert
from utils.logging import get_logger, append_scalar, log_stats
from utils.timehelper import time_left, time_str

from components.replay_buffer import ReplayBuffer
from learners import REGISTRY as le_REGISTRY
from runners import REGISTRY as r_REGISTRY

def run(_run, _config, _log, pymongo_client):
    #------------------------------------------------------------------------------------------------------------------
    # Launch point for DeepMARL framework
    # Christian Schroeder de Witt 2018, caschroeder@outlook.com
    #
    #------------------------------------------------------------------------------------------------------------------

    # check args sanity
    _config = args_sanity_check(_config, _log)

    # convert _config dict to GenericDict objects (which cannot be overwritten later)
    args = convert(_config)
    _log.info("Experiment Parameters:")
    experiment_params = pprint.pformat(_config,
                                       indent=4,
                                       width=1)
    _log.info("\n\n" + experiment_params + "\n")

    # ----- configure logging
    # configure tensorboard logger
    unique_token = "{}__{}".format(args.name, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    if tensorboard:
        import os
        from os.path import dirname, abspath
        file_tb_path = os.path.join(dirname(dirname(abspath(__file__))), "tb_logs")
        configure(os.path.join(file_tb_path, "{}").format(unique_token))

    # set up logging object to be passed on from now on
    logging_struct = SN(py_logger=_log,
                        sacred_log_scalar_fn=partial(append_scalar, run=_run))
    if tensorboard:
        logging_struct.tensorboard_log_scalar_fn=log_value

    # ----- execute runners
    # run framework in run_mode selected
    if args.run_mode in ["parallel_subproc"]:
        run_parallel(args=args, _run=_run, _logging_struct=logging_struct, unique_token=unique_token)
    else:
        run_sequential(args=args, _run=_run, _logging_struct=logging_struct, unique_token=unique_token)

    #Clean up after finishing
    print("Exiting Main")

    if pymongo_client is not None: #args.use_mongodb:
        print("Attempting to close mongodb client")
        pymongo_client.close()
        print("Mongodb client closed")

    print("Stopping all threads")
    for t in threading.enumerate():
        if t.name != "MainThread":
            print("Thread {} is alive! Is daemon: {}".format(t.name, t.daemon))
            t.join(timeout=1)
            print("Thread joined")

    print("Exiting script")

    # Making sure framework really exits
    exit()


def args_sanity_check(config, _log):

    # set CUDA flags
    config["use_cuda"] = True # Use cuda whenever possible!
    if config["use_cuda"] and not th.cuda.is_available():
        config["use_cuda"] = False
        _log.warning("CUDA flag use_cuda was switched OFF automatically because no CUDA devices are available!")

    assert (config["run_mode"] in ["parallel_subproc"] and config["use_replay_buffer"]) or (not config["run_mode"] in ["parallel_subproc"]),  \
        "need to use replay buffer if running in parallel mode!"

    assert not (not config["use_replay_buffer"] and (config["batch_size_run"]!=config["batch_size"]) ) , "if not using replay buffer, require batch_size and batch_size_run to be the same."

    if config["learner"] == "coma":
       assert (config["run_mode"] in ["parallel_subproc"]  and config["batch_size_run"]==config["batch_size"]) or \
       (not config["run_mode"] in ["parallel_subproc"]  and not config["use_replay_buffer"]), \
           "cannot use replay buffer for coma, unless in parallel mode, when it needs to have exactly have size batch_size."

    return config

def run_parallel(args, _logging_struct, _run, unique_token):
    """
     this run mode runs runner and learner in parallel subprocesses and uses a specially protected shared replay buffer in between
     TODO: under construction!
     """
    from torch import multiprocessing as mp
    def runner_process(self, args):
        """
        TODO: add inter-process communication
        :return:
        """
        runner_train_obj = r_REGISTRY[args.runner](args=args)
        while True:
            runner_train_obj.run()
        pass

    def learner_process():
        """
        TODO: add inter-process communication
        :return:
        """
        runner_test_obj = r_REGISTRY[args.runner](multiagent_controller=runner_train_obj.multiagent_controller,
                                                  args=args,
                                                  test_mode=True)
        while True:
            runner_test_obj.run()
        pass

    runner_obj = NStepRunner(args=args)
    runner_obj.share_memory()

    test_runner_obj = NStepRunner(multiagent_controller=runner_obj.multiagent_controller,
                                  args=args)
    test_runner_obj.share_memory()

    # TODO: Create a data scheme registry (possibly with yaml files or sth)
    replay_buffer = ReplayBuffer(scheme, args.buffer_size, is_cuda=True, is_shared_mem=True)

    mp.set_start_method('forkserver')
    runner_proc = mp.Process(target=runner_process, args=(runner_obj, replay_buffer,))
    learner_proc = mp.Process(target=learner_process, args=(learner_obj, replay_buffer,))
    runner_proc.start()
    learner_proc.start()

    ###
    #  Main process keeps train / runner ratios roughly in sync, caters for logging and termination
    ###
    while True:
        break

    runner_proc.join()
    learner_proc.join()

def run_sequential(args, _logging_struct, _run, unique_token):

    # set up train runner
    runner_obj = r_REGISTRY[args.runner](args=args,
                                         logging_struct=_logging_struct)

    # create the learner
    learner_obj = le_REGISTRY[args.learner](multiagent_controller=runner_obj.multiagent_controller,
                                            logging_struct=_logging_struct,
                                            args=args)

    # create non-agent models required by learner
    learner_obj.create_models(runner_obj.data_scheme)

    # set up replay buffer (if enabled)
    buffer = None
    if args.use_replay_buffer:
        buffer = ReplayBuffer(data_scheme=runner_obj.data_scheme,
                              n_bs=args.buffer_size,
                              n_t=runner_obj.env_episode_limit + 1,
                              n_agents=runner_obj.n_agents,
                              batch_size=args.batch_size,
                              is_cuda=args.use_cuda,
                              is_shared_mem=not args.use_cuda,
                              logging_struct=_logging_struct)

    #---- start training

    T = 0
    episode = 0
    last_test_T = 0
    # start_time = time.time()

    _logging_struct.py_logger.info("Beginning training for {} timesteps".format(args.t_max))

    while T <= args.t_max:

        # Run for a whole episode at a time
        episode_rollout = runner_obj.run(T_global=T, test_mode=False)
        T = runner_obj.T

        episode_sample = None
        if args.use_replay_buffer:
            buffer.put(episode_rollout)
            T = runner_obj.T

            if buffer.can_sample(args.batch_size):
                episode_sample = buffer.sample(args.batch_size, seq_len=0)
        else:
            episode_sample = episode_rollout

        learner_obj.train(episode_sample, T_global=T)

        # Execute test runs once in a while
        n_test_runs = max(1, args.test_nepisode // runner_obj.batch_size)
        if (T - last_test_T) / args.test_interval > 1.0:

            _logging_struct.py_logger.info("T_global: {}".format(T))
            runner_obj.log() # log runner statistics derived from training runs

            last_test_T = T
            for _ in range(n_test_runs):
                runner_obj.run(T_global=T, test_mode=True)

            runner_obj.log()  # log runner statistics derived from test runs
            learner_obj.log()

        # save model once in a while
        if args.save_model and T - model_save_time >= args.t_max // args.save_model_interval:
            model_save_time = T
            _logging_struct.py_logger.info("Saving models")

            save_path = "results/models/{}".format(unique_token)
            os.makedirs(save_path, exist_ok=True)

            # learner obj will save all agent and further models used
            learner_obj.save_models(path=save_path, token=unique_token, time=T)

        episode += 1

    _logging_struct.py_logger.info("Finished Training")
    # end of parallel / anti-parallel branch