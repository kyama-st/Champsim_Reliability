#!/bin/bash

## Compile
echo "Compile"
./config.sh
make

##dpc3_tracesを取得していない時にダウンロードする
if [ -d dpc3_traces ]; then
    echo "dpc3_trace directory found"
else
    echo "trace directory not found"
    ./download_traces.sh
fi

## Run simulation
echo "Run Simulation"
if [ -d results ]; then 
    echo "results directory found"
else 
    echo "make results directory"
    mkdir results
fi

bin/champsim --warmup_instructions 200000000 --simulation_instructions 500000000 ./dpc3_traces/600.perlbench_s-210B.champsimtrace.xz > results/600.perlbench.txt
