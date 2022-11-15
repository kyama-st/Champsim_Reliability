from cProfile import label
import csv
import imp
from importlib.util import module_from_spec
from lib2to3.pgen2.grammar import opmap_raw
from posixpath import sep
from traceback import print_tb
from turtle import color, width
from numpy import NaN, average, float32, sort
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import time
import makedir
import os
import elapsed_time
import Calculate_AVF_WrRd as Calc
import page_AVF_WrRd as page_AVF
import all_benchmarks_AVF_variation as all_AVF
import pdb 
import AVF_wr_ratio_corr as corr
##### global variable ######
dir_page_AVF_std = 'pages_AVF_std/'

dir_page_AVF_std_accth = 'accth_10_AVF_2/'
dir_WrRatio = 'Wr_ratio_AVF/'
dir_corr = dir_WrRatio+'correlation/'
dir_page_WrRatio ='Wr_ratio_page_corr_2/'
dir_json = '../results_100M_JSON/'
dir_line_AVF = re.sub('JSON', 'LINE_AVF', dir_json)

list_benchmark = ["600.perlbench",
"602.gcc",
"603.bwaves",
"605.mcf",
"607.cactuBSSN",
"619.lbm",
"620.omnetpp",
"621.wrf",
"623.xalancbmk",
"625.x264",
"627.cam4",
"628.pop2",
"631.deepsjeng",
"638.imagick",
"641.leela",
"644.nab",
"648.exchange2",
"649.fotonik3d",
"654.roms",
"657.xz"]

csv_output_confirm = 'python_output.csv'

#グラフのプロット
def plot_graph(df_result, benchmark, directory, page):
    #graphのplot
    x = df_result.index.tolist()
    y = df_result['line_AVF'].tolist()
    
    fig = plt.figure()

    ax = fig.add_subplot(1,1,1)
    gr = '_page_AVF_' if page == 1 else '_line_AVF_'
    ax.scatter(x,y)
    ## graph_test関数から
    # title = gr +benchmark 
    ## benchmark_AVF関数から
    # benchmark = gr + re.sub('.{56}$', '', benchmark[16:])
    ax.set_title(benchmark+gr)
    ax.set_xlabel('address')
    ax.set_ylabel('AVF')
    ax.set_ylim(0,1)
    print("graph benchmark: "+ benchmark)
    makedir.func(directory)
    fig.savefig(directory+benchmark+gr+".png")

#結果をCSVで格納-------------
def save_results(df_result, benchmark, directory, page):
    gr = '_page_AVF_' if page == 1 else '_line_AVF_'

    makedir(directory)
    df_result.to_csv(directory+benchmark+gr+".csv", sep='\t')
#--------------------------

#1つのベンチマークについてAVFとwr-ratioの相関係数を算出する
def benchmark_AVF_Wr_ratio(benchmark):
    print("対象のベンチマーク: ", end="")
    print(benchmark)

    if os.path.exists(dir_WrRatio+benchmark+'line_WrRatio_.csv') :
        df_line_AVF_WrRatio = pd.read_csv(dir_WrRatio+benchmark+'line_WrRatio_.csv', sep='\t', index_col=0)

    else:
        df_json = pd.read_json(dir_json+benchmark+'.json')
        cycle_file = dir_json+benchmark+'.txt' 
        with open(cycle_file) as f:
            all_cycle = int(f.read().strip())
        
        ############### line粒度のAVFとWrratioの算出 ###################
        address_arr = df_json['Address'].unique().tolist()
        df_line_AVF_WrRatio = calculate_WrRd_AVF(address_arr, df_json, all_cycle)
        df_line_AVF_WrRatio.to_csv(dir_WrRatio+benchmark+'line_WrRatio_'+".csv", mode='w', sep='\t')
        # df_line_AVF_WrRatio.to_csv("log_wr-ratio-2.csv", mode='a', sep='\t')
        ######################################

    ######### line粒度のAVFと相関係数 #######
    series_x = df_line_AVF_WrRatio['AVF']
    series_y = df_line_AVF_WrRatio['wr_ratio']
    fig, ax = plt.subplots() 
    ax.scatter(series_x, series_y)
    ax.set_title('line granurality '+ benchmark)
    ax.set_xlabel('AVF')
    ax.set_ylabel('Wr Ratio')
    # ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    # plt.show()
    makedir.func(dir_corr)
    print(df_line_AVF_WrRatio.corr())
    df_line_corr = df_line_AVF_WrRatio.corr()

    ####### page粒度のAVFと相関係数 ############
    mean_grouped_by_page =df_line_AVF_WrRatio.groupby('page').mean()
    sum_grouped_by_page =df_line_AVF_WrRatio.groupby('page').sum()
    df_page_AVF_WrRatio = sum_grouped_by_page.copy()
    df_page_AVF_WrRatio['mean_AVF']=mean_grouped_by_page['AVF']
    df_page_AVF_WrRatio['page_wr_ratio']=df_page_AVF_WrRatio['wr']/df_page_AVF_WrRatio['rd'].fillna(0)
    df_page_corr = df_page_AVF_WrRatio.corr()

    series_x = df_page_AVF_WrRatio['mean_AVF']
    series_y = df_page_AVF_WrRatio['page_wr_ratio']
    fig2, ax2 = plt.subplots() 
    ax2.scatter(series_x, series_y)
    ax2.set_title('page granurality ' + benchmark)
    ax2.set_xlabel('AVF')
    ax2.set_ylabel('Wr Ratio')
    # ax2.set_ylim(0, 1)
    ax2.set_xlim(0, 1)
    # plt.show()
    ###### save data list
    
    #### save png file : line粒度のAVFとWrratioの相関係数のグラフ
    fig.savefig(dir_corr+"line_corr_"+benchmark+".png")
    #### save csv file : line粒度のAVFとWr-ratioの相関係数
    df_line_corr.fillna('-', inplace=True)
    df_line_corr.to_csv(dir_corr+'line_corr_'+benchmark+".csv", mode='w', sep='\t')
    ##### save file 4: page粒度のAVFとWr-ratio
    df_page_AVF_WrRatio.to_csv(dir_WrRatio+benchmark+"page_WrRatio.csv",sep='\t', mode='w')
    #### save file 5 : page粒度のAVFとWr-ratioの相関係数のグラフ
    df_page_corr.fillna('-', inplace=True)
    df_page_corr.to_csv(dir_corr+'page_corr_'+benchmark+".csv", mode='w', sep='\t')
    #### save file 6: page粒度のAVFとWr-ratioの相関係数のグラフ
    fig2.savefig(dir_corr+"page_corr_"+benchmark+".png")

    return df_line_corr, df_page_corr


def AVF_all_ave(json_list):
    result_line_dir = "results_10M_AVF_LINE/"
    result_page_dir = "results_10M_AVF_PAGE/"

    AVF_csv_list = [re.sub('^results_10M_CSV/','',re.sub('.{56}$', '.csv', l)) for l in json_list]

    df_all_ave = pd.DataFrame(columns=['line_AVF_mean', 'page_AVF_mean'])

    # calculate AVF average of one benchmark
    for filename in AVF_csv_list:
        benchmark = re.sub('^\d{3}.','', re.sub('_.*$', '', filename))
        ### line粒度のAVFの平均値　###
        with open(result_line_dir+"line_AVF_"+filename) as f:
            df_AVF = pd.read_csv(f, sep='\t')
            df_all_ave.loc[benchmark, 'line_AVF_mean'] = df_AVF["line_AVF"].mean()
        ### page粒度のAVFの平均値　###
        with open(result_page_dir+"page_AVF_"+filename) as f:
            df_AVF = pd.read_csv(f, sep='\t')
            df_all_ave.loc[benchmark, 'page_AVF_mean'] = df_AVF["line_AVF"].mean()
        print(df_all_ave)
    df_all_ave.loc['gmean', 'line_AVF_mean'] = df_all_ave['line_AVF_mean'].mean()
    df_all_ave.loc['gmean', 'page_AVF_mean'] = df_all_ave['page_AVF_mean'].mean()

    print("Average AVF of all benchmark")
    print(df_all_ave)
    # csvファイルに保存するコマンド
    directory = 'results_10M_AVF_allbenchmark/'
    makedir.func(directory)
    df_all_ave.to_csv(directory+"line_page_AVF_allbenchmark.csv", sep='\t')


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

def all_benchmark_AVF_WrRatio_corr():
    df_all_benchmark_page_coor = pd.DataFrame(columns=['corr'])
    df_all_benchmark_line_corr = pd.DataFrame(columns=['corr'])

    log_file = 'log_wr-ratio_3.csv'
    with open(log_file, mode='w') as f:
            f.write("\nAVF_WrRatio_from_file\n")
    for benchmark in list_benchmark:
        #### ベンチマークごとに相関係数をcsvに保存していた場合。
        if os.path.exists(dir_corr+"line_corr_"+benchmark+'.csv'): 
            df_benchmark_line_corr = pd.read_csv(dir_corr+"line_corr_"+benchmark+'.csv', sep='\t', index_col=0)  
            df_benchmark_page_corr = pd.read_csv(dir_corr+"page_corr_"+benchmark+'.csv', sep='\t', index_col=0)  

            df_all_benchmark_page_coor.loc[ind, 'corr'] = df_benchmark_page_corr.loc['mean_AVF', 'page_wr_ratio']
            df_all_benchmark_line_corr.loc[ind, 'corr'] = df_benchmark_line_corr.loc['AVF', 'wr_ratio']
        else: 
            print()
        ### page粒度のWrRatio オープン 
        filename = 'page_WrRatio_'+benchmark+'.csv'
        # filename = 'page_WrRatio_619.lbm_s-4268B.csv'
        df_page_WrRatio = pd.read_csv(dir_WrRatio+filename, sep='\t', index_col=0)

        with open(log_file, mode='a') as f:
            f.write("\n")
            f.write(benchmark)
            f.write("\n")
        df_page_WrRatio.corr().to_csv(log_file, mode='a', sep='\t')

        #### page単位での相関係数のグラフ
        series_x = df_page_WrRatio['mean_AVF']
        series_y = df_page_WrRatio['page_wr_ratio']
        fig2, ax2 = plt.subplots() 
        ax2.scatter(series_x, series_y)
        print("title: "+benchmark)
        ax2.set_title('page granurality' + benchmark)
        ax2.set_xlabel('AVF')
        ax2.set_ylabel('Wr Ratio')
        # ax2.set_ylim(0, 1)
        ax2.set_xlim(0, 1)
        # plt.show()
        fig2.savefig(dir_page_WrRatio+"page_WrRatio_"+benchmark+".png")
        
        #### line粒度のWrRatioのファイル #######

        line_filename = 'line_WrRatio_'+benchmark+'.csv'
        # line_filename = 'line_WrRatio_619.lbm_s-4268B.csv'
        df_line_WrRatio = pd.read_csv(dir_WrRatio+line_filename, sep='\t', index_col=0)
        # print("line granurarity")
        # print(df_line_WrRatio.corr())
        df_line_WrRatio.corr().to_csv(log_file, mode='a', sep='\t')
        # print(df_line_WrRatio.corr().loc['AVF', 'wr_ratio'])

        ####benchmark毎に
        ind = re.sub( '_.*$','', re.sub('^\d{3}.', '', benchmark)) 

        df_all_benchmark_page_coor.loc[ind, 'corr'] = df_page_WrRatio.corr().loc['mean_AVF', 'page_wr_ratio']
        df_all_benchmark_line_corr.loc[ind, 'corr'] = df_line_WrRatio.corr().loc['AVF', 'wr_ratio']
    
    df_all_benchmark_page_coor.fillna('-', inplace=True)
    df_all_benchmark_line_corr.fillna('-', inplace=True)
    df_all_benchmark_page_coor.to_csv(dir_page_WrRatio+"all_page_AVF_"+benchmark+".csv", sep='\t')

    df_all_benchmark_line_corr.to_csv(dir_page_WrRatio+"all_line_AVF_"+benchmark+".csv", sep='\t')

    series_x = df_all_benchmark_page_coor[df_all_benchmark_page_coor['corr']!= '-' ].index.tolist()
    series_y = df_all_benchmark_page_coor[df_all_benchmark_page_coor['corr']!= '-' ]

    plt.rcParams["font.size"] = 15
    fig3, ax3 = plt.subplots() 
    # ax3.rcParams['font.size'] = 16
    fig3.set_figheight(8)
    fig3.set_figwidth(9)
    ax3.scatter(series_x, series_y)
    ax3.set_title('page AVF Wr-ratio correlated coefficient')
    ax3.set_xlabel('benchmark')
    ax3.set_ylabel('Correlated Coefficient')

    plt.xticks(rotation=70)
    # plt.yticks(rotation=90)
    plt.tight_layout()

    # ax2.set_ylim(0, 1)
    fig3.subplots_adjust(bottom=0.34, top=0.8, left=0.16)

    plt.show()
    fig3.savefig(dir_page_WrRatio+"all_page_corr.png")

    fig4, ax4 = plt.subplots() 
    fig4.set_figheight(6)
    fig4.set_figwidth(9)
    series_x = df_all_benchmark_line_corr[df_all_benchmark_line_corr['corr']!= '-' ].index.tolist()
    series_y = df_all_benchmark_line_corr[df_all_benchmark_line_corr['corr']!= '-' ]
    # fig3, ax3 = plt.subplots() 
    ax4.scatter(series_x, series_y)
    ax4.set_title('line granurarity AVF Wr-ratio correlated coefficient')
    ax4.set_xlabel('benchmark')
    ax4.set_ylabel('Correlated Coefficient')

    plt.xticks(rotation=70)
    # ax2.set_ylim(0, 1)

    fig4.subplots_adjust(bottom=0.3)
    plt.show()

    fig4.savefig(dir_page_WrRatio+"all_line_corr.png")


########### main 関数 ####### 
if __name__ == '__main__': 
    # makedir.func(dir_WrRatio)
    # makedir(dir_corr)
    # makedir(dir_page_WrRatio)
    pdb.set_trace()
    for benchmark in list_benchmark:
        if benchmark == "620.omnetpp":
            page_AVF.func(benchmark, dir_line_AVF)

    pdb.set_trace()
    corr.func(list_benchmark[1], dir_line_AVF)    

    # 全てのベンチマークについてlineAVF計算してcsvに保存。
    pdb.set_trace() 
    print("命令数："+dir_json)
    for benchmark in list_benchmark:
        if benchmark != "619.lbm":
            Calc.func(benchmark, dir_json)

    pdb.set_trace()
    #### AVFのばらつき
    all_AVF.AVF_variation_graph(list_benchmark, dir_line_AVF) 

    ## 全てのベンチマークでページ内の標準偏差を出す
    ## ベンチマークごとにAVFとwr-ratioの算出
    # for benchmark in list_benchmark:
        # benchmark_AVF_Wr_ratio(benchmark)
    # benchmark_AVF_Wr_ratio(list_benchmark[0])
    # #ライン粒度でのAVFのベンチマークごとの平均算出
    # AVF_all_ave(json_list)
    
    ## グラフ作成テスト（グラフのタイトル調整用なので今後消す）
    # graph_test(json_list)

