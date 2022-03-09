#!/bin/bash
debug=
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
units=${3:-5,15,50}   # MMM2 left out
maps=${8:-sc2_gen_protoss,sc2_gen_zerg,sc2_gen_terran}
threads=${4:-24} # 2
args=${5:-}    # ""
gpus=${6:-0,1,2,3,4,5,6,7}    # 0,1,2
times=${7:-3}   # 5

maps=(${maps//,/ })
gpus=(${gpus//,/ })
args=(${args//,/ })
units=(${units//,/ })

if [ ! $config ] || [ ! $tag ]; then
    echo "Please enter the correct command."
    echo "bash run.sh config_name map_name_list (experinments_threads_num arg_list gpu_list experinments_num)"
    exit 1
fi

echo "CONFIG:" $config
echo "MAP LIST:" ${maps[@]}
echo "THREADS:" $threads
echo "ARGS:"  ${args[@]}
echo "GPU LIST:" ${gpus[@]}
echo "TIMES:" $times


# run parallel
count=0
for map in "${maps[@]}"; do
    for((i=0;i<times;i++)); do
        for unit in "${units[@]}"; do
            gpu=${gpus[$(($count % ${#gpus[@]}))]}  
            group="${config}-${tag}"
            $debug ./run_docker.sh $gpu python3 src/main.py --no-mongo --config="$config" --env-config="$map" with env_args.n_units=$unit group="$group" "${args[@]}" &

            count=$(($count + 1))     
            if [ $(($count % $threads)) -eq 0 ]; then
                wait
            fi
            # for random seeds
            sleep $((RANDOM % 60 + 10))
        done 
    done
done
wait
