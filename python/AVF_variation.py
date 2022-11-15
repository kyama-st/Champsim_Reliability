from asyncio import AbstractChildWatcher
import pandas as pd
import pdb

def func(benchmark, dir_line_AVF, acc_th):
    #### csvファイルの取り込み 
    print(benchmark)
    df_line_AVF = pd.read_csv(dir_line_AVF+benchmark+'_LINE_AVF.csv', sep='\t', index_col=0)
    list_AVF_std = [] 
    ## 1ページ内のラインAVF平均値とその標準偏差の算出
    ### page内のアクセス回数、lineAVFの平均値、標準偏差を保存するdf
    df_groupedby_page = df_line_AVF.groupby('Page')
    series_AVF_std = df_groupedby_page.std()['AVF']  
    df_page = pd.DataFrame(series_AVF_std)
    df_page.rename(columns={'AVF':'AVF_std'}, inplace=True)
    df_page['page_AVF'] = df_groupedby_page.mean()['AVF']
    df_page['access'] = df_groupedby_page.sum()['Wr']+df_groupedby_page.sum()['Rd'] 

    ##### AVFの標準偏差
    list_AVF_std.append(df_page.mean()['AVF_std'])
    
    ### アクセス回数が閾値以上のページについて標準偏差を計算する
    df_page_extractby_acc = df_page.query('@acc_th <= access') 
    list_AVF_std.append(df_page_extractby_acc['AVF_std'].mean()) 
    # pdb.set_trace()
    return list_AVF_std 

if __name__ == '__main__':
    print("AVF variation")