from math import sin, asin, cos, radians, fabs, sqrt
from geopy.distance import geodesic
from haversine import haversine, Unit
from clickhouse_driver import connect, Client
EARTH_RADIUS = 6371      # 地球平均半径大约6371km


def hav(theta):
    s = sin(theta / 2)
    return s * s


def get_distance_hav(lat0, lng0, lat1, lng1):
    # 用haversine公式计算球面两点间的距离
    # 经纬度转换成弧度
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)
    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))      # km
    return distance


def compute_distance(device_lat, device_lon, object_lat, object_lon):
    lon1, lat1, lon2, lat2 = map(radians, [device_lat, device_lon, object_lat, object_lon])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000



if __name__ == "__main__":
    client = Client(host='10.1.203.216', port=9000, user='default', password='test', database='default')
    data = client.execute('SELECT *  FROM simulate_0404.person')
    # data_result = [data_little for data_little in data if data_little[0] == 'deliveryman_6']
    data_result = []
    for data_little in data:
        if data_little[0] == 'salaryman_5':
            # print(data_little)
            data_result.append(data_little)

    point1 = (32.03075408935547, 118.7471694946289)
    for data_little in data_result:
        point2 = (float(data_little[2]), float(data_little[3]))
        result2 = haversine(point1, point2, unit=Unit.METERS)  # m
        if result2 < 500:
            print(result2)



    # print("距离：{:.2f}m".format(distance))
    # result = get_distance_hav(point1[0], point1[1], point2[0], point2[1])
    # print("距离：{:.2f}km".format(result))
    # distance = geodesic((point1[0], point1[1]), (point2[0], point2[1])).km
    # print("距离：{:.3f}km".format(distance))
    # # 两点的经纬度
    # result1 = haversine(point1, point2, unit=Unit.KILOMETERS)  # km
    # result2 = haversine(point1, point2, unit=Unit.METERS)  # m
    # # 打印计算结果
    # print("距离：{:.3f}km".format(result1))
    # print("距离：{:.3f}m".format(result2))