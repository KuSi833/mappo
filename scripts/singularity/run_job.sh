#!/bin/bash

# File used to initiate an SGE queue job

# Job name
JOB_NAME="MULTITHREADING"

# Timestamp format: YYYYMMDD-HHMMSS
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Output file name with job name and timestamp
OUTPUT_PATH="../../logs/"
OUTPUT_FILE="${OUTPUT_PATH}${JOB_NAME}-${TIMESTAMP}.txt"

mkdir -p ${OUTPUT_PATH}

# Submit the job to SGE
qsub -N "$JOB_NAME" -o "$OUTPUT_FILE" run.jobscript clipping_rnn_central_V "$JOB_NAME"