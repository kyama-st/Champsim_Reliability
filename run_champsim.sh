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


warmup_instruction=10000000
### simulation 命令数をMで割った値で入力する
divided_byM_inst=500
M=1000000
simulation_instruction=$((divided_byM_inst*M))
results_dir="results_${divided_byM_inst}M"
echo $results_dir
mkdir $results_dir

### json用のディレクトリ作成
json_dir="${results_dir}_JSON"
mkdir $json_dir 

#ベンチマークリスト取得
trace_list=(`ls -1 dpc3_traces`) 
i=0

## シミュレーション実行からjsonの抽出まで
for trace in "${trace_list[@]}" 
do 
    # echo $trace
    echo $i 
    if [ $i -eq 19 ]; then
        echo $trace
        sim_result=`echo $trace|sed -e "s/_s.*//g"`
        bin/champsim --warmup_instructions $warmup_instruction --simulation_instructions $simulation_instruction ./dpc3_traces/$trace > $results_dir/$sim_result.txt

        line_num_end=`cat $results_dir/$sim_result.txt | awk 'END{print NR}'`
        line_num_json=$((line_num_end-34))

        # extract siumulation result to make json file (log write and read instruction)
        cat $results_dir/$sim_result.txt |awk "NR==18, NR==$line_num_json {print}"|sed -e "1 s/^{/[\{/g "|sed -e "$ s/\},$/\}]/g" >$json_dir/"${sim_result}".json
        
        ## get cycle counts
        warmup_cycle=`cat $results_dir/$sim_result.txt | awk "NR==$line_num_end {print}" | awk '{print $NF}'`
        finish_cycle=`cat $results_dir/$sim_result.txt | awk "NR==$((line_num_end-1)) {print}" | awk '{print $NF}'`
        all_cycle=$(($warmup_cycle+$finish_cycle))

        echo $all_cycle > $json_dir/"${sim_result}".txt

    fi 
    ## コード試験用。指定したベンチマークのみ実行する
    i=$((++i))
    # if [ $i -gt 1 ] ; then 
    #     break
    # fi 
done

