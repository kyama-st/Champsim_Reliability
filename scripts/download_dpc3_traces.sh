#!/bin/bash

mkdir -p $PWD/../dpc3_traces
# while read LINE
# do
#     wget -P $PWD/../dpc3_traces -c http://hpca23.cse.tamu.edu/champsim-traces/speccpu/$LINE
# done < dpc3_max_simpoint.txt

wget -P $PWD/../dpc3_traces -c http://hpca23.cse.tamu.edu/champsim-traces/speccpu/400.perlbench-41B.champsimtrace.xz
