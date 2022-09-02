from ast import If
from cProfile import label
from email.headerregistry import Address
from fileinput import filename
from operator import index
from turtle import width
from unittest import result
from numpy import float32, sort
import pandas as pd
import json
import pprint
import numpy as np
import matplotlib.pyplot as plt
import re
import time
import os

#一つのアドレスについてAVFを計算する
def Cal_AVF(addr_arr, df_json, all_cycle):
    df_AVF = pd.DataFrame(dtype=float32,index=addr_arr.tolist(), columns=['AVF'] )
    i = 0
    with open("output_python_log.csv", mode="w") as f:
        f.write("in Cal_AVF\n")

    for addr in addr_arr:
        log_address = df_json.query('Address == @addr')  
        #ACEの計算
        log_address.loc[log_address["R/W"]=="Read", "ACE"]=log_address["Cycle"].diff(1).fillna(log_address["Cycle"]) 
        log_address.loc[log_address["R/W"]=="Write", "ACE"]=0

        df_AVF.loc[addr, 'AVF']=log_address["ACE"].sum()/all_cycle
        # ACE確認用
        # log_address.to_csv("output_python_log.csv", mode='a', sep='\t')
        # # i += 1
        # # if(i >100):
        #     break
    return df_AVF["AVF"].fillna(0) 

#グラフのプロット
def plot_graph(df_result, benchmark, directory, page):
    #graphのplot
    x = df_result.index.tolist()
    y = df_result['line_AVF'].tolist()

    fig = plt.figure()

    ax = fig.add_subplot(1,1,1)
    gr = 'page_AVF_' if page == 1 else 'line_AVF_'
    ax.scatter(x,y)
    ## graph_test関数から
    # title = gr +benchmark 
    ## benchmark_AVF関数から
    title = gr + re.sub('.{56}$', '', benchmark[16:])
    ax.set_title(title)
    ax.set_xlabel('address')
    ax.set_ylabel('AVF')
    print("graph title: "+ title)
    makedir(directory)
    fig.savefig(directory+title+".png")

#結果をCSVで格納
def save_results(df_result, benchmark, directory, page):
    gr = 'page_AVF_' if page == 1 else 'line_AVF_'

    title = gr + re.sub('.{56}$', '', benchmark[16:])
    makedir(directory)
    df_result.to_csv(directory+title+".csv", sep='\t')

#一つのベンチマークについてAVFを計算する。
def benchmark_AVF(benchmark):
    print("対象のベンチマーク: ", end="")
    print(benchmark)
    #ベンチマークごとに処理時間がどれくらいかかるか記録する用
    start_time = time.time() 

    df_json = pd.read_json(benchmark)
    cycle_file = re.sub('.{56}$', '', benchmark) + ".txt"
    with open(cycle_file) as f:
        all_cycle = int(f.read().strip())
    # print(all_cycle)

    ############### line粒度のAVF ###################
    # #addressだけのリスト -> アドレスごとにAVFを計算した行を追加する
    address_arr = pd.DataFrame(df_json['Address'].unique().tolist(), index=range(len(df_json['Address'].unique().tolist())), columns=['Address'])
    df_buffer_line_AVF = address_arr.apply(Cal_AVF, args=(df_json,all_cycle))
    df_line_AVF = df_buffer_line_AVF.rename(columns={'Address': 'line_AVF'},)
    print(type(df_line_AVF))
    with open("output_python_log.csv", mode="a") as f:
        f.write("\n in benchmark_AVF \n")
    print(address_arr)
    for addr in address_arr['Address']: 
        buffer=df_json.query("Address==@addr")['Page'].unique()
        df_line_AVF.loc[addr, 'page']=int(buffer[0])
    df_line_AVF.to_csv("output_python_log.csv", mode='a', sep='\t')
    
    result_line_dir = re.sub('CSV/.*$', 'AVF_LINE/', benchmark)
    # #### CSV保存 ####
    save_results(df_line_AVF, benchmark, result_line_dir, 0)
    # #### グラフ作成と保存 #####
    plot_graph(df_line_AVF, benchmark, result_line_dir, 0)
    
    ############### page粒度のAVF #################
    print(df_line_AVF.groupby('page').mean())
    df_page_AVF = df_line_AVF.groupby('page').mean()
    #csv保存
    result_page_dir = re.sub('CSV/.*$', 'AVF_PAGE/', benchmark)
    save_results(df_page_AVF, benchmark, result_page_dir, 1)
    #グラフ表示
    plot_graph(df_page_AVF, benchmark, result_page_dir, 1)

    #終了時刻
    end_time = time.time()
    #経過時間の表示
    elapsed_time(start_time, end_time)

#ディレクトリの存在確認と作成
def makedir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

#経過時間
def elapsed_time(start_time, end_time):
    periods_sec= end_time - start_time
    print("秒単位の経過時間：　", end="")
    print(str(periods_sec)+"sec", end="\n")
    if 1 <= (periods_sec/60) < 60:
        print_periods = '{:.2f}'.format(periods_sec/60)+"min"
    elif (periods_sec/60) >= 60:
        hours=int(periods_sec/3600)
        mins=int((periods_sec-(3600*hours))/60)
        print_periods =  '{hour}h{min}min'.format(hour=hours, min=mins)
    else:
        print_periods = '{:.2f}'.format(periods_sec)+"sec"

    print("AVF算出に掛かった時間: ", end="")
    print(print_periods)

def AVF_all_ave(json_list):
    result_line_dir = "results_10M_AVF_LINE/"
    result_page_dir = "results_10M_AVF_PAGE/"

    AVF_csv_list = [re.sub('^results_10M_CSV/','',re.sub('.{56}$', '.csv', l)) for l in json_list]

    df_all_ave = pd.DataFrame(columns=['line_AVF_mean', 'page_AVF_mean'])

    # calculate AVF average of one benchmark
    for filename in AVF_csv_list:
        benchmark = re.sub('^\d{3}.','', re.sub('_.*$', '', filename))
        ### line粒度のAVFの平均値　###
        with open(result_line_dir+filename) as f:
            df_AVF = pd.read_csv(f, sep='\t')
            df_all_ave.loc[benchmark, 'line_AVF_mean'] = df_AVF["line_AVF"].mean()
        ### page粒度のAVFの平均値　###
        with open(result_page_dir+filename) as f:
            df_AVF = pd.read_csv(f, sep='\t')
            df_all_ave.loc[benchmark, 'page_AVF_mean'] = df_AVF["line_AVF"].mean()
        print(df_all_ave)
    df_all_ave.loc['gmean', 'line_AVF_mean'] = df_all_ave['line_AVF_mean'].mean()
    df_all_ave.loc['gmean', 'page_AVF_mean'] = df_all_ave['page_AVF_mean'].mean()

    print("Average AVF of all benchmark")
    print(df_all_ave)
    # csvファイルに保存するコマンド
    directory = 'results_10M_AVF_allbenchmark/'
    makedir(directory)
    df_all_ave.to_csv(directory+"page_line_AVF_allbenchmark.csv", sep='\t')


    ############# pageとline粒度のベンチマークごとのAVFグラフ　#############
    #graphのプロット
    x = df_all_ave.index.tolist()
    y1 = df_all_ave['line_AVF_mean'].tolist()
    y2 = df_all_ave['page_AVF_mean'].tolist()
    bar_width = 0.35
    fig = plt.figure(figsize=(9,6))
    plt.bar(x,y1,width=-bar_width, align='edge', label="line AVF")
    plt.bar(x, y2, width=bar_width, align='edge', label="page AVF" )
    plt.xticks(rotation=70) 
    plt.title("Line and Page AVF")
    fig.subplots_adjust(bottom=0.2)
    plt.ylabel("AVF")
    plt.ylim(0, 1)
    plt.legend()
    # plt.show()
    png_name = "line_page_AVF_allbenchmark.png"
    fig.savefig(directory+png_name)

def graph_test(json_list):
    result_line_dir = "results_10M_AVF_LINE/"
    result_page_dir = "results_10M_AVF_PAGE/"
    dir_graph_test = "graph_test/"
    makedir(dir_graph_test)
    AVF_csv_list = [re.sub('^results_10M_CSV/','',re.sub('.{56}$', '.csv', l)) for l in json_list]

    # calculate AVF average of one benchmark
    for filename in AVF_csv_list:
        benchmark =re.sub('_.*$', '', filename)
        ### line粒度のAVFの平均値　###
        with open(result_line_dir+filename) as f:
            df_line_AVF = pd.read_csv(f, sep='\t', index_col=0)
            df_line_AVF.to_csv("output_python_log.csv", mode='w', sep='\t')
            plot_graph(df_line_AVF, benchmark, dir_graph_test, 0)

        ### page粒度のAVFの平均値　###
        with open(result_page_dir+filename) as f:
            df_page_AVF = pd.read_csv(f, sep='\t', index_col=0)
            plot_graph(df_page_AVF, benchmark, dir_graph_test, 1)



def main():    
    # get json filename list
    # directory = "results_10M_CSV/"
    results_list_path = "json_list.txt"
    results_cycle_path = "allcycle_list.txt"
    with open(results_list_path) as f:
        json_list = [l.strip() for l in f.readlines()]

    # 全てのベンチマークについてAVF計算する。
    for filename in json_list:
        benchmark_AVF(filename)
    # benchmark_AVF(json_list[1])
    #ライン粒度でのAVFのベンチマークごとの平均算出
    AVF_all_ave(json_list)
    
    ## グラフ作成テスト（グラフのタイトル調整用なので今後消す）
    # graph_test(json_list)




main()
