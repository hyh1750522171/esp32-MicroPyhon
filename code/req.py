import urequests  # 引入urequests库
import ujson
def send_post_request():
    url = 'http://192.168.1.12/wifiInfo.json'  # 指定请求的URL
    headers = {'Content-Type': 'application/json'}  # 指定发送的数据类型为JSON
    data = {
        "key": ""
    }
    # 转换数据为JSON字符串
    data_json = ujson.dumps(data)

    # 准备要发送的数据
    print("请求数据：",data_json)
    # 发送POST请求
    response = urequests.get(url, data=data_json, headers=headers)

    # 1检查请求是否成功
    if response.status_code == 200:
        print("请求成功，返回的数据：")
        response_text = response.text
        response_text = response_text.encode('utf-8').decode('unicode-escape')  # 解码Unicode转义字符
        print(response_text)  # 打印返回的JSON数据
    else:
        print("请求失败，状态码：", response.status_code)

    response.close()  # 关闭连接
    
send_post_request()
