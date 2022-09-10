#!/bin/bash

# day=`date '+%F'`
# mkdir ../sim_results/${day}/
# mkdir ../local_data/${day}/

#copy to github
# cp -vR results_10M_* ../sim_results/${day}/
# cp -vR Wr_ratio_* ../sim_results/${day}/
# cp -vR top* ../sim_results/${day}/
# cp -vR line* ../sim_results/${day}/
# cp -vR corr* ../sim_results/${day}/
# cp -vR accth* ../sim_results/${day}/

#copy to local 
# cp -vR results_10M_* ../local_data/${day}/
# cp -vR Wr_ratio_* ../local_data/${day}/
# cp -vR top* ../local_data/${day}/
# cp -vR line* ../local_data/${day}/
# cp -vR corr* ../local_data/${day}/
# cp -vR accth* ../local_data/${day}/

#delete trace file and results
rm -rf dpc3_traces
rm -rf results_10M_* 
rm -rf Wr_ratio_* 
rm -rf top* 
rm -rf line* 
rm -rf corr* 
rm -rf accth* 

# rm *.txt