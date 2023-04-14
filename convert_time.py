import time
import json
import pandas as pd

with open('./config.json', 'r') as f:
    config = json.load(f)

global generate_time
generate_time = config["generate_time"]

def convert_time_to_str(time):
    #时间数字转化成字符串，不够10的前面补个0
    if (time < 10):
        time = '0' + str(time)
    else:
        time=str(time)
    return time


def datetime_timestamp(dt):
    # dt为字符串
    # 中间过程，一般都需要将字符串转化为时间数组
    time.strptime(dt, '%Y-%m-%d %H:%M:%S')
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=-1)
    # 将"2012-03-28 06:53:40"转化为时间戳
    s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
    return int(s)

def sec_to_data(y):

    h=int(y//3600 % 24)
    d = int(y // 86400)
    m =int((y % 3600) // 60)
    s = round(y % 60,2)
    h=convert_time_to_str(h)
    m=convert_time_to_str(m)
    s=convert_time_to_str(s)
    d=convert_time_to_str(d)
    # 天 小时 分钟 秒
    return generate_time + h + ":" + m + ":" + s.split('.')[0]

if __name__ == "__main__":
    data = pd.read_csv('./person.csv')
    data[u'ltime'] = data[u'ltime'].apply(lambda x : datetime_timestamp(sec_to_data(x*60)))
    data.to_csv('./person_test.csv',index=False, encoding='utf-8')



