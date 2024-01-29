#!/bin/bash
# debug=
# debug=echo
trap 'onCtrlC' INT

function onCtrlC () {
  echo 'Ctrl+C is captured'
  for pid in $(jobs -p); do
    kill -9 $pid
  done
  
  kill -HUP $( ps -A -ostat,ppid | grep -e '^[Zz]' | awk '{print $2}')
  exit 1
}

config=$1  # qmix
tag=$2
units=${3:-5}   # MMM2 left out
clipping_range=0.1
lr=0.0005
offset=0
maps=${8:-sc2_gen_protoss,sc2_gen_zerg,sc2_gen_terran,sc2_gen_protoss_open_loop,sc2_gen_terran_open_loop,sc2_gen_zerg_open_loop}
#processes=1 # 2
gpus=${CUDA_VISIBLE_DEVICES}
processes=${#gpus[@]}
args=${5:-}    # ""
times=1   # 5

maps=(${maps//,/ })
gpus=(${gpus//,/ })
args=(${args//,/ })
units=(${units//,/ })
lrs=(${lr//,/ })
clipping_ranges=(${clipping_range//,/ })

if [ ! $config ] || [ ! $tag ]; then
    echo "Please enter the correct command."
    echo "bash run.sh config_name map_name_list (experinments_threads_num arg_list gpu_list experinments_num)"
    exit 1
fi

echo "CONFIG:" $config
echo "MAP LIST:" ${maps[@]}
echo "CONCURRENT PROCESSES:" $processes
echo "ARGS:"  ${args[@]}
echo "GPU LIST:" ${gpus[@]}
echo "TIMES:" $times


# run parallel
count=0
for lr in "${lrs[@]}"; do
    for clipping_range in "${clipping_ranges[@]}"; do
        for map in "${maps[@]}"; do
            for((i=0;i<times;i++)); do
                for unit in "${units[@]}"; do
                    gpu=${gpus[$(($count % ${#gpus[@]}))]}
                    group="${config}-${tag}"
                    enemies=$(($unit + $offset))
                    $debug ./run_singularity.sh $gpu python3 src/main.py --no-mongo --config="$config" --env-config="$map" with env_args.capability_config.n_units=$unit env_args.capability_config.n_enemies=$enemies group="$group" clip_range=$clipping_range lr_actor=$lr use_wandb=True save_model=True "${args[@]}" &

                    count=$(($count + 1))     
                    if [ $(($count % $processes)) -eq 0 ]; then
                        wait
                    fi
                    # for random seeds
                    sleep $((RANDOM % 3 + 3))
        	done 
            done
        done
    done
done
wait
