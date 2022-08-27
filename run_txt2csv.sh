#!/bin/bash

echo "Extract results"
mkdir results_10M_CSV
# ls -1 results_10M | head -n 1 | xargs -I{} sh -c 'cat results_10M/{} | awk "NR==16, {print}" > results_10M_CSV/{}.json'

resultsArr=(`ls -1 results_10M`)
for fName in "${resultsArr[@]}" 
do 
    echo $fName
    END_num=`cat results_10M/$fName | awk 'END{print NR}'`-58
    finish_num=$((END_num+2))
    echo $finish_num
    # make json file (log write and read instruction)
    cat results_10M/$fName |awk "NR==16, NR==$END_num {print}"|sed -e "1 s/^{/[\{/g "|sed -e "$ s/\},$/\}]/g" >results_10M_CSV/$fName.json
    #
    name=`echo $fName|sed -e "s/\.champsim.*txt$//g"`

    
    warmup_cycle=`cat results_10M/$fName | awk "NR==14 {print}" | awk '{print $(NF-8)}'`
    finish_cycle=`cat results_10M/$fName | awk "NR==$finish_num {print}" | awk '{print $(NF-11)}'`
    all_cycle=$((warmup_cycle+$finish_cycle))
    # echo `cat results_10M/$fName | awk "NR==$finish_num {print}"` 
    # echo `cat results_10M/$fName | awk "NR==14 {print}"`
    echo $name
    echo $all_cycle > results_10M_CSV/"${name}".txt
done

echo "Make json filename list in json_list.txt"
ls -1 results_10M_CSV/*.json > json_list.txt

