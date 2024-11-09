# ESP32开机自动运行程序

在MicroPython的运行环境中，`boot.py`和`main.py`是两个关键文件，它们在ESP32启动时的执行顺序和作用不同。

## 1. `boot.py`

#### [作用]

`boot.py`是MicroPython固件在设备启动时首先执行的脚本，类似于系统初始化脚本。其主要作用包括：

1. **初始化设置**：进行设备的基本初始化设置，例如配置引脚、电源管理、时钟设置等。
2. **网络配置**：配置WiFi或其他网络连接，设置静态IP地址等。
3. **外设初始化**：初始化外设，如I2C、SPI、UART等。
4. **日志设置**：设置调试信息输出方式，是否启用REPL（Read-Eval-Print Loop）等。

#### 示例

以下是一个简单的`boot.py`示例，它配置了WiFi连接：

```python
import network

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())

connect_to_wifi('your_SSID', 'your_PASSWORD')复制Error复制成功...
```

## 2. `main.py`

#### 作用

`main.py`是MicroPython固件在设备启动时第二个执行的脚本，通常用于编写用户的主要应用逻辑。其主要作用包括：

1. **应用逻辑**：执行主要功能代码，如传感器数据采集、控制输出设备、数据处理等。
2. **任务调度**：管理和调度不同任务的执行。
3. **事件处理**：响应用户输入或外部事件（如定时器中断、网络请求等）。

#### 示例
以下是一个简单的`main.py`示例，它控制LED闪烁：

```python
import time
import machine

led = machine.Pin(2, machine.Pin.OUT)

while True:
    led.value(not led.value())
    time.sleep(1)复制Error复制成功...
```

## 3. 区别总结

- **执行顺序**：`boot.py`在ESP32上电或重启时首先执行，然后执行`main.py`。
- **作用不同**：`boot.py`主要用于系统初始化设置和配置，而`main.py`用于编写具体的应用逻辑。
- **重要性**：`boot.py`的配置影响整个系统的运行环境，而`main.py`则是实现设备具体功能的核心脚本。

通过正确地使用这两个文件，你可以有效地管理ESP32的启动流程和应用逻辑，确保设备在启动时按照预期进行初始化和执行。