#!/bin/bash

## Delete trace file
echo "Delete trace file"
rm -rf dpc3_traces
echo " "

echo "zip results file "
day=`date '+%F'`
mkdir ../csv_keep/sim_results/${day}/
list=(`ls -d -1 results*`)

# for dir in "${list[@]}"
# do 
#     echo $dir
#     zip ../csv_keep/sim_results/${day}/$dir.zip $dir/*
    
# done


# zip ../csv_keep/sim_results/${day}/page_AVF_std.zip pages_AVF_std/*
# zip ../csv_keep/sim_results/${day}/Wr_ratio_AVF.zip Wr_ratio_AVF/*

# touch ../csv_keep/sim_results/${day}/README.md 

echo "delete results"