micropython 自己编译固件有几个好处

- 只加入自己需要的模块降低硬件资源占用
- `.py` 文件可以修改中中间码，并烧录到固件内部，
- - 可以方便量产
- - 可一定程度保护代码
- - 更加省略了编译过程节省内存

我这里 只记录 添加 `smartconfig` 的方法，并以`S2 mini`为例，其他`esp32` 同理。
简中网络上，几乎没有相关资料，有一些资料也是错的或无法使用。所以这里单独记录分享一下。 你可以直接下载 我编译好的
https://github.com/joyanhui/file.leiyanhui.com/blob/main/esp32/

# 准备

- `linux`系统，我这里是ubuntu22.04
- 科学工具 因为需要拉 `github`
- 基本的 `linux` 基础

# 环境配置 和 依赖

修改到国内源，这个自己处理

```bash
apt install git wget curl make gcc cmake rsync
# ppa安装pythone 3.11  Ubuntu自带的版本太低
apt install software-properties-common
add-apt-repository ppa:deadsnakes/ppa
apt install python3.11 python-is-python3
# pip3
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py --force-reinstall
pip install mpy-cross-v6
```


# 克隆代码

```bash
mkdir mpy-bin && cd mpy-bin
```


## esp-idf

注意 不同的 `esp32`平台 `micropython`支持的`esp-idf`版本不同，详情参考 https://github.com/micropython/micropython/tree/master/ports/esp32#readme
`linux`小白 一步一步操作，注意里面的警告信息

```bash
git clone -b v4.4.5 --recursive https://github.com/espressif/esp-idf.git esp-idf-v4.4.5
cd esp-idf-v4.4.5/
git checkout v4.4.5
git submodule update --init --recursive
```


处理环境变量

```bash
./install.sh 
source export.sh
```


## micropython

本文基于 `1.20` 版本，如果新版失效，请 直接去下载 https://github.com/micropython/micropython/releases/download/v1.20.0/micropython-1.20.0.zip 不要 `git clone` 最新的



```bash
cd ..
git clone https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross
cd ports/esp32
```

# 测试默认编译`micropython`固件



```bash
make submodules
make  # make BOARD=LOLIN_S2_MINI
```



直接`make`的话 是 `esp32` ，我这里是 `s2` ，并且是 `esp32 s2 mini`开发板 所以添加参数 `BOARD=LOLIN_S2_MINI` 这样就可以编译 了,编译后 会有提示 `./build-XXXX/ firmware.bin` 这个文件是合并后的，可以直接烧到 `esp32` 开发板上了。

## 推送到 nas

我这里推送到`nas`里面，方便其他机器使用

```bash
rsync -avzut --progress  ./build-LOLIN_S2_MINI/firmware.bin    root@10.1.1.200:/mnt/nas/temp/firmware-my.bin 
```


## 烧录

在连接`esp32`的机器上从`nas`复制`bin`文件过来然后下入

```bash
esptool  --port COM3  erase_flash #擦除
esptool --port COM3   --baud 1000000 write_flash -z 0x1000 firmware-my.bin # 写入从nas 拷贝过来的 新固件
```



烧录完成后，重启板，`thonny` 链接上，输入 `help(‘modules’)` 查看模块

# 添加 smartconfig 模块

```bash
cd ~/mpy-bin/micropython/ports/esp32
```


需要两个地方，1是 添加一个`smartconfig.c`文件，2 是修改还 `ports/esp32/main/CMakeLists.txt` 把 `smartconfig.c` 加进去

## CMakeLists.txt

查看 `cat ~/mpy-bin/micropython/ports/esp32/main/CMakeLists.txt` 目前版本`1.20`版本 需要修改的内容在 54-92行 格式如下

```bash
set(MICROPY_SOURCE_PORT
    main.c
    ....
    machine_sdcard.c
    ...
)
```


我们需要在 `machine_sdcard.c` 后面添加一个 `smartconfig.c`，然后在 `machine_sdcard.c`的同目录下 创建一个 `smartconfig.c` (内容查看后文)
修改后的 `CMakeLists.txt` 内容格式如下

```bash
set(MICROPY_SOURCE_PORT
    main.c
    ....
    machine_sdcard.c
    smarconfig.c
    ...
)
```


> 同理，可以在这里删掉不用的模块

## smartconfig.c

```bash
nano ~/mpy-bin/micropython/ports/esp32/machine_sdcard.c
```


内容参考后文。 找

# 重新编译



```bash
make submodules
make BOARD=LOLIN_S2_MINI
```


# 上级测试

新固件烧录后，烧录完成后，重启板，thonny 链接上，输入 `help('modules')` 查看模块 已经有 smarconfig 运行一个 main.py 测试，测试代码参考后文。 启动后，找一个支持smarconfig的手机app或者微信小程序 配网测试 我用的微信小程序`#小程序://一键配网/047fob5XqOB14hk` 复制发送到手机微信，聊天窗口点开即可。配网成功

# 添加自定义py文件

优点：1 保护代码 2 方便量产 内容单独另起一一个文章 [添加自定义py文件到固件](https://dev.leiyanhui.com/mcu/esp32-mpy-code-to-bin)

# 内容

## smartconfig.c

```bash
#include "py/obj.h"
#include "py/runtime.h"

#include <string.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_smartconfig.h"

static EventGroupHandle_t s_wifi_event_group;

static const int ESPTOUCH_DONE_BIT = BIT1;
static const char *TAG = "smartconfig";

static int found_ssid_and_password = false;
static uint8_t ssid[33] = {0};
static uint8_t password[65] = {0};
static uint8_t type = -1;
static uint8_t token = 0;

static void smartconfig_task(void * parm);


static void event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data)
{
    if (event_base == SC_EVENT && event_id == SC_EVENT_SCAN_DONE) {
        ESP_LOGI(TAG, "Scan done");
    } else if (event_base == SC_EVENT && event_id == SC_EVENT_FOUND_CHANNEL) {
        ESP_LOGI(TAG, "Found channel");
    } else if (event_base == SC_EVENT && event_id == SC_EVENT_GOT_SSID_PSWD) {
        ESP_LOGI(TAG, "Got SSID and password");

        smartconfig_event_got_ssid_pswd_t *evt = (smartconfig_event_got_ssid_pswd_t *)event_data;

        memcpy(ssid, evt->ssid, sizeof(evt->ssid));
        memcpy(password, evt->password, sizeof(evt->password));
        type = evt->type;
        token = evt->token;

        ESP_LOGI(TAG, "SSID:%s", ssid);
        ESP_LOGI(TAG, "PASSWORD:%s", password);
        ESP_LOGI(TAG, "TYPE:%d", type);
        ESP_LOGI(TAG, "TOKEN:%d", token);

        found_ssid_and_password = true;

        xEventGroupSetBits(s_wifi_event_group, ESPTOUCH_DONE_BIT);
    }
}

static void initialise_wifi(void)
{
    s_wifi_event_group = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(esp_event_handler_register(SC_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL));

    xTaskCreate(smartconfig_task, "smartconfig_task", 4096, NULL, 3, NULL);
}

static void smartconfig_task(void * parm)
{
    EventBits_t uxBits;
    ESP_ERROR_CHECK(esp_smartconfig_set_type(SC_TYPE_ESPTOUCH_AIRKISS));
    smartconfig_start_config_t cfg = SMARTCONFIG_START_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_smartconfig_start(&cfg));

    while (1) {
        uxBits = xEventGroupWaitBits(s_wifi_event_group, ESPTOUCH_DONE_BIT, true, false, portMAX_DELAY); 
        if(uxBits & ESPTOUCH_DONE_BIT) {
            ESP_LOGI(TAG, "smartconfig over");
            ESP_ERROR_CHECK(esp_smartconfig_stop());
            vTaskDelete(NULL);
        }
    }
}

STATIC mp_obj_t smartconfig_start(void)
{
    initialise_wifi();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(smartconfig_start_obj, smartconfig_start);

STATIC mp_obj_t smartconfig_success(void)
{
    return mp_obj_new_bool(found_ssid_and_password);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(smartconfig_success_obj, smartconfig_success);

STATIC mp_obj_t smartconfig_info(void)
{
    mp_obj_t info[] = {
        mp_obj_new_str((const char *)ssid, strlen((const char *)ssid)),
        mp_obj_new_str((const char *)password, strlen((const char *)password)),
        mp_obj_new_int(type),
        mp_obj_new_int(token)
    };

    return mp_obj_new_tuple(4, info);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(smartconfig_info_obj, smartconfig_info);


STATIC const mp_rom_map_elem_t smartconfig_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_smartconfig)},
    {MP_ROM_QSTR(MP_QSTR_start), MP_ROM_PTR(&smartconfig_start_obj)},
    {MP_ROM_QSTR(MP_QSTR_success), MP_ROM_PTR(&smartconfig_success_obj)},
    {MP_ROM_QSTR(MP_QSTR_info), MP_ROM_PTR(&smartconfig_info_obj)},
    {MP_ROM_QSTR(MP_QSTR_TYPE_UNKNOWN), MP_ROM_INT(-1)},
    {MP_ROM_QSTR(MP_QSTR_TYPE_ESPTOUCH), MP_ROM_INT(SC_TYPE_ESPTOUCH)},
    {MP_ROM_QSTR(MP_QSTR_TYPE_AIRKISS), MP_ROM_INT(SC_TYPE_AIRKISS)},
};

STATIC MP_DEFINE_CONST_DICT(smartconfig_module_globals, smartconfig_module_globals_table);

const mp_obj_module_t smartconfig_user_cmodule = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&smartconfig_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_smartconfig, smartconfig_user_cmodule);

```



## main.py

```bash
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

while not smartconfig.success():
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

```

### 参考链接


* https://dev.leiyanhui.com/mcu/esp32-s2-mpy-smartconfig/
* https://github.com/micropython/micropython/tree/master/ports/esp32 
* https://github.com/Walkline80/MicroPython-SmartConfig-CModule/tree/master
* https://github.com/espressif/esp-idf.git



