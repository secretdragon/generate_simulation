import json
import requests



def get_location(query, address):
    result_query = {}
    result_query[query] = []
    # 百度地图API密钥
    ak = "8R77GhjvVwe1YDXSMKpEHjvLeK80u1iV"

    # 地址
    # address = ['玄武区','秦淮区','建邺区','鼓楼区','浦口区','栖霞区','雨花台区','江宁区','六合区','溧水区','高淳区']
    # 构造API请求
    url = f"http://api.map.baidu.com/place/v2/search?query={query}&region={address}&output=json&ak={ak}"

    # 分页查询，每页最多返回20个结果
    page_size = 100
    for page_num in range(4):
        # 构造请求URL
        page_url = f"{url}&page_size={page_size}&page_num={page_num}"
        # 发送请求并获取响应
        response = requests.get(page_url)
        if response.status_code == 200:
            print('请求成功')
            # 解析响应数据，获取外卖的经纬度信息
            results = response.json()["results"]
            for result in results:
                name = result["name"]
                location = result["location"]
                address = result['address']
                longitude, latitude = location["lng"], location["lat"]
                result_query[query].append([name, latitude, longitude, address])
    return result_query




if __name__ == "__main__":
    query = '营业厅'
    address = '南京市栖霞区'
    result_query = get_location(query, address)
    with open(f"./栖霞{query}.json", "w") as f:
        json.dump(result_query, f)








