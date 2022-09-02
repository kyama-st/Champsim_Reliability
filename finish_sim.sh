#!/bin/bash

day=`date '+%F'`
mkdir ../sim_results/${day}/
mkdir ../local_data/${day}/

#copy to github
# cp -vR results_10M_* ../sim_results/${day}/
#copy to local 
# cp -vR results_10M_* ../local_data/${day}/

#delete trace file and results
rm -rf dpc3_traces
rm -rf results_*
# rm *.txt