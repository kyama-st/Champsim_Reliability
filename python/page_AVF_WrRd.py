from cProfile import label
import imp
from tkinter import W
from turtle import width
import pandas as pd 
import pdb
import re 
import matplotlib.pyplot as plt
import numpy as np

def func(benchmark, dir_line_AVF):
    print('現在のベンチマーク: '+benchmark)
    df_line_AVF = pd.read_csv(dir_line_AVF+benchmark+'_LINE_AVF.csv', sep='\t', index_col=0) 

    df_grouped = df_line_AVF.groupby('Page')
    series_AVF = df_grouped.mean()['AVF']
    df_page = pd.DataFrame(series_AVF)
    df_page['access'] = df_grouped.sum()['Wr']+df_grouped.sum()['Rd']
    df_page['std'] = df_grouped.std()['AVF']
    
    df_sortedby_access = df_page.sort_values('access', ascending=False)
    list_page = df_sortedby_access.index

    pdb.set_trace()

    for page in list_page:

        df_extractedby_page = df_line_AVF.query('Page == @page')
        bins=np.linspace(0,1.0,11)
        mean_AVF = df_extractedby_page.mean()['AVF']
        freq_AVF = df_extractedby_page['AVF'].value_counts(bins=bins, normalize=True, sort=False)
        arr_freq_AVF = np.array(freq_AVF)
        max_freq_AVF = freq_AVF.max()
        print(freq_AVF)
        ##### plot histgram
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))
        axes[0].hist(df_extractedby_page['AVF'], range=(0, 1.0), bins=10, ec='black', label='frequency')
        axes[1].bar(bins[:-1], arr_freq_AVF, width=0.1 , edgecolor='black',color='orange', align='edge' ,label='relative frequency')
        axes[1].set_ylim(0,1.0)

        axes[0].legend()
        axes[1].legend()
        axes[0].set_title(benchmark+": line AVF in page#"+str(page)+" access counts:"+str(df_sortedby_access.loc[page, 'access']))
        # plt.show()
        plt.savefig(dir_line_AVF+benchmark+"_"+str(page)+"_AVF_relative_hist.png")

        if page == list_page[5]:
            break
    return 0

if __name__ == '__main__':
    print("page_AVF_WrRd")

