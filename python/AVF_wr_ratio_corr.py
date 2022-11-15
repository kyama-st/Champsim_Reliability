import pandas as pd 
import pdb
def func(benchmark,dir_line_AVF):
    pdb.set_trace() 
    df_line_AVF = pd.read_csv(dir_line_AVF+benchmark+'_LINE_AVF.csv', sep='\t', index_col=0)      
    df_line_corr = df_line_AVF.corr
    

if __name__ == '__main__':
    print("AVF_wr_ratio_corr")