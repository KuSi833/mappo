# Using PyTorch with CUDA support as the base image
FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-devel

LABEL maintainer="Christian Schroeder de Witt"

# Install system dependencies
RUN rm /etc/apt/sources.list.d/cuda.list && \
    rm /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get update && \
    apt-get install -y git

# Upgrade pip and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install SMAC
ENV smac_ver 1
RUN pip install "protobuf<3.21" git+https://github.com/oxwhirl/smacv2.git
ENV SC2PATH /home/pymarluser/pymarl/3rdparty/StarCraftII

# Install MA Gym
RUN git clone https://github.com/koulanurag/ma-gym.git && \
    cd ma-gym && \
    pip install -e .

# Create a user named pymarluser with the given UID
ARG UID=1000
RUN groupadd -r pymarlgroup && \
    useradd -r -u $UID -g pymarlgroup --create-home pymarluser

# Finalise
USER pymarluser
RUN mkdir /home/pymarluser/pymarl
WORKDIR /home/pymarluser/pymarl
