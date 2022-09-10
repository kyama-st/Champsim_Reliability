from cProfile import label
from importlib.util import module_from_spec
from lib2to3.pgen2.grammar import opmap_raw
from traceback import print_tb
from turtle import color, width
from numpy import NaN, average, float32, sort
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import time
import os

##### global variable ######
dir_page_AVF_std = 'top50pages_AVF/'

dir_page_AVF_std_accth = 'accth_10_AVF_2/'
dir_corr = 'corr_coeff/'
dir_WrRatio = 'Wr_ratio_AVF/'
dir_page_WrRatio ='Wr_ratio_page_corr_2/'
dir_sim_results = 'results_10M_CSV/'

list_benchmark = ["600.perlbench_s-210B",
"602.gcc_s-734B",
"603.bwaves_s-3699B",
"605.mcf_s-665B",
"607.cactuBSSN_s-2421B",
"619.lbm_s-4268B",
"620.omnetpp_s-874B",
"621.wrf_s-575B",
"623.xalancbmk_s-700B",
"625.x264_s-18B",
"627.cam4_s-573B",
"628.pop2_s-17B",
"631.deepsjeng_s-928B",
"638.imagick_s-10316B",
"641.leela_s-800B",
"644.nab_s-5853B",
"648.exchange2_s-1699B",
"649.fotonik3d_s-1176B",
"654.roms_s-842B",]
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

def calculate_WrRd_AVF(addr_arr, df_json, all_cycle):
    df_results = pd.DataFrame(index=addr_arr['Address'].tolist(), columns=['page', 'access#', 'AVF', 'wr_ratio', 'wr#', 'rd#'] )
    i = 0
    with open("log_wr-ratio-2.csv", mode="w") as f:
        f.write("in Calculate_WrRd\n")
    for addr in addr_arr['Address']:
        extract_at_addr = df_json.query('Address == @addr')  
        #ACEの計算
        extract_at_addr.loc[extract_at_addr["R/W"]=="Read", "ACE"]=extract_at_addr["Cycle"].diff(1).fillna(extract_at_addr["Cycle"]) 
        extract_at_addr.loc[extract_at_addr["R/W"]=="Write", "ACE"]=0

        # AVF計算
        df_results.loc[addr, 'AVF']=extract_at_addr["ACE"].sum()/all_cycle
        # ACE確認用
        # print(extract_at_addr)
        extract_at_addr.to_csv("log_wr-ratio-2.csv", mode='a', sep='\t')
        # i += 1
        # if(i >500):
        #     break

        # page
        df_results.loc[addr, 'page']=extract_at_addr.iat[0,3]

        # access counts
        access_counts = len(extract_at_addr)
        df_results.loc[addr, 'access#']= access_counts 

        # wr-ratio

        extract_at_addr_copy = extract_at_addr.rename(columns={'R/W':'R_W'})
        # print("change column name")
        # print(extract_at_addr_copy)
        # print(extract_at_addr_copy.query('R_W == "Read"'))
        num_rd = len(extract_at_addr_copy.query('R_W == "Read"')) 

        num_wr = len(extract_at_addr_copy.query('R_W == "Write"')) 
        # num_rd = len(extract_at_addr.query('"R\/W" == "Read"'))
        # num_wr = len(extract_at_addr.query('"R/W" == "Write"'))
        with open('log_wr-ratio-2.csv', mode='a') as f:

            f.write("wr "+ str(num_wr)+"rd "+ str(num_rd))
            f.write("\n---------------\n")

        # if num_rd == 0:
            # break
        df_results.loc[addr, 'wr#']=num_wr 
        df_results.loc[addr, 'rd#']=num_rd
        wr_ratio = num_wr/num_rd if num_rd != 0 else 1 
        df_results.loc[addr, 'wr_ratio']= wr_ratio 


    return df_results 

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


def benchmark_AVF_Wr_ratio(benchmark):
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

    address_arr = pd.DataFrame(df_json['Address'].unique().tolist(), index=range(len(df_json['Address'].unique().tolist())), columns=['Address'])
    ########## calcurate_wrrd_の確認用　 #######
    df_line_AVF_WrRatio = calculate_WrRd_AVF(address_arr, df_json, all_cycle)
    
    title = re.sub('^results_10M_CSV/', '', re.sub('.{56}$', '', benchmark))

    # df_line_AVF_WrRatio.to_csv("log_wr-ratio-2.csv", mode='a', sep='\t')
    print("end-df-calcurate-wr-ratio")
    ######################################

    ######### line粒度のAVFと相関係数 #######
    series_x = df_line_AVF_WrRatio['AVF']
    series_y = df_line_AVF_WrRatio['wr_ratio']
    fig, ax = plt.subplots() 
    ax.scatter(series_x, series_y)
    print("title: "+title)
    ax.set_title('line granurality'+ title)
    ax.set_xlabel('AVF')
    ax.set_ylabel('Wr Ratio')
    # ax.set_ylim(0, 1)
    ax.set_xlim(0, 1)
    # plt.show()
    makedir(dir_corr)
    print(df_line_AVF_WrRatio.corr())
    df_line_corr = df_line_AVF_WrRatio.corr()

    ####### page粒度のAVFと相関係数 ############
    mean_grouped_by_page =df_line_AVF_WrRatio.groupby('page').mean()
    sum_grouped_by_page =df_line_AVF_WrRatio.groupby('page').sum()
    df_page_AVF_WrRatio = sum_grouped_by_page.copy()
    df_page_AVF_WrRatio['mean_AVF']=mean_grouped_by_page['AVF']
    df_page_AVF_WrRatio['page_wr_ratio']=df_page_AVF_WrRatio['wr#']/df_page_AVF_WrRatio['rd#'].fillna(0)
    df_page_corr = df_page_AVF_WrRatio.corr()

    series_x = df_page_AVF_WrRatio['mean_AVF']
    series_y = df_page_AVF_WrRatio['page_wr_ratio']
    fig2, ax2 = plt.subplots() 
    ax2.scatter(series_x, series_y)
    print("title: "+title)
    ax2.set_title('page granurality' + title)
    ax2.set_xlabel('AVF')
    ax2.set_ylabel('Wr Ratio')
    # ax2.set_ylim(0, 1)
    ax2.set_xlim(0, 1)
    # plt.show()
    ###### save data list
    
    #### save file 1
    df_line_AVF_WrRatio.to_csv(dir_WrRatio+'line_WrRatio_'+title+".csv", mode='w', sep='\t')
    #### save file 2
    fig.savefig(dir_corr+"line_corr_"+title+".png")
    #### save file 3
    df_line_corr.to_csv(dir_corr+'line_corr_'+title+".csv", mode='w', sep='\t')
    ##### save file 4
    df_page_AVF_WrRatio.to_csv(dir_WrRatio+'page_WrRatio_'+title+".csv",sep='\t', mode='w')

    #### save file 5
    df_page_corr.to_csv(dir_corr+'page_corr_'+title+".csv", mode='w', sep='\t')
    #### save file 6
    fig2.savefig(dir_corr+"page_corr_"+title+".png")

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
    makedir(directory)
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

def AVF_WrRatio_from_file():

    df_page_AVF_corr = pd.DataFrame(columns=['corr'])
    df_line_AVF_corr = pd.DataFrame(columns=['corr'])

    log_file = 'log_wr-ratio_3.csv'
    with open(log_file, mode='w') as f:
            f.write("\nAVF_WrRatio_from_file\n")
    for benchmark in list_benchmark:
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

        df_page_AVF_corr.loc[ind, 'corr'] = df_page_WrRatio.corr().loc['mean_AVF', 'page_wr_ratio']
        df_line_AVF_corr.loc[ind, 'corr'] = df_line_WrRatio.corr().loc['AVF', 'wr_ratio']
    
    df_page_AVF_corr.fillna('-', inplace=True)
    df_line_AVF_corr.fillna('-', inplace=True)
    df_page_AVF_corr.to_csv(dir_page_WrRatio+"all_page_AVF_"+benchmark+".csv", sep='\t')

    df_line_AVF_corr.to_csv(dir_page_WrRatio+"all_line_AVF_"+benchmark+".csv", sep='\t')

    series_x = df_page_AVF_corr[df_page_AVF_corr['corr']!= '-' ].index.tolist()
    series_y = df_page_AVF_corr[df_page_AVF_corr['corr']!= '-' ]

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
    series_x = df_line_AVF_corr[df_line_AVF_corr['corr']!= '-' ].index.tolist()
    series_y = df_line_AVF_corr[df_line_AVF_corr['corr']!= '-' ]
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


def line_AVF_within_page_fromfile(benchmark):
    ##### top50pages_AVF/page_AVF_top25_page_AVF_620.omnetpp_s-874B.csv
    df_allbenchmark =pd.DataFrame(columns=['line_AVF_std_mean']) 
    file = dir_page_AVF_std+"page_AVF_top25_page_AVF_"+benchmark+".csv"
    print("open: "+ file)
    df_page_AVF_std = pd.read_csv(file, sep=',', index_col=0)
    access_th = 20    
    print(df_page_AVF_std)
    print(df_page_AVF_std.columns)
    print(df_page_AVF_std['access#'])
    df_extract_at_access = df_page_AVF_std[df_page_AVF_std['access#'] >= 10]
    print(df_extract_at_access)
    # df_extract_at_access = df_page_AVF_std.query('`access#` >= @access_th')
    print(df_extract_at_access.mean())
    std_mean = df_extract_at_access['line_AVF_std'].mean()
    return std_mean 

def line_AVF_within_page(filename):


    #### 
    dir = "results_10M_AVF_LINE/"
    # filename = "line_AVF_649.fotonik3d_s-1176B.csv"
    df_line_AVF = pd.read_csv(dir+filename, sep='\t')
    df_line_AVF.rename(columns={'Unnamed: 0':'Address'}, inplace=True)
    page_list = [float(str(l).strip()) for l in df_line_AVF['page'].unique().tolist()] 
    
    ##### pageごとにラインがいくつあるのか示す　#######
    with open("python_output.csv", mode='w') as f:
        f.write('value counts\n')
    df_line_AVF.value_counts('page').to_csv("python_output.csv", mode='a', sep='\t')
    
    df_page_AVF = pd.DataFrame(columns=['access#','line_AVF_average', 'line_AVF_std'], dtype=float32)
    dir = "line_AVF_within_page/"
    makedir(dir)
    for page in page_list:
        # print(df_line_AVF.value_counts('page').loc[page])
        df_extract_at_page = df_line_AVF.query('page == @page')
        AVF_average_within_page = df_extract_at_page['line_AVF'].mean()
        AVF_std_within_page = df_extract_at_page['line_AVF'].std() if len(df_extract_at_page)>1 else 0
        df_page_AVF.loc[page, 'access#']=len(df_extract_at_page)
        df_page_AVF.loc[page, 'line_AVF_average']=AVF_average_within_page
        df_page_AVF.loc[page, 'line_AVF_std']=AVF_std_within_page
        # if df_line_AVF.value_counts('page').loc[page] >= 10 :
        #     ##### グラフ作成 #####
        #     fig, ax = plt.subplots()  
        #     series_x = df_extract_at_addr['Address']
        #     series_y = df_extract_at_addr['line_AVF']
        #     list_AVF_average = [AVF_average_within_page] * len(series_x)
        #     ax.scatter(series_x,series_y, label='line AVF')
        #     ax.plot(series_x, list_AVF_average, color='orange', label='average line AVF')
        #     title = "600.perlbench_page#" + str(page) 
        #     ax.set_title(title)
        #     ax.set_xlabel('address')
        #     ax.set_ylabel('AVF')
        #     ax.set_ylim(0, 1)
        #     print("graph title:"+ title)
            
        #     ax.legend()
        #     # plt.show()
        #     fig.savefig(dir+title+".png")

        # else :
            # continue
 

    #### 平均値と標準偏差のグラフ ####
    df_page_AVF_sorted = df_page_AVF.sort_values('access#', ascending=False)
    df_page_AVF_sorted.to_csv("output_df_page_AVF.csv", sep='\t', mode='w')
    #アクセス回数上位25%のページについてグラフを作る
    
    top_25 = (len(df_page_AVF)//2)
    print("len: " + str(len(df_page_AVF)))
    print("top_25: "+ str(top_25))
    print(df_page_AVF_sorted.iloc[0:top_25])
    df_extract_at_page = df_page_AVF.query('30000639600<  index <34094640000')
    fig2, ax2 = plt.subplots() 
    
    temp_x = df_page_AVF_sorted.iloc[0:top_25].index.to_list()
    series_x = [l/(10**10) for l in temp_x]
    series_y = df_page_AVF_sorted.iloc[0:top_25]['line_AVF_average']
    series_y_std = df_page_AVF_sorted.iloc[0:top_25]['line_AVF_std']
    ax2.bar(series_x, series_y, yerr=series_y_std, ecolor='black', width=0.01 )

    # ax2.scatter(series_x, series_y )

    # ax2.errorbar(series_x, series_y, yerr=series_y_std, color='black')
    
    title = re.sub('.csv$', '', re.sub('^line_AVF', 'top25_page_AVF', filename))   
    ax2.set_title(title)
    ax2.set_xlabel('page')
    ax2.set_ylabel('AVF')
    ax2.set_ylim(0, 1)   
    # plt.show()
    makedir(dir_page_AVF_std)
    fig2.savefig(dir_page_AVF_std+title+".png")
    df_page_AVF.loc['gmean', 'line_AVF_average'] = df_page_AVF['line_AVF_average'].mean()
    df_page_AVF.loc['gmean', 'line_AVF_std'] = df_page_AVF['line_AVF_std'].mean()
    df_page_AVF.to_csv(dir_page_AVF_std+'page_AVF_'+title+'.csv')

    std_mean = df_page_AVF_sorted.iloc[0:top_25]['line_AVF_std'].mean()
    print("std_mean: ", end='')
    print(df_page_AVF_sorted.iloc[0:top_25]['line_AVF_std'].mean())
    print(type(df_page_AVF_sorted.iloc[0:top_25]['line_AVF_std'].mean()))
    ##### アクセス回数トップ25%の標準偏差の平均値を戻り値とする
    return std_mean 
    

def all_benchmark_AVF_std():
    with open('all_benchmark_AVF_std.txt') as f:
        csv_list = [l.strip() for l in f.readlines()]
    i = 0
    df_page_AVF_std = pd.DataFrame()
    ##### stdの計算が必要な場合
    # for filename in csv_list:
    #     print("\nfilename: "+filename)
    #     benchmark = re.sub('_.*$','', re.sub('line_AVF_\d{3}.', '', filename))

    #     df_page_AVF_std.loc[benchmark, 'std']=line_AVF_within_page(filename)
        
        # i += 1
        # if i >2:
        #     break
    ###### stdのファイルが存在している場合
    for benchmark in list_benchmark:
        print("\nfilename: "+benchmark)
        ind = re.sub( '_.*$','', re.sub('^\d{3}.', '', benchmark)) 
        df_page_AVF_std.loc[ind, 'std']=line_AVF_within_page_fromfile(benchmark)
    df_page_AVF_std.loc['gmean', 'std']=df_page_AVF_std['std'].mean()
    ######## plot graph ############
    series_x = df_page_AVF_std.index.to_list()
    series_y = df_page_AVF_std['std']
    fig = plt.figure(figsize=(9,6))
    plt.rcParams["font.size"] = 16
 
    title = "all_benchmark_page_AVF_std"
    plt.bar(series_x, series_y)
    plt.xticks(rotation=70)
    plt.title(title+" access#>10")
    plt.xlabel('benchmark')
    plt.ylabel('AVF')
    fig.subplots_adjust(bottom=0.3)
    plt.show()
    makedir(dir_page_AVF_std_accth)
    fig.savefig(dir_page_AVF_std_accth+title+".png")
    
    df_page_AVF_std.to_csv(dir_page_AVF_std_accth+title+'access.csv', sep='\t')

def main():    
    # get json filename list
    directory = "results_10M_CSV/"
    results_list_path = "json_list.txt"
    results_cycle_path = "allcycle_list.txt"
    with open(results_list_path) as f:
        json_list = [l.strip() for l in f.readlines()]
    # line_AVF_within_page_fromfile()
    # AVF_WrRatio_from_file()
    # 全てのベンチマークについてAVF計算する。
    # for filename in json_list:
        # benchmark_AVF(filename)
    # benchmark_AVF(json_list[1])
        # benchmark_AVF_Wr_ratio(filename)
    # #ライン粒度でのAVFのベンチマークごとの平均算出
    # AVF_all_ave(json_list)
    
    all_benchmark_AVF_std()
    ## グラフ作成テスト（グラフのタイトル調整用なので今後消す）
    # graph_test(json_list)


################# program start ############

makedir(dir_WrRatio)
makedir(dir_corr)
makedir(dir_page_WrRatio)
main()
