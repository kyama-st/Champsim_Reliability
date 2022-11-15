import imp
import numpy  
import makedir
import pandas as pd
import time
import elapsed_time
import pdb
from numpy import NaN, average, float32, sort
import re

def ACE(df_grouped, all_cycle):
    series_buffer = df_grouped.iloc[0, [1,3]]
    df_temp = pd.DataFrame([series_buffer])
    df_grouped.loc[df_grouped["R/W"]=="Read", "ACE"]=df_grouped["Cycle"].diff(1).fillna(df_grouped["Cycle"]) 
    df_grouped.loc[df_grouped["R/W"]=="Write", "ACE"]=0

    df_temp['AVF'] = df_grouped['ACE'].sum()/all_cycle
    df_bool_rd = (df_grouped == 'Read')
    df_bool_wr = (df_grouped == 'Write')
    num_rd = df_bool_rd.sum().sum()
    num_wr = df_bool_wr.sum().sum()
    df_temp['Rd']= num_rd
    df_temp['Wr']= num_wr
    wr_ratio = num_wr/num_rd if num_rd != 0 else 1 
    df_temp['WrRd']= wr_ratio 

    return df_temp 

def func(benchmark, dir_json):
    print("対象のベンチマーク: ", end="")
    print(benchmark)
    #ベンチマークごとに処理時間がどれくらいかかるか記録する用
    start_time = time.time() 

    ## jsonファイル取り込み
    df_json = pd.read_json(dir_json+benchmark+".json")
    ## サイクル数取り込み
    cycle_file = dir_json + benchmark + ".txt"
    with open(cycle_file) as f:
        all_cycle = int(f.read().strip())
    ##　ラインのAVFを計算する
    # pdb.set_trace()
    df_line_AVF=df_json.groupby('Address').apply(ACE, all_cycle=all_cycle)
    df_line_AVF.reset_index(drop=True, inplace=True)
    dir_line_AVF = re.sub('JSON', 'LINE_AVF', dir_json) 
    makedir.func(dir_line_AVF)
    # # #### line_AVF_CSV保存 ####
    df_line_AVF.to_csv(dir_line_AVF+benchmark+'_LINE_AVF.csv', sep='\t')

    #終了時刻
    end_time = time.time()
    #経過時間の表示
    elapsed_time.func(start_time, end_time)



if __name__ == '__main__':
    print("Calculate AVF")