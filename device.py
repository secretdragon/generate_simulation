from math import radians, cos, sin, asin, sqrt
from haversine import haversine, Unit

class Device(object):
    def __init__(self, info_device):
        self.id = info_device['id']
        self.location = [float(info_device['location'].split(',')[0]), float(info_device['location'].split(',')[1])]
        self.radius = info_device['radius']
        self.tracked_objects = []
        self.virtual_location = info_device['virtual_location']
        self.status = info_device['status']

    def record_track_device(self, info_track, all_record_tracks_camera):
        """

        :param info_track:
        :return:
        """
        # 计算设备到人的轨迹的距离
        distances = self._get_distance(self.location, info_track)
        # 计算设备到捕获点的距离
        distance_captures = self._get_distance_capture(self.location, all_record_tracks_camera)

        # 获取所有小于threshold的元素的索引和数值
        indices = []
        values = []
        for i, x in enumerate(distance_captures):
            if x <= self.radius:
                indices.append(i)
                values.append(x)

        # 如果人在半径范围内，记录其轨迹
        for distance in distances:
            if distance <= self.radius:
                if len(values) == 0:
                    # get index if distance < radius
                    index = distances.index(distance)
                    capture_time = info_track[index][1]

                    if 'deliveryman' in info_track[index][0]:
                        object_id = info_track[index][0].replace('deliveryman', 'imsi')
                    elif 'salaryman' in info_track[index][0]:
                        object_id = info_track[index][0].replace('salaryman', 'imsi')
                    elif 'taximan' in info_track[index][0]:
                        object_id = info_track[index][0].replace('taximan', 'imsi')
                    device = 'None'
                    print('??????????????????????????????????????????????????????????????????????????????????????', [self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status])
                    self.tracked_objects.append([self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status])
                else:
                    # get index if distance < radius
                    index = distances.index(distance)
                    for indice, value in zip(indices, values):
                        capture_time = info_track[index][1]

                        if 'deliveryman' in info_track[index][0]:
                            object_id = info_track[index][0].replace('deliveryman', 'imsi')
                        elif 'salaryman' in info_track[index][0]:
                            object_id = info_track[index][0].replace('salaryman', 'imsi')
                        elif 'taximan' in info_track[index][0]:
                            object_id = info_track[index][0].replace('taximan', 'imsi')

                        device = all_record_tracks_camera[indice][0]
                        if len(self.tracked_objects)==0:
                            print('??????????????????????????????????????????????????????????????????????????????????????', [self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status])
                            self.tracked_objects.append([self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status])
                        elif [self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status] == self.tracked_objects[-1]:
                            pass
                            # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>重复了')
                        else:
                            print('??????????????????????????????????????????????????????????????????????????????????????', [self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status])
                            self.tracked_objects.append([self.id, capture_time, self.location[0], self.location[1], object_id, device, self.virtual_location, self.status])

        return self.tracked_objects

    def _get_distance(self, location, info_track):
        """

        :param location:
        :param info_track:
        :return: [distance1, distance2, distance3]
        """
        # 计算两点之间的距离
        # 将十进制度数转化为弧度
        device_lat = location[0]
        device_lon = location[1]

        distances = []
        for obj_person in info_track:
            object_lat = obj_person[2]
            object_lon = obj_person[3]
            distance = haversine((device_lat, device_lon), (object_lat, object_lon), unit=Unit.METERS)  # m
            distances.append(distance)
        return distances

    def _get_distance_capture(self, location, record_tracks_camera):
        """

        :param location:
        :param info_track:
        :return: [distance1, distance2, distance3]
        """
        # 计算两点之间的距离
        # 将十进制度数转化为弧度
        camera_lat = location[0]
        camera_lon = location[1]
        distances = []
        # record_tracks_camera ===>>>> ['camera_id', 'time', 'latitude', 'longitude', 'capture_id']
        for obj_capture in record_tracks_camera:
            object_lat = obj_capture[2]
            object_lon = obj_capture[3]
            distance = haversine((camera_lat, camera_lon), (object_lat, object_lon), unit=Unit.METERS)  # m
            distances.append(distance)
        return distances







