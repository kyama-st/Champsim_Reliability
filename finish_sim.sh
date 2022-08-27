#!/bin/bash

day=`date '+%F'`

#copy to github
cp -vR results_10M_* ../sim_results/$day/
#copy to local 
cp -vR results_10M_* ../local_data/$day/
rm -rf dpc3_traces
rm -rf results_*
rm *.txt