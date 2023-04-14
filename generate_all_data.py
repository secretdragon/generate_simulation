# -*- coding:utf-8 -*-
# @author ：sbc
# @time   : 2023/3/6
# @file   : generate_data.py
import random
import json
from random import choice
import pandas as pd
import numpy as np
from camera import Camera
from device import Device
from traffic import Traffic
from get_route import generate_deliveryman_routes, generate_salaryman_routes, generate_taximan_routes
from clickhouse_driver import connect, Client




def get_bounds(coords):
    """

    :param coords:
    :return:
    """
    min_lat, min_lng = float('inf'), float('inf')
    max_lat, max_lng = float('-inf'), float('-inf')

    for lat, lng in coords:
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
        min_lng = min(min_lng, lng)
        max_lng = max(max_lng, lng)

    return [[min_lat, min_lng], [max_lat, max_lng]]






if __name__ == "__main__":
    with open(f"./{'栖霞营业厅'}.json", "r") as f:
        location_error = json.load(f)

    # 获取配置文件
    with open('./config.json', 'r') as f:
        config = json.load(f)
    people_num = config['people_num']
    camera_num = config['camera_num']
    camera_locations = []
    radius = config['camera_radius']

    # 生成所有人的轨迹
    deliveryman_num = int(people_num*0.1)
    salaryman_num = int(people_num*0.4)
    taximan_num = int(people_num*0.5)

    index = 0
    total_gps_track = []
    total_gps_track_deliveryman = generate_deliveryman_routes(deliveryman_num, index)
    index = index + deliveryman_num
    total_gps_track.extend(total_gps_track_deliveryman)
    total_gps_track_salaryman = generate_salaryman_routes(salaryman_num, index)
    index = index + salaryman_num
    total_gps_track.extend(total_gps_track_salaryman)
    total_gps_track_taximan = generate_taximan_routes(taximan_num, index)
    total_gps_track.extend(total_gps_track_taximan)

    # 获取所有运动的点
    all_points = [[point[2], point[3]] for point in total_gps_track if point[-1] != 0]

    df = pd.DataFrame(total_gps_track, columns=['appuserid', 'ltime', 'latitude', 'longitude', 'status'])
    # 将DataFrame保存为CSV文件
    df.to_csv(f'./person.csv', index=False)

    [[min_lat, min_lng], [max_lat, max_lng]] = get_bounds(all_points)
    # # 生成随机经度坐标
    # lons_camera = np.random.uniform(min_lng, max_lng, size=camera_num)
    #
    # # 生成随机纬度坐标
    # lats_camera = np.random.uniform(min_lat, max_lat,size=camera_num)

    # 获取每个摄像头的捕获ID
    device_num = config['device_num']
    total_num = device_num
    # 生成随机经度坐标
    lons = np.random.uniform(min_lng, max_lng, size=total_num)

    # 生成随机纬度坐标
    lats = np.random.uniform(min_lat, max_lat,size=total_num)
    # 获取每个摄像头的捕获ID
    all_record_tracks_camera = []
    total_locations = []
    for camera_id in range(camera_num):
        record_tracks = []
        # all_points = [list(x) for x in set(tuple(x) for x in all_points)]
        # location =  random.sample(all_points, 1)[0]
        location = [lats[camera_id], lons[camera_id]]
        # 记录所有人脸摄像头的位置
        camera_locations.append([f"traffic_camera_{camera_id}", location, radius])
        # 创建摄像头的信息
        inf_camera = {
            "id": f"traffic_camera_{camera_id}",
            "direction":0,
            "field_of_view":360,
            "location":f"{location[0]},{location[1]}",
            "radius":radius
        }
        # 遍历每个人的轨迹是否经过该摄像头
        traffic = Traffic(inf_camera)
        record_track = traffic.record_track(total_gps_track)

        record_tracks.extend(record_track)
        # 按时间排序
        record_tracks_camera = sorted(record_tracks, key=lambda x: x[1])
        # 获取每个摄像头的信息
        all_record_tracks_camera.extend(record_tracks_camera)

    # 将列表转换为pandas DataFrame
    df = pd.DataFrame(all_record_tracks_camera, columns=['camera_id', 'ltime', 'latitude', 'longitude', 'direction', 'field_of_view', 'capture_id'])
    # 将DataFrame保存为CSV文件
    df.to_csv(f'./camera.csv', index=False)
    print('摄像头的捕获信息')




    all_record_tracks_device = []
    for device_id in range(device_num):
        record_tracks = []
        location = choice(all_points)
        # 创建基站的信息
        # 生成随机经度坐标
        # lons = np.random.uniform(min_lng, max_lng, size=device_num)
        # # 生成随机纬度坐标
        # lats = np.random.uniform(min_lat, max_lat, size=device_num)
        ID = device_id

        # 正常基站 status：0
        inf_device_normal = {
            "id": f"device_{device_id}",
            "location":f"{lats[ID]},{lons[ID]}",
            "virtual_location": f"{lats[ID]},{lons[ID]}",
            "status":"0",
            "radius":config['device_radius']
        }
        # 错误基站 虚拟经纬度为0 status：1, 虚拟经纬度不一致 status：2
        inf_device_error1 = {
            "id": f"device_{device_id}",
            "location":f"{lats[ID]},{lons[ID]}",
            "virtual_location": f"{0},{0}",
            "status":"1",
            "radius":config['device_radius']
        }

        inf_device_error2 = {
            "id": f"device_{device_id}",
            "location":f"{lats[ID]},{lons[ID]}",
            "virtual_location": f"{choice(location_error['营业厅'])[1]},{choice(location_error['营业厅'])[2]}",
            "status":"2",
            "radius":config['device_radius']
        }

        # 坏基站 相对捕获点比较少
        inf_device_bad = {
            "id": f"device_{device_id}",
            "location":f"{lats[ID]},{lons[ID]}",
            "virtual_location": f"{lats[ID]},{lons[ID]}",
            "status":"3",
            "radius":config['device_radius'] // 4
        }

        device_values = [inf_device_normal, inf_device_error1, inf_device_error2, inf_device_bad]
        device_weights = [0.5, 0.0, 0.0, 0.5]
        inf_device = random.choices(device_values, weights=device_weights)[0]

        # 遍历每个人的轨迹是否经过该设备
        device = Device(inf_device)
        # record_tracks_camera ===>>>> ['camera_id', 'time', 'latitude', 'longitude', 'capture_id']
        record_track_device = device.record_track_device(total_gps_track, all_record_tracks_camera)
        record_tracks.extend(record_track_device)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', device_id)
        record_tracks = sorted(record_tracks, key=lambda x: x[1])
        # # 将列表转换为pandas DataFrame
        # df = pd.DataFrame(record_tracks,
        #                   columns=['device_id', 'time', 'latitude', 'longitude', 'capture_id', 'device_relation'])
        # # 将DataFrame保存为CSV文件
        # df.to_csv(f'./device_{device_id}.csv', index=False)

        all_record_tracks_device.extend(record_tracks)
    # 将列表转换为pandas DataFrame
    df = pd.DataFrame(all_record_tracks_device, columns=['bsid', 'ltime', 'latitude', 'longitude', 'imsi', 'device_relation', 'virtual_location', 'status'])
    # 将DataFrame保存为CSV文件
    df.to_csv(f'./device.csv', index=False)
    print('设备的捕获信息')

    # 导入数据库中
    client = Client(host='10.1.203.216', port=9000, user='default', password='test', database='default')

    # 创建数据库和表
    client.execute('DROP DATABASE simulate_0413')


    # 读取CSV文件并将其转换为Pandas数据帧
    df = pd.read_csv('./person.csv')

    # 将数据插入ClickHouse数据库
    client.execute('CREATE DATABASE IF NOT EXISTS simulate_0413')
    client.execute('USE simulate_0329')
    # 插入人物轨迹表
    client.execute('DROP TABLE IF EXISTS simulate_0413.person')
    client.execute(
        'CREATE TABLE simulate_0413.person (`appuserid` String, `ltime` Float32, `latitude` Float32, `longitude` Float32, `status` Int32) ENGINE = MergeTree() ORDER BY appuserid')
    client.execute(
        'INSERT INTO simulate_0413.person (appuserid, ltime, latitude, longitude, status) VALUES', [tuple(row) for row in df[['appuserid', 'ltime', 'latitude', 'longitude', 'status']].values])

    # 插入摄像头捕获表
    df = pd.read_csv('./camera.csv')
    client.execute('DROP TABLE IF EXISTS simulate_0329.camera')
    client.execute(
        'CREATE TABLE simulate_0413.camera (`camera_id` String, `ltime` Int32, `latitude` Float32, `longitude` Float32, `direction` Int32, `field_of_view` Int32, `capture_id` String) ENGINE = MergeTree() ORDER BY camera_id')
    client.execute(
        'INSERT INTO simulate_0413.camera (camera_id, ltime, latitude, longitude, direction, field_of_view, capture_id) VALUES', [tuple(row) for row in df[['camera_id', 'ltime', 'latitude', 'longitude', 'direction', 'field_of_view', 'capture_id']].values])

    # 插入设备捕获信息
    df = pd.read_csv('./device.csv')
    client.execute('DROP TABLE IF EXISTS simulate_0329.device')
    client.execute(
        'CREATE TABLE simulate_0413.device (`bsid` String, `ltime` Int32, `latitude` Float32, `longitude` Float32, `imsi` String, `device_relation` String, `virtual_location` String, `status` Int32) ENGINE = MergeTree() ORDER BY bsid')
    client.execute(
        'INSERT INTO simulate_0413.device (bsid, ltime, latitude, longitude, imsi, device_relation, virtual_location, status) VALUES', [tuple(row) for row in df[['bsid', 'ltime', 'latitude', 'longitude', 'imsi', 'device_relation', 'virtual_location', 'status']].values])


    # 关闭连接
    client.disconnect()









