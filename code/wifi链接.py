# common/wifi.py
import time
import network


def format_wifi_data(datas):
    # 计算每列的最大宽度
    data = [(i[0].decode('utf-8'), i[3]) for i in datas]  # 解码 WiFi 名称
    column_widths = [max(len(str(value)) for value in column) for column in zip(*data)]

    # 输出表头
    print("-" * (sum(column_widths) + 10))
    header = "|   wifi 名称  | 信号强度 |"
    print(header)
    print("-" * (sum(column_widths) + 10))

    # 输出数据行
    for item in data:
        formatted_row = "".join(f"| {str(value).center(width)} " for value, width in zip(item, column_widths))
        print(formatted_row + "|")
    print("-" * (sum(column_widths) + 10))



def wifi_connect(ssid, password):
    # 创建 WIFI 连接对象
    wlan = network.WLAN(network.STA_IF)
    # 激活 wlan 接口
    wlan.active(True)

    # 断开之前的链接
    wlan.disconnect()
    # 扫描允许访问的 WiFi
    data = wlan.scan()
    print('扫描周围信号源：')
    format_wifi_data(data)
    # 打印出 WiFi 的名称和信号强度

    print("正在连接 WiFi 中", end="")
    # 连接 wifi
    wlan.connect(ssid, password)

    # 如果一直没有连接成功，则每隔 0.1s 在命令行中打印一个 .
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(0.1)

    # 连接成功之后，打印出 IP、子网掩码(netmask)、网关(gw)、DNS 地址
    print(
        f"\nwifi信息 -> IP: {wlan.ifconfig()[0]}, 子网掩码: {wlan.ifconfig()[1]}, 网关: {wlan.ifconfig()[2]}, DNS: {wlan.ifconfig()[3]}")


if __name__ == '__main__':
    wifi_connect('wifi名称', 'wifi密码')
