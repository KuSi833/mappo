#!/bin/bash
set -x

# Validate critical environment variables
if [ -z "$WANDB_API_KEY_FILE" ]; then
    echo "Error: WANDB_API_KEY_FILE is not set."
    exit 1
fi

if [ -z "$GROUP" ]; then
    echo "Error: GROUP is not set."
    exit 1
fi

HASH=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 4 | head -n 1)
WANDB_API_KEY=$(cat $WANDB_API_KEY_FILE)
name=${USER}_pymarl_${HASH}

echo "Launching container named '${name}'"
# Launches a Singularity container using our image, and runs the provided command

# Set the environment variables for Singularity
export APPTAINER_HOME="$HOME"
export APPTAINER_LANG="$LANG"

# Check if CUDA_VISIBLE_DEVICES is set for GPU jobs
if [ -n "$CUDA_VISIBLE_DEVICES" ]; then
   export APPTAINERENV_CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES"
   NVIDIAFLAG=--nv
fi

# Run the Singularity container with the necessary bindings and environment variables
sg $GROUP -c "singularity run $NVIDIAFLAG \
    --env WANDB_API_KEY=$WANDB_API_KEY \
    --env LANG=$APPTAINER_LANG \
    --env LC_ALL=C.UTF-8 \
    --bind $(pwd)/../../:/home/pymarluser/pymarl \
    --pwd /home/pymarluser/pymarl \
    --contain \
    $SINGULARITY_IMAGE \
    $(printf '%q ' "${@:1}")"
