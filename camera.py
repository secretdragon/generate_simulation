from math import radians, cos, sin, asin, sqrt
from haversine import haversine, Unit

class Camera(object):
    def __init__(self, info_camera):
        self.id = info_camera['id']
        self.location = [float(info_camera['location'].split(',')[0]), float(info_camera['location'].split(',')[1])]
        self.radius = info_camera['radius']
        self.tracked_objects = []

    def record_track(self, info_track):
        """

        :param info_track:
        :return:
        """
        # 计算物体到摄像头的距离
        distances = self._get_distance(self.location, info_track)

        # 如果物体在半径范围内，记录其轨迹 distances [[id, time, distance], [id, time, distance], [id, time, distance]]
        for distance in distances:
            if distance[-1] <= self.radius:
                object_id = distance[0]
                capture_time = distance[1]
                latitude = distance[2]
                longitude = distance[3]
                self.tracked_objects.append([self.id,  capture_time, latitude, longitude, object_id])

        return self.tracked_objects

    def _get_distance(self, location, info_track):
        """

        :param location:
        :param info_track:
        :return: [distance1, distance2, distance3]
        """
        # 计算两点之间的距离
        # 将十进制度数转化为弧度
        camera_lon = location[0]
        camera_lat = location[1]
        distances = []
        for obj_person in info_track:
            object_id  = obj_person[0]
            object_time = obj_person[1]
            object_lat = obj_person[2]
            object_lon = obj_person[3]
            distance = haversine((camera_lat, camera_lon), (object_lat, object_lon), unit=Unit.METERS)  # m
            distances.append([object_id, object_time, object_lat, object_lon, distance])
        return distances





