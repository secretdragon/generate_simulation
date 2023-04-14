import pandas as pd
from clickhouse_driver import connect, Client
client = Client(host='10.1.203.216', port=9000, user='default', password='test', database='default')

# 创建数据库和表
client.execute('CREATE DATABASE IF NOT EXISTS simulate_0328')

# 读取CSV文件并将其转换为Pandas数据帧
df = pd.read_csv('./camera.csv')

# 将数据插入ClickHouse数据库
client.execute('CREATE DATABASE IF NOT EXISTS simulate_0328')
client.execute('USE simulate_0328')
client.execute('DROP TABLE IF EXISTS simulate_0328.camera')
client.execute('CREATE TABLE simulate_0328.camera (`camera_id` String, `ltime` Int32, `latitude` Float32, `longitude` Float32, `direction` Int32, `field_of_view` Int32, `capture_id` String) ENGINE = MergeTree() ORDER BY camera_id')
client.execute('INSERT INTO simulate_0328.camera (camera_id, ltime, latitude, longitude, direction, field_of_view, capture_id) VALUES', [tuple(row) for row in df[['camera_id', 'ltime', 'latitude', 'longitude', 'direction', 'field_of_view', 'capture_id']].values])

# 关闭连接
client.disconnect()
