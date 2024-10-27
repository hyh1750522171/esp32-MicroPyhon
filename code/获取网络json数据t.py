import urequests
import time


while True:
    response = urequests.get('http://192.168.31.155:8000/data.json')
    data = response.json()
    time.sleep(1)
    if data['id'] == 1:
        print('exploded, booommmmm......')
        time.sleep(10)
    else: 
        print('safety')

