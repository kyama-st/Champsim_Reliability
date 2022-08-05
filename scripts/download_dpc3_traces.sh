#!/bin/bash

mkdir -p $PWD/../dpc3_traces
# while read LINE
# do
#     wget -P $PWD/../dpc3_traces -c http://hpca23.cse.tamu.edu/champsim-traces/speccpu/$LINE
# done < dpc3_max_simpoint.txt

wget -P $PWD/../dpc3_traces -c http://hpca23.cse.tamu.edu/champsim-traces/speccpu/600.perlbench_s-210B.champsimtrace.xz

