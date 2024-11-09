# import machine
from lib.easyota import EasyOTA
from lib.easynetwork import Client

# 连接网络
# client = Client()
# client.connect('xuqianfeng', '00000000')
# while not client.isconnected():
#     pass
# print("IP Address: ", client.ifconfig()[0])
from lib.wifi import wlan
wlan()



