import time

def func(start_time, end_time):
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

    print("経過時間: ", end="")
    print(print_periods)
 
if __name__ == '__main__':
    print("elapsed_time")