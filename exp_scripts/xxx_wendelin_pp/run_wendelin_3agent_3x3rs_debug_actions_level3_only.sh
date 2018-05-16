#!/bin/bash

TAG=$1
N_REPEAT=$2
TIMESTAMP=`date "+%d/%m/%y-%H:%M:%S"`
echo "Experiment ${TAG} time stamp: ${TIMESTAMP}"
./wendelin_3agent_3x3rs_debug_actions_level3_only ${TAG} ${TIMESTAMP} ${N_REPEAT} &