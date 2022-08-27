from ast import If
from operator import index
from tkinter import W
from numpy import float32, sort
import pandas as pd
import json
import pprint
import numpy as np
import matplotlib.pyplot as plt
import re

def Cal_AVF(addr_arr, df_json, all_cycle):
    df_AVF = pd.DataFrame(dtype=float32,index=addr_arr.tolist(), columns=["AVF"])
    for addr in addr_arr:
        log_address = df_json.query('Address == @addr')  
        #ACEの計算
        log_address.loc[log_address["R/W"]=="Read", "ACE"]=log_address["Cycle"].diff(1).fillna(log_address["Cycle"]) 
        log_address.loc[log_address["R/W"]=="Write", "ACE"]=0

        df_AVF.loc[addr, 'AVF']=log_address["ACE"].sum()/all_cycle

        # print("df_AVF: " + str(addr))
        # print(df_AVF["AVF"])

        # if addr ==1964810345014:
            # break

    return df_AVF["AVF"].fillna(0) 

def plot_graph(df_result, benchmark):
    #graphのplot
    x = df_result.index.tolist()
    y = df_result['Address'].tolist()

    fig = plt.figure()

    ax = fig.add_subplot(1,1,1)

    ax.scatter(x,y)
    title = re.sub('.{56}$', '', benchmark[16:])
    ax.set_title(title)
    ax.set_xlabel('address')
    ax.set_ylabel('AVF')

    directory = "results_10M_AVF_Fig/" 

    fig.savefig(directory+title+".png")

def save_results(df_result, benchmark):
    directory = "results_10M_AVF_CSV/"
    title = re.sub('.{56}$', '', benchmark[16:])
    df_result.to_csv(directory+title+".csv", sep='\t')

def benchmark_AVF(benchmark):
    print(benchmark)
    df_json = pd.read_json(benchmark)
    cycle_file = re.sub('.{56}$', '', benchmark) + ".txt"
    with open(cycle_file) as f:
        all_cycle = int(f.read().strip())
    print(all_cycle)

    # #addressだけのリスト -> アドレスごとにAVFを計算した行を追加する
    address_arr = pd.DataFrame(df_json['Address'].unique().tolist(), index=range(len(df_json['Address'].unique().tolist())), columns=['Address'])

    # address_arr["AVF"] = address_arr.apply(Cal_AVF, args=(df_json,))
    result_arr = address_arr.apply(Cal_AVF, args=(df_json,all_cycle))

    print("AVF計算後")
    print(result_arr)

    #csv保存
    save_results(result_arr, benchmark)

    #グラフ表示
    plot_graph(result_arr, benchmark)


def main():    
    # get json filename list
    # directory = "results_10M_CSV/"
    results_list_path = "json_list.txt"
    results_cycle_path = "allcycle_list.txt"
    with open(results_list_path) as f:
        json_list = [l.strip() for l in f.readlines()]

    # 全てのベンチマークについてAVF計算する。
    for filename in json_list:
        #シミュレーション結果のテキストファイルのパスを引数に入れる。
        benchmark_AVF(filename)
    
main()
