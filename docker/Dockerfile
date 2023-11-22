# Using PyTorch with CUDA support as the base image
FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-devel

LABEL maintainer="Christian Schroeder de Witt"

# Install system dependencies
RUN rm /etc/apt/sources.list.d/cuda.list && \
    rm /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get update && \
    apt-get install -y git

# Accept the UID from the build command
ARG UID=1000

# Create a user named pymarluser with the given UID
RUN groupadd -r pymarlgroup && \
    useradd -r -u $UID -g pymarlgroup --create-home pymarluser


# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install \
        numpy \
        scipy \
        pyyaml \
        matplotlib \
        imageio \
        pygame \
        tensorboard-logger \
        ruamel.base \
        ryd \
        wandb \
        pymongo

# Switch to the non-root user
USER pymarluser
WORKDIR /home/pymarluser

# Create install dir
RUN mkdir install && \
    cd install

# Install Sacred (from OxWhirl fork)
RUN pip install \
    jsonpickle==0.9.6 \
    setuptools
RUN git clone https://github.com/oxwhirl/sacred.git && \
    cd sacred && \
    python setup.py install --user

# Install SMAC
ENV smac_ver 1
RUN pip install "protobuf<3.21" git+https://github.com/oxwhirl/smacv2.git
ENV SC2PATH /home/pymarluser/pymarl/3rdparty/StarCraftII

# Install MA Gym
RUN git clone https://github.com/koulanurag/ma-gym.git && \
    cd ma-gym && \
    pip install -e .

# Finalise
RUN mkdir /home/pymarluser/pymarl
WORKDIR /home/pymarluser/pymarl
