from tkinter import W
import pandas as pd
import AVF_variation as std
import pdb 
import re
import matplotlib.pyplot as plt
import makedir

def AVF_variation_graph(list_benchmark, dir_line_AVF):
    acc_th= 20
    pdb.set_trace()
    column_name = 'AVF_std_acc_'+str(acc_th)
    df_all_benchmark = pd.DataFrame(columns=['AVF_std', column_name])
    for benchmark in list_benchmark:
        if benchmark != '619.lbm':
            df_buffer = std.func(benchmark, dir_line_AVF, acc_th) 
            df_all_benchmark.loc[benchmark]=df_buffer 

    ##### plot graph 
    title = 'all_benchmark_AVF_std'
    series_x = [ re.sub('\d{3}.', '', l) for l in df_all_benchmark.index.to_list()]
    series_y = df_all_benchmark['AVF_std']
    fig = plt.figure(figsize=(9,6))
    plt.rcParams["font.size"] = 12

    plt.bar(series_x, series_y)
    plt.xticks(rotation=80)
    # plt.title(title+" access# "+str(acc_th))
    plt.title(title)
    plt.xlabel('benchmark')
    plt.ylim(0,1)
    plt.ylabel('AVF')
    fig.subplots_adjust(bottom=0.3)
    # plt.show()
    dir_AVF_variation = re.sub('LINE_AVF', 'variation', dir_line_AVF)
    makedir.func(dir_AVF_variation)
    fig.savefig(dir_AVF_variation+title+'_acc'+str(acc_th)+".png")
    df_all_benchmark.to_csv(dir_AVF_variation+'all_benchmark_AVF_std.csv', sep='\t')


if __name__ == '__main__':
    print('all_benchmarks_AVF_variation')
    
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

    AVF_variation_graph(list_benchmark, dir_line_AVF='../results_100M_LINE_AVF/') 
