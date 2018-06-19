#!/bin/bash

TAG=$1
N_REPEAT=$2
TIMESTAMP=`date "+%d/%m/%y-%H:%M:%S"`
echo "Experiment ${TAG} time stamp: ${TIMESTAMP}"
./mackrel_jakob_sc2_5m__bs8__bias.sh ${TAG} ${TIMESTAMP} ${N_REPEAT} &