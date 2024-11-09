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

