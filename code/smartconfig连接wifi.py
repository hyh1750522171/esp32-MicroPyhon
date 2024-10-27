import network
import socket
import smartconfig
import time


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

station = network.WLAN(network.STA_IF)
station.active(True)

print('- start smartconfig...')
smartconfig.start()

print('- waiting for success...')

while not smartconfig.done():
    time.sleep_ms(500)

print('- got smartconfig info')
ssid, password, sc_type, token = smartconfig.info()
print(smartconfig.info())

print('- connecting to wifi...')
station.connect(ssid, password)

while not station.isconnected():
    time.sleep_ms(500)
print('- wifi connected')

while station.ifconfig()[0] == '0.0.0.0':
    time.sleep_ms(500)
print('- got ip')
print(station.ifconfig())

send_ack(station.ifconfig()[0], station.config('mac'))

