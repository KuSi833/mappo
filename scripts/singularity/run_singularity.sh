#!/bin/bash
set -x
HASH=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 4 | head -n 1)
WANDB_API_KEY=$(cat $WANDB_API_KEY_FILE)
name=${USER}_pymarl_${HASH}

echo "Launching container named '${name}'"
# Launches a Singularity container using our image, and runs the provided command

cmd=singularity

${cmd} run --nv \
    --env WANDB_API_KEY=$WANDB_API_KEY \
    --env LANG=C.UTF-8 \
    --env LC_ALL=C.UTF-8 \
    --bind $(pwd)/../..:/home/pymarluser/pymarl \
    pymarl_smacv2.sif \
    ${@:1}
