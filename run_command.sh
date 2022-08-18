#!/bin/bash

echo "Build" 
./build_champsim.sh bimodal no no no no lru 1

echo "Run"
ls -1 dpc3_traces | xargs -I{} sh -c 'echo {} && ./run_champsim.sh bimodal-no-no-no-no-lru-1core 1 10 {}'
# ./run_champsim.sh bimodal-no-no-no-no-lru-1core 1 10 600.perlbench_s-210B.champsimtrace.xz

# echo "Extract results"
# cat results_10M/*.txt | awk "NR==1,NR==100 {print}" > result_10M.txt
# echo "Convert to CSV"
# cat result_10M/*.txt | awk "NR==16, "