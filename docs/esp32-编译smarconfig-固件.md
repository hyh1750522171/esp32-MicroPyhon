micropython 自己编译固件有几个好处

- 只加入自己需要的模块降低硬件资源占用
- .py文件可以修改中中间码，并烧录到固件内部，
- - 可以方便量产
- - 可一定程度保护代码
- - 更加省略了编译过程节省内存

我这里 只记录 添加 smartconfig的方法，并以S2 mini为例，其他esp32 同理。
简中网络上，几乎没有相关资料，有一些资料也是错的或无法使用。所以这里单独记录分享一下。 你可以直接下载 我编译好的
https://github.com/joyanhui/file.leiyanhui.com/blob/main/esp32/

# 准备

- linux系统，我这里是pve lxc运行的ubuntu22.04
- 科学工具 因为需要拉github
- 基本的linux基础

# 环境配置 和 依赖

修改到国内源，这个自己处理

```bash
apt install git wget curl make gcc cmake python3-venv
# ppa安装pythone 3.11  Ubuntu自带的版本太低
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa
# pip3
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py --force-reinstall
pip install mpy-cross-v6

```



# 克隆代码

```bash
mkdir esp32 && cd esp32
```





## esp-idf

注意 不同的esp32平台 micropython支持的esp-idf版本不同，详情参考 https://github.com/micropython/micropython/tree/master/ports/esp32#readme
linux小白 一步一步操作，注意里面的警告信息

```bash
git clone https://github.com/micropython/micropython.git
git clone https://github.com/Walkline80/MicroPython-SmartConfig-CModule
git clone -b v5.0.4 --recursive https://github.com/espressif/esp-idf.git esp-idf
cd esp-idf
git checkout v5.0.4
git submodule update --init --recursive

```



处理环境变量

```bash
./install.sh 
source export.sh

```



## micropython

本文基于 1.20 版本，如果新版失效，请 直接去下载 https://github.com/micropython/micropython/releases/download/v1.20.0/micropython-1.20.0.zip 不要 git clone最新的



```bash
cd ..
cd micropython
make -C mpy-cross
cd ports/esp32

```





Copy

# 测试默认编译micropython固件



```bash
make submodules
make USER_C_MODULES=../../../../smartconfig/cmodules/micropython.cmake、
```



##  测试代码



```bash
import network
import socket
import smartconfig
import time
import os
import json


def saveWifiInfo(ssid,password):
    """ 保存wifi信息  """
    wifi_config ={
        'ssid':ssid,
        'password':password
        }
    with open('./wifiInfo.json','w',encoding='utf-8') as f:
        f.write(json.dumps(wifi_config))

def getWifiInfo():
    ''' 获取保存的wifi信息   '''
    if 'wifiInfo.json' in os.listdir('./'):
        with open('./wifiInfo.json','r',encoding='utf-8') as f:
            return json.loads(f.read())
    else:
        None



def inet_pton(ip_str:str):
    '''convert ip address from string to bytes'''
    ip_bytes = b''
    ip_segs = ip_str.split('.')

    for seg in ip_segs:
        ip_bytes += int(seg).to_bytes(1, 'little')

    return ip_bytes

def send_ack(local_ip, local_mac):
    '''sent ack_done event to phone'''
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    data = smartconfig.info()[3].to_bytes(1, 'little') + local_mac
    port = 10000 # airkiss port

    if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH:
        data += inet_pton(local_ip)
        port = 18266 # esptouch port

    print(
f"""- sending ack:
    type: {'esptouch' if smartconfig.info()[2] == smartconfig.TYPE_ESPTOUCH else 'airkiss'}
    port: {port}
    data: {data}
    length: {len(data)}
"""
    )

    for _ in range(20):
        time.sleep_ms(100)
        try:
            udp.sendto(data, ('255.255.255.255', port))
        except OSError:
            pass

    print('- ack was sent')


def smartConfig():
    print('- start smartconfig...')
    smartconfig.start()

    print('- waiting for success...')

    while not smartconfig.done():
        time.sleep_ms(500)

    print('- got smartconfig info')
    ssid, password, sc_type, token = smartconfig.info()
    print(smartconfig.info())
    return [ssid, password, sc_type, token]


def wlan():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    wifiInfo = getWifiInfo()
    if not wifiInfo:
        ssids = smartConfig()
        ssid = ssids[0]
        password = ssids[1]
        saveWifiInfo(ssid=ssid,password=password)
    else:
        ssid = wifiInfo['ssid']
        password =  wifiInfo['password']

    try:
        print('- connecting to wifi...')
        station.connect(ssid, password)
    except:
        ssids = smartConfig()
        ssid = ssids[0]
        password = ssids[1]
        saveWifiInfo(ssid=ssid,password=password)

    while not station.isconnected():
        time.sleep_ms(500)
    print('- wifi connected')

    while station.ifconfig()[0] == '0.0.0.0':
        time.sleep_ms(500)
    print('- got ip')
    print(station.ifconfig())

    send_ack(station.ifconfig()[0], station.config('mac'))


    
if __name__ == "__main__":
    wlan()

```

