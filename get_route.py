import json
import requests
import random
import pandas as pd
from random import choice
from random import uniform
from geopy.distance import geodesic
from clickhouse_driver import connect, Client
from convert_time import datetime_timestamp, sec_to_data

# 第一步获取所有位置库的信息
querys = ['住宅区', '公寓式酒店', '写字楼', '小吃快餐店', '快捷酒店', '景点', '电影院', '购物中心', '超市']


with open(f"./{'住宅区'}.json", "r") as f:
    location_home = json.load(f)

with open(f"./{'写字楼'}.json", "r") as f:
    location_company = json.load(f)

location_other = {}
location_other['其它位置'] = []
with open(f"./{'小吃快餐店'}.json", "r") as f:
    location = json.load(f)
    location_other['其它位置'].extend(location['小吃快餐店'])

with open(f"./{'快捷酒店'}.json", "r") as f:
    location = json.load(f)
    location_other['其它位置'].extend(location['快捷酒店'])

with open(f"./{'电影院'}.json", "r") as f:
    location = json.load(f)
    location_other['其它位置'].extend(location['电影院'])

with open(f"./{'购物中心'}.json", "r") as f:
    location = json.load(f)
    location_other['其它位置'].extend(location['购物中心'])

# 构建路径
# 百度地图API密钥
api_key = "veCvYtG6Uyz0i6XDpNKMutK0WacXEvOj"

# 外卖员路径
# 调用百度地图API获取路径规划
def generate_deliveryman_route(location_start, location_end, time_start, id, gps_track_deliveryman):

    origin = f"{location_start[1]},{location_start[2]}"
    destination = f"{location_end[1]},{location_end[2]}"

    url = "http://api.map.baidu.com/directionlite/v1/riding?origin={}&destination={}&ak={}&tactics=12".format(origin, destination, api_key)
    response = requests.get(url)
    result = json.loads(response.text)

    # 提取路径规划结果
    route = result["result"]["routes"][0]
    steps = route["steps"]

    # 打印路径规划结果
    for step in steps:
        time_duration = step['duration'] / 60
        path = step['path']
        interval = time_duration / len(path.split(';'))
        for time in range(len(path.split(';'))):
            lng, lat = path.split(';')[time].split(",")
            time_start = time_start + interval
            gps_track_deliveryman.append((id, datetime_timestamp(sec_to_data(time_start*60)), float(lat), float(lng), 1))

    return gps_track_deliveryman, time_start


# 上班族路径
def generate_salaryman_route(location_start, location_end, time_start, id, gps_track_worker):
    origin = f"{location_start[1]},{location_start[2]}"
    destination = f"{location_end[1]},{location_end[2]}"

    url = "http://api.map.baidu.com/directionlite/v1/transit?origin={}&destination={}&ak={}".format(origin, destination, api_key)

    response = requests.get(url)
    result = json.loads(response.text)

    # 提取路径规划结果
    route = result["result"]["routes"][0]
    steps = route["steps"]

    # 打印路径规划结果
    for step in steps:
        time_duration = step[0]['duration'] / 60
        path = step[0]['path']
        interval = time_duration / len(path.split(';'))
        for time in range(len(path.split(';'))):
            lng, lat = path.split(';')[time].split(",")
            time_start = time_start + interval
            gps_track_worker.append((id, datetime_timestamp(sec_to_data(time_start*60)), float(lat), float(lng), 1))
    return gps_track_worker, time_start

# 出租车路径
def get_taxi_route(location_start, location_end, time_start, id, gps_track_taxi):
    origin = f"{location_start[1]},{location_start[2]}"
    destination = f"{location_end[1]},{location_end[2]}"

    url = "http://api.map.baidu.com/directionlite/v1/driving?origin={}&destination={}&ak={}".format(origin, destination, api_key)


    response = requests.get(url)
    result = json.loads(response.text)

    # 提取路径规划结果
    route = result["result"]["routes"][0]
    steps = route["steps"]

    # 打印路径规划结果
    for step in steps:
        time_duration = step['duration'] / 60
        path = step['path']
        interval = time_duration / len(path.split(';'))
        for time in range(len(path.split(';'))):
            lng, lat = path.split(';')[time].split(",")
            time_start = time_start + interval
            gps_track_taxi.append((id, datetime_timestamp(sec_to_data(time_start*60)), float(lat), float(lng), 1))
    return gps_track_taxi, time_start

# 逗留路径
def get_stay_route(location_stay, time_start, time_end, id, gps_track_stay):
    # 逗留时间
    time_stay = time_end - time_start
    # 逗留半径
    radius = 0.01
    # 中心坐标
    center_point = (location_stay[1], location_stay[2])
    # 间隔时间
    interval = 30

    # 生成逗留点
    box = geodesic(kilometers=radius).destination(center_point, bearing=45)
    min_lat, min_lon = min(center_point[0], box.latitude), min(center_point[1], box.longitude)
    max_lat, max_lon = max(center_point[0], box.latitude), max(center_point[1], box.longitude)
    # 生成随机点
    points = int(time_stay / interval)
    for i in range(points):
        lat = uniform(min_lat, max_lat)
        lng = uniform(min_lon, max_lon)
        time_start = time_start + interval
        gps_track_stay.append((id, datetime_timestamp(sec_to_data(time_start*60)), float(lat), float(lng), 0))
    return gps_track_stay, time_start

def generate_deliveryman_routes(num, index):
    total_gps_track_deliveryman = []
    for i in range(num):
        try:
            # 构建外卖员轨迹
            # time_start = random.randint(360, 540)
            time_start = 360
            id = f'deliveryman_{index + i}'
            gps_track_deliveryman = []

            # 开始构建轨迹
            location_start_1 = choice(location_home['住宅区'])
            location_end_1 = choice(location_other['其它位置'])
            # location_start_1 = location_home['住宅区'][i]
            # location_end_1 = location_company['写字楼'][i]
            # 获取在家逗留轨迹
            time_sleep = 0
            gps_track_deliveryman, time_start = get_stay_route(location_start_1, time_sleep, time_start, id, gps_track_deliveryman)

            # 出发开始送外卖
            gps_track_deliveryman, time_start = generate_deliveryman_route(location_start_1, location_end_1, time_start, id, gps_track_deliveryman)

            location_start_2 = location_end_1
            location_end_2 = choice(location_other['其它位置'])
            gps_track_deliveryman, time_start = generate_deliveryman_route(location_start_2, location_end_2, time_start, id, gps_track_deliveryman)

            location_start_3 = location_end_2
            location_end_3 = choice(location_other['其它位置'])
            gps_track_deliveryman, time_start = generate_deliveryman_route(location_start_3, location_end_3, time_start, id, gps_track_deliveryman)

            # 中途休息 12~13点
            # time_rest = random.randint(720, 780)
            time_rest = 720
            if time_start > time_rest:
                print('不休息')
            else:
                gps_track_deliveryman, time_start = get_stay_route(location_end_3, time_start, time_rest, id, gps_track_deliveryman)


            location_start_4 = location_end_3
            location_end_4 = choice(location_other['其它位置'])
            gps_track_deliveryman, time_start = generate_deliveryman_route(location_start_4, location_end_4, time_start, id, gps_track_deliveryman)

            location_start_5 = location_start_4
            location_end_5 = location_start_1
            gps_track_deliveryman, time_start = generate_deliveryman_route(location_start_5, location_end_5, time_start, id, gps_track_deliveryman)

            # 回家休息 21~24点
            # time_rest = random.randint(1260, 1440)
            time_rest = 1260
            time_end = 1440
            if time_start > time_rest:
                print('不休息')
            else:
                gps_track_deliveryman, time_start = get_stay_route(location_end_5, time_start, time_end, id, gps_track_deliveryman)
            print('0000000000000000000000000000000000000000000000000000000000000000', gps_track_deliveryman)
            total_gps_track_deliveryman.extend(gps_track_deliveryman)
        except:
            print('error~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return total_gps_track_deliveryman

def generate_salaryman_routes(num, index):
    total_gps_track_salaryman = []
    for i in range(num):
        try:
            # 构建上班族轨迹
            # time_start = random.randint(360, 540)
            time_start = 360
            id = f'salaryman_{index + i}'
            gps_track_salaryman = []

            # 开始构建轨迹
            location_start_1 = choice(location_home['住宅区'])
            location_end_1 = choice(location_company['写字楼'])
            # location_start_1 = location_home['住宅区'][i]
            # location_end_1 = location_company['写字楼'][i]
            # 获取在家逗留轨迹
            time_sleep = 0
            gps_track_salaryman, time_start = get_stay_route(location_start_1, time_sleep, time_start, id, gps_track_salaryman)

            # 出发开始工作
            gps_track_salaryman, time_start = generate_salaryman_route(location_start_1, location_end_1, time_start, id, gps_track_salaryman)


            # 中途休息 12~13点
            # time_rest = random.randint(720, 780)
            time_rest = 720
            if time_start > time_rest:
                print('不休息')
            else:
                gps_track_salaryman, time_start = get_stay_route(location_end_1, time_start, time_rest, id, gps_track_salaryman)

            location_start_2 = location_end_1
            location_end_2 = location_start_1

            gps_track_salaryman, time_start = generate_salaryman_route(location_start_2, location_end_2, time_start, id, gps_track_salaryman)

            # 回家休息 18~24点
            # time_rest = random.randint(1080, 1440)
            time_rest = 1080
            time_end = 1440
            if time_start > time_rest:
                print('不休息')
            else:
                gps_track_salaryman, time_start = get_stay_route(location_end_2, time_start, time_end, id, gps_track_salaryman)

            print('0000000000000000000000000000000000000000000000000000000000000000', gps_track_salaryman)
            total_gps_track_salaryman.extend(gps_track_salaryman)
        except:
            print('error~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return total_gps_track_salaryman

def generate_taximan_routes(num, index):
    total_gps_track_taximan = []
    for i in range(num):
        try:
            # 构建外卖员轨迹
            # time_start = random.randint(360, 540)
            time_start = 360
            id = f'taximan_{index + i}'
            gps_track_taximan = []

            # 开始构建轨迹
            location_start_1 = choice(location_home['住宅区'])
            location_end_1 = choice(location_company['写字楼'])
            # location_start_1 = location_home['住宅区'][i]
            # location_end_1 = location_company['写字楼'][i]
            # 获取在家逗留轨迹
            time_sleep = 0
            gps_track_taximan, time_start = get_stay_route(location_start_1, time_sleep, time_start, id, gps_track_taximan)

            # 出发开始送外卖
            gps_track_taximan, time_start = get_taxi_route(location_start_1, location_end_1, time_start, id, gps_track_taximan)

            location_start_2 = location_end_1
            location_end_2 = choice(location_company['写字楼'])
            gps_track_taximan, time_start = get_taxi_route(location_start_2, location_end_2, time_start, id, gps_track_taximan)

            location_start_3 = location_end_2
            location_end_3 = choice(location_company['写字楼'])
            gps_track_taximan, time_start = get_taxi_route(location_start_3, location_end_3, time_start, id, gps_track_taximan)

            # 中途休息 12~13点
            # time_rest = random.randint(720, 780)
            time_rest = 720
            if time_start > time_rest:
                print('不休息')
            else:
                gps_track_taximan, time_start = get_stay_route(location_end_3, time_start, time_rest, id, gps_track_taximan)

            location_start_4 = location_end_3
            location_end_4 = choice(location_company['写字楼'])
            gps_track_taximan, time_start = get_taxi_route(location_start_4, location_end_4, time_start, id, gps_track_taximan)

            location_start_5 = location_start_4
            location_end_5 = location_start_1
            gps_track_taximan, time_start = get_taxi_route(location_start_5, location_end_5, time_start, id, gps_track_taximan)

            # 回家休息 21~24点
            # time_rest = random.randint(1260, 1440)
            time_rest = 1260
            time_end = 1440
            if time_start > time_rest:
                print('不休息')
            else:
                gps_track_taximan, time_start = get_stay_route(location_end_5, time_start, time_end, id, gps_track_taximan)

            print('0000000000000000000000000000000000000000000000000000000000000000', gps_track_taximan)
            total_gps_track_taximan.extend(gps_track_taximan)
        except:
            print('error~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return total_gps_track_taximan

if __name__ == "__main__":
    # # 生成所有人的轨迹
    # total_gps_track = []
    # total_gps_track_deliveryman = generate_deliveryman_routes(3)
    # total_gps_track.extend(total_gps_track_deliveryman)
    # total_gps_track_salaryman = generate_salaryman_routes(3)
    # total_gps_track.extend(total_gps_track_salaryman)
    # total_gps_track_taximan = generate_taximan_routes(3)
    # total_gps_track.extend(total_gps_track_taximan)
    # df = pd.DataFrame(total_gps_track, columns=['appuserid', 'ltime', 'latitude', 'longitude', 'status'])
    # # 将DataFrame保存为CSV文件
    # df.to_csv(f'./person.csv', index=False)
    # # 将生成的轨迹上传数据库
    # # 将列表转换为pandas DataFrame
    # total_gps_track_deliveryman = generate_deliveryman_routes(3)
    # df = pd.DataFrame(total_gps_track_deliveryman, columns=['appuserid', 'ltime', 'latitude', 'longitude', 'status'])
    # # 将DataFrame保存为CSV文件
    # df.to_csv(f'./person.csv', index=False)
    client = Client(host='10.1.203.216', port=9000, user='default', password='test', database='default')

    # 创建数据库和表
    client.execute('CREATE DATABASE IF NOT EXISTS simulate_0329')

    # 读取CSV文件并将其转换为Pandas数据帧
    df = pd.read_csv('./person.csv')

    # 将数据插入ClickHouse数据库
    client.execute('CREATE DATABASE IF NOT EXISTS simulate_0329')
    client.execute('USE simulate_0329')
    client.execute('DROP TABLE IF EXISTS simulate_0329.person')
    client.execute(
        'CREATE TABLE simulate_0329.person (`appuserid` String, `ltime` Float32, `latitude` Float32, `longitude` Float32, `status` Int32) ENGINE = MergeTree() ORDER BY appuserid')
    client.execute(
        'INSERT INTO simulate_0329.person (appuserid, ltime, latitude, longitude, status) VALUES', [tuple(row) for row in df[['appuserid', 'ltime', 'latitude', 'longitude', 'status']].values])

    # 关闭连接
    client.disconnect()




















