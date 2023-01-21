#!/bin/bash

## Compile
echo "Compile"
./config.sh
make
echo ""

##dpc3_tracesを取得していない時にダウンロードする
if [ -d dpc3_traces ]; then
    echo "dpc3_trace directory found"
else
    echo "trace directory not found"
    ./download_trace.sh
fi

#### 命令数の入力
### warmup_instruction
warmup_instruction=10000000
### simulation 命令数を1M単位で割った値で入力する
divided_byM_inst=500
M=1000000
simulation_instruction=$((divided_byM_inst*M))

#### 結果格納ファイルの場所
root='../csv_keep/sim_results/'
day=`date '+%F'`
path_to_results=${root}${day}'/champsim/'${divided_byM_inst}'M' 
echo $path_to_results
mkdir -p $path_to_results

### json(メモリトレース）のディレクトリ作成
path_to_json=${path_to_results}'_JSON'
mkdir -p $path_to_json 

#ベンチマークリスト取得
trace_list=(`ls -1 dpc3_traces`) 
i=0

## シミュレーション実行からjsonの抽出まで
for trace in "${trace_list[@]}" 
do 
    if [ $i -ge 0 ]; then
        echo $trace
        sim_result=`echo $trace|sed -e "s/_s.*//g"`
        bin/champsim --warmup_instructions $warmup_instruction --simulation_instructions $simulation_instruction ./dpc3_traces/$trace > $path_to_results/$sim_result.txt

        line_num_end=`cat $path_to_results/$sim_result.txt | awk 'END{print NR}'`
        line_num_json=$((line_num_end-37))

        # extract siumulation result to make json file (log write and read instruction)
        cat $path_to_results/$sim_result.txt |awk "NR==18, NR==$line_num_json {print}"|sed -e "1 s/^{/[\{/g "|sed -e "$ s/\},$/\}]/g" >$path_to_json/"${sim_result}".json
        
        ## get cycle counts
        warmup_cycle=`cat $path_to_results/$sim_result.txt | awk "NR==$line_num_end {print}" | awk '{print $NF}'`
        finish_cycle=`cat $path_to_results/$sim_result.txt | awk "NR==$((line_num_end-1)) {print}" | awk '{print $NF}'`
        all_cycle=$(($warmup_cycle+$finish_cycle))

        echo $all_cycle > $path_to_json/"${sim_result}".txt
        vpage_size=`cat $path_to_results/$sim_result.txt | awk "NR==$((line_num_end-2)) {print}" | awk '{print $NF}'`
        echo $vpage_size > $path_to_json/"${sim_result}"'_memory_footprint'.txt

    fi 
    ## コード試験用。指定したベンチマークのみ実行する
    i=$((++i))
    # if [ $i -gt 2 ] ; then 
        # break
    # fi 
done

