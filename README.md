# 树莓派 GPIO 硬件编程 — "一生一芯" v24.07 课程实践

本仓库记录了基于树莓派（Raspberry Pi）的嵌入式 GPIO 硬件编程学习过程，涵盖超声波测距、TM1650 四位数码管显示、LED 灯带控制等实验。配套教材为《Pithon Billingual》（中英双语 Python 硬件编程教材）。

---

## 目录

- [1. 硬件环境总览](#1-硬件环境总览)
- [2. 树莓派引脚速查](#2-树莓派引脚速查)
- [3. 外设接线规范](#3-外设接线规范)
  - [3.1 TM1650 四位数码管](#31-tm1650-四位数码管)
  - [3.2 HC-SR04 超声波测距模块](#32-hc-sr04-超声波测距模块)
  - [3.3 WS2812 LED 灯带](#33-ws2812-led-灯带)
  - [3.4 单颗 LED 双引脚控制](#34-单颗-led-双引脚控制)
- [4. Python 库与 API 调用](#4-python-库与-api-调用)
  - [4.1 RPi.GPIO](#41-rpigpio)
  - [4.2 TM1650 位绑定驱动](#42-tm1650-位绑定驱动)
  - [4.3 smbus2 硬件 I2C](#43-smbus2-硬件-i2c)
  - [4.4 rpi_ws281x LED 灯带库](#44-rpi_ws281x-led-灯带库)
- [5. 示例代码索引](#5-示例代码索引)
- [6. SFTP 同步：本地 ↔ 树莓派](#6-sftp-同步本地--树莓派)
- [7. BusyBox 精简 Linux 操作教程](#7-busybox-精简-linux-操作教程)
- [8. 错误记录与教训](#8-错误记录与教训)
- [9. 参考资源](#9-参考资源)

---

## 1. 硬件环境总览

| 项目 | 详情 |
|:---|:---|
| **开发板** | Raspberry Pi（40Pin GPIO 接口） |
| **操作系统** | Buildroot 构建的精简嵌入式 Linux |
| **Shell** | BusyBox（命令极度精简） |
| **Python 版本** | Python 3.8.2（执行命令：`python3`） |
| **GPIO 库** | `RPi.GPIO` 0.7.1（手动编译安装） |
| **代码部署** | Windows 宿主机通过 SFTP 传输到 `/root/projects/` |
| **编程模式** | **GPIO.BOARD**（物理引脚编号，非 BCM 编号） |

> ⚠️ **重要：必须使用 BOARD 模式（物理引脚号）**，不要使用 BCM 模式。本仓库所有代码均遵循此约定。

---

## 2. 树莓派引脚速查

以下为 40Pin 树莓派 GPIO 引脚图（参考 [pinout.xyz](https://pinout.xyz/)）：

```
左侧（奇数引脚）                          右侧（偶数引脚）
引脚1  3.3V DC Power                      引脚2  5V DC Power
引脚3  GPIO 2  (I2C1 SDA)                 引脚4  5V DC Power
引脚5  GPIO 3  (I2C1 SCL)                 引脚6  GND
引脚7  GPIO 4  (GPCLK0)                   引脚8  GPIO 14 (UART0 TX)
引脚9  GND                                引脚10 GPIO 15 (UART0 RX)
引脚11 GPIO 17                            引脚12 GPIO 18 (PCM CLK)
引脚13 GPIO 27                            引脚14 GND
引脚15 GPIO 22                            引脚16 GPIO 23
引脚17 3.3V DC Power                      引脚18 GPIO 24
引脚19 GPIO 10 (SPI0 MOSI)                引脚20 GND
引脚21 GPIO 9  (SPI0 MISO)                引脚22 GPIO 25
引脚23 GPIO 11 (SPI0 SCLK)                引脚24 GPIO 8  (SPI0 CE0)
引脚25 GND                                引脚26 GPIO 7  (SPI0 CE1)
引脚27 GPIO 0  (EEPROM SDA)               引脚28 GPIO 1  (EEPROM SCL)
引脚29 GPIO 5                             引脚30 GND
引脚31 GPIO 6                             引脚32 GPIO 12 (PWM0)
引脚33 GPIO 13 (PWM1)                     引脚34 GND
引脚35 GPIO 19 (PCM FS)                   引脚36 GPIO 16
引脚37 GPIO 26                            引脚38 GPIO 20 (PCM DIN)
引脚39 GND                                引脚40 GPIO 21 (PCM DOUT)
```

**关键引脚记忆：**
- **电源**：引脚 1/17（3.3V）、引脚 2/4（5V）
- **I2C1**：引脚 3（SDA）、引脚 5（SCL）
- **UART**：引脚 8（TX）、引脚 10（RX）
- **SPI0**：引脚 19（MOSI）、21（MISO）、23（SCLK）、24（CE0）
- **PWM0**：引脚 12（GPIO 18）、引脚 32（GPIO 12）

---

## 3. 外设接线规范

### 3.1 TM1650 四位数码管

TM1650 是一款 I2C 协议的 4 位 7 段数码管驱动芯片。本课程使用两种驱动方式：**GPIO 位绑定（Bit-Banging）** 和 **硬件 I2C（smbus2）**。

#### 接线表（BOARD 模式）

| 数码管模块引脚 | 树莓派物理引脚 | 说明 |
|:---|:---|:---|
| VCC | **引脚 4**（5V） | 5V 电源供电 |
| GND | **引脚 6** | 系统公共接地 |
| SDA | **引脚 3**（GPIO 2 / I2C1 SDA） | 数据传输线 |
| SCL | **引脚 5**（GPIO 3 / I2C1 SCL） | 时钟信号线 |

> ⚠️ **注意**：早期尝试过用引脚 1（3.3V）供电，见 [第 8 节的错误记录](#8-错误记录与教训)。

#### TM1650 关键寄存器地址

| 寄存器 | 位绑定地址 | I2C 7位地址（地址右移1位） | 说明 |
|:---|:---|:---|:---|
| 控制寄存器（亮度/开关） | `0x48` | `0x24` | 亮度 0~7 级，bit 0: 显示开关 |
| 第1位段码（最左） | `0x68` | `0x34` | 7 段数码管段码数据 |
| 第2位段码 | `0x6A` | `0x35` | 同上 |
| 第3位段码 | `0x6C` | `0x36` | 同上 |
| 第4位段码（最右） | `0x6E` | `0x37` | 同上 |

#### 7 段数码管字模（共阴极）

```
 '0': 0x3F    '1': 0x06    '2': 0x5B    '3': 0x4F    '4': 0x66
 '5': 0x6D    '6': 0x7D    '7': 0x07    '8': 0x7F    '9': 0x6F
 ' ': 0x00    '-': 0x40    'c': 0x58    'E': 0x79    'r': 0x50
```

> 字模中的 `c`（0x58）用于显示厘米单位，`E` 和 `r`（0x79 + 0x50）用于错误提示 "Err"。

#### 控制命令说明

发送给控制寄存器 `0x48` 的格式：`0x30 | brightness`（亮度 0~7），再加 bit 0 控制开关。

- `0x31`：开显示 + 亮度等级 3
- `0x37`：开显示 + 最大亮度 7

---

### 3.2 HC-SR04 超声波测距模块

#### 接线表（BOARD 模式）

| 超声波模块引脚 | 树莓派物理引脚 | 说明 |
|:---|:---|:---|
| VCC | **引脚 4**（5V） | HC-SR04 需要 5V 供电 |
| GND | **引脚 6** 或任意 GND | 系统公共接地 |
| Trig | **引脚 12**（GPIO 18） | 触发信号（树莓派输出） |
| Echo | **引脚 16**（GPIO 23） | 回响信号（树莓派输入） |

#### 工作原理

1. 树莓派向 Trig 引脚发送 ≥10μs 的高电平脉冲
2. HC-SR04 模块自动发送 8 个 40kHz 超声波脉冲
3. 模块将 Echo 引脚拉高，持续时间 = 超声波往返时间
4. 距离 = (高电平持续时间 × 340m/s) ÷ 2

#### 关键时序

```
Trig:    ──────┐     ┌──────┐     ┌────────────
               └─────┘      └─────┘
                     ≥10μs
                     
Echo:    ────────────┐         ┌────────────────
                     └─────────┘
                     ← 脉宽 ∝ 距离 →
```

#### 典型代码片段

```python
import RPi.GPIO as GPIO
import time

TRIG = 12   # 物理引脚 12
ECHO = 16   # 物理引脚 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 发送触发脉冲
GPIO.output(TRIG, GPIO.HIGH)
time.sleep(0.00001)     # 10μs
GPIO.output(TRIG, GPIO.LOW)

# 等待 Echo 变高（带超时保护）
t_timeout = time.time() + 0.05
while GPIO.input(ECHO) == GPIO.LOW:
    if time.time() > t_timeout:
        return -1          # 超时，模块无响应

# 测量高电平时间
t_start = time.time()
t_timeout = time.time() + 0.05
while GPIO.input(ECHO) == GPIO.HIGH:
    if time.time() > t_timeout:
        return -1          # 信号异常超时

t_end = time.time()
distance = (t_end - t_start) * 34000 / 2   # 单位：厘米
```

> ⚠️ **超时保护非常重要**：如果超声波模块未连接或损坏，Echo 引脚会一直保持低电平/高电平，没有超时保护会导致程序永久卡死。

---

### 3.3 WS2812 LED 灯带

#### 接线表

| LED 灯带引脚 | 树莓派物理引脚 | 说明 |
|:---|:---|:---|
| VCC（红线） | **引脚 2 或 4**（5V） | ⚠️ 需要外部 5V 电源，灯珠多时勿从树莓派取电 |
| GND（白线） | **引脚 6**（GND） | 需与树莓派共地 |
| DIN（绿线） | **引脚 12**（GPIO 18） | 数据输入，GPIO 18 支持硬件 PWM |

#### 关键参数

```python
from rpi_ws281x import PixelStrip, Color

LED_COUNT      = 16      # LED 数量（根据实际灯带修改）
LED_PIN        = 18      # GPIO 18（物理引脚 12），支持硬件 PWM
LED_FREQ_HZ    = 800000  # WS2812 信号频率 800kHz
LED_DMA        = 10      # DMA 通道
LED_BRIGHTNESS = 255     # 亮度 0~255
LED_INVERT     = False   # 信号不反转（经 NPN 三极管驱动时设为 True）
LED_CHANNEL    = 0       # PWM 通道

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                   LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# 设置颜色并刷新
strip.setPixelColor(0, Color(255, 0, 0))  # 第1颗LED设为红色
strip.show()                               # 刷新到灯带
```

> ⚠️ **功耗警告**：单颗 WS2812 全白最大电流约 60mA。16 颗全白 ≈ 1A，远超树莓派 5V 引脚供电能力。多颗灯珠时务必使用外部 5V 电源，并确保与树莓派共地。

---

### 3.4 单颗 LED 双引脚控制

本项目使用"双引脚电平对冲"方式控制 LED，比传统的"一引脚+串联电阻"更安全。

#### 接线表

| LED 引脚 | 树莓派物理引脚 | 说明 |
|:---|:---|:---|
| 正极（长脚） | **引脚 11**（GPIO 17） | LED 阳极 |
| 负极（短脚） | **引脚 13**（GPIO 27） | LED 阴极 |

#### 原理

**同时输出低电平 → 0V 电势差 → 灯灭 + 零电流（绝对安全）**
**阳极高 + 阴极低 → 3.3V 电势差 → 灯亮**

这种方式比传统的"阳极接 3.3V + 阴极接 GPIO"更安全，因为关机时两端皆为低电平，不会有漏电流。

---

## 4. Python 库与 API 调用

### 4.1 RPi.GPIO

树莓派 GPIO 操作的核心库，版本 0.7.1。

```python
import RPi.GPIO as GPIO

# --- 初始化（必须最先调用）---
GPIO.setmode(GPIO.BOARD)      # 使用物理引脚编号
GPIO.setwarnings(False)       # 关闭引脚占用警告

# --- 引脚配置 ---
GPIO.setup(pin, GPIO.OUT)     # 设为输出模式
GPIO.setup(pin, GPIO.IN)      # 设为输入模式
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)   # 输入 + 上拉电阻

# --- 数字读写 ---
GPIO.output(pin, GPIO.HIGH)   # 输出高电平（3.3V）
GPIO.output(pin, GPIO.LOW)    # 输出低电平（0V）
value = GPIO.input(pin)       # 读取引脚电平（0 或 1）

# --- 事件回调（中断方式）---
GPIO.add_event_detect(pin, GPIO.RISING, callback=my_func, bouncetime=200)
GPIO.add_event_callback(pin, another_func)  # 追加第二个回调

# --- 清理（退出时必须调用）---
GPIO.cleanup()
```

### 4.2 TM1650 位绑定驱动

当硬件 I2C 不可用或需要精确控制时，使用位绑定（Bit-Banging）方式模拟 I2C 时序。

```python
SDA = 3   # 物理引脚 3
SCL = 5   # 物理引脚 5

# I2C 起始信号：SCL 高时 SDA 下降沿
def write_start():
    GPIO.output(SDA, GPIO.HIGH)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SDA, GPIO.LOW)
    time.sleep(0.001)
    GPIO.output(SCL, GPIO.LOW)

# I2C 停止信号：SCL 高时 SDA 上升沿
def write_stop():
    GPIO.output(SDA, GPIO.LOW)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SDA, GPIO.HIGH)
    time.sleep(0.001)

# 写入一个字节（高位在前，每 bit 后切换一次 SCL）
def write_byte(byte):
    for _ in range(8):
        GPIO.output(SDA, GPIO.HIGH if (byte & 0x80) else GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.LOW)
        byte <<= 1
    # 读取 ACK（不检查返回值，仅走时序）
    GPIO.setup(SDA, GPIO.IN)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SCL, GPIO.LOW)
    GPIO.setup(SDA, GPIO.OUT)

# 发送命令
def send_command(addr, data):
    write_start()
    write_byte(addr)
    write_byte(data)
    write_stop()
```

> ⚠️ **时序关键**：`time.sleep(0.001)`（1ms）不能更短，否则 TM1650 无法正确识别信号。TM1650 是低速 I2C 设备，标准 100kHz 时序反而会造成通信失败。

### 4.3 smbus2 硬件 I2C

使用硬件 I2C 总线驱动 TM1650 时，需要 smbus2 库。

```python
from smbus2 import SMBus

bus = SMBus(1)   # 打开 /dev/i2c-1

# 写入数据：S Addr+W A Data A P
bus.write_byte(0x34, 0x3F)  # 在第1位显示 '0'

bus.close()
```

> **重要地址转换**：位绑定地址 → smbus2 地址 = 右移 1 位
>
> `0x68 >> 1 = 0x34`、`0x48 >> 1 = 0x24`

### 4.4 rpi_ws281x LED 灯带库

#### 安装

```bash
# 在树莓派上手动编译安装（Buildroot 系统无 pip）
# 参考：https://github.com/jgarff/rpi_ws281x
```

#### 常用 API

```python
from rpi_ws281x import PixelStrip, Color

strip = PixelStrip(count, pin, freq, dma, invert, brightness, channel)
strip.begin()                          # 初始化库
strip.setPixelColor(i, Color(r,g,b))   # 设置第 i 颗 LED 颜色
strip.setPixelColor(i, Color(0,0,0))   # 熄灭第 i 颗 LED
strip.show()                           # 将所有设置刷新到灯带
strip.numPixels()                      # 返回 LED 总数
```

#### 颜色公式

```python
Color(red, green, blue)  # 内部实现: (red << 16) | (green << 8) | blue
```

---

## 5. 示例代码索引

本仓库提供以下可直接运行的示例脚本：

### 数码管（TM1650）

| 文件 | 说明 | 驱动方式 |
|:---|:---|:---|
| [test.py](test.py) | 显示固定数字 "0854" | 位绑定（Bit-Banging） |
| [display_zero_i2c.py](display_zero_i2c.py) | 显示 "0000" | smbus2 硬件 I2C |
| [i2c.py](i2c.py) | 显示 "1234" | smbus2 硬件 I2C |
| [high.py](high.py) | 读取 GPIO 26 状态，接地显示 "LOW"，断开清空 | 位绑定 + 输入检测 |

### 超声波测距（HC-SR04）

| 文件 | 说明 | 附加功能 |
|:---|:---|:---|
| [sonar_test.py](sonar_test.py) | 基础测距测试 | 无 |
| [sonar.py](sonar.py) | 超声波 + LED 倒车雷达 | LED 随距离变频闪烁 |
| [sonar_display.py](sonar_display.py) | 超声波 + 数码管实时显示距离 | smbus2 I2C 数码管 |
| [dis.py](dis.py) | 超声波 + 数码管联动（**最终完整版**） | 位绑定数码管 + 多重重试 |

### LED 灯带 / 单颗 LED

| 文件 | 说明 | 控制方式 |
|:---|:---|:---|
| [blink.py](blink.py) | 双引脚电平对冲让 LED 闪烁（0.5s 周期） | 双引脚 |
| [blink_ground.py](blink_ground.py) | 引脚 37 接地触发 LED 闪烁 | 双引脚 + 输入检测 |
| [led.py](led.py) | WS2812 LED 灯带全部点亮 | rpi_ws281x |

### 其他

| 文件 | 说明 |
|:---|:---|
| [回调.py](回调.py) | RPi.GPIO 事件回调示例（`add_event_detect` + `add_event_callback`） |

> 📄 PDF 教材 `Pithon_billingual.pdf`（3.8MB）因体积过大不上传 GitHub，请从课程官方渠道获取。

---

## 6. SFTP 同步：本地 ↔ 树莓派

### 6.0 树莓派网络连接

本环境通过 USB 直连树莓派，树莓派默认 IP：`192.168.88.1`。

树莓派端需要运行 SSH 服务（Buildroot 需启用 Dropbear SSH）。

### 6.1 VS Code SFTP 插件配置

配置文件：[.vscode/sftp.json](.vscode/sftp.json)

```json
{
    "name": "RaspberryPi-Buildroot",
    "host": "192.168.88.1",
    "protocol": "sftp",
    "port": 22,
    "username": "root",
    "password": "123456",
    "remotePath": "/root/projects",
    "uploadOnSave": true,
    "ignore": [
        "**/.vscode/**",
        "**/.git/**"
    ]
}
```

**功能说明：**

| 特性 | 说明 |
|:---|:---|
| `uploadOnSave: true` | 每次 Ctrl+S 保存时自动上传到树莓派 |
| `remotePath` | 树莓派上的目标目录（自动创建） |
| `ignore` | 排除本地目录，不上传 VS Code 和 Git 元数据 |

### 6.2 手动 SFTP 命令（备选）

当 VS Code SFTP 插件不可用时，可在 Git Bash 终端使用命令行：

```bash
# 上传单个文件
sftp root@192.168.88.1
> put test.py /root/projects/test.py
> quit

# 批量上传（使用 scp）
scp *.py root@192.168.88.1:/root/projects/
```

### 6.3 工作流程

```
┌──────────────┐     SFTP (保存即上传)     ┌────────────────┐
│  Windows 宿主机  │ ◄──────────────────────► │  树莓派 Buildroot │
│  VS Code 编辑   │     IP: 192.168.88.1     │  /root/projects/ │
│  .py 源码       │     Port: 22             │  python3 执行     │
└──────────────┘                            └────────────────┘
```

**日常开发流程：**
1. 在 Windows 上使用 VS Code 编写 Python 脚本
2. Ctrl+S 保存 → 自动通过 SFTP 上传到树莓派 `/root/projects/`
3. 在树莓派终端（串口/SSH）执行：`python3 /root/projects/脚本名.py`
4. Ctrl+C 退出程序 → 脚本自动清理 GPIO 并安全退出

---

## 7. BusyBox 精简 Linux 操作教程

本树莓派使用 Buildroot + BusyBox，**不是** Raspberry Pi OS（Debian）。很多常规 Linux 命令在此系统上不可用。

### 7.1 与标准 Linux 的关键差异

| 功能 | 标准 Linux | BusyBox/Buildroot |
|:---|:---|:---|
| 包管理器 | `apt`、`yum`、`pip` | ❌ 无（所有软件需手动编译安装或交叉编译） |
| 文件编辑 | `vim`、`nano`、`emacs` | ❌ 无编辑器（需在宿主机编辑后上传） |
| 在线帮助 | `man`、`info`、`--help` | ❌ 无 `man`，部分命令支持 `--help` |
| 文件传输 | `curl`、`wget` | ⚠️ 可能不可用（Buildroot 需手动启用） |
| 网络诊断 | `ping`、`ifconfig`、`ip` | ⚠️ `ping` 通常可用，`ifconfig` → 用 `ip addr` |
| 文本处理 | `awk`、`sed`、`grep` | ✅ BusyBox 内置（功能精简） |
| 文件操作 | `cp`、`mv`、`rm`、`ls`、`cat` | ✅ BusyBox 内置 |

### 7.2 BusyBox 常用命令速查

```bash
# --- 文件操作 ---
ls              # 列出目录（不支持 ls -la 的某些选项）
ls -l           # 长格式列表
cat file.txt    # 显示文件内容
cp a b          # 复制文件
mv a b          # 移动/重命名文件
rm file.txt     # 删除文件
rm -r dir/      # 递归删除目录
mkdir dir       # 创建目录
touch file.txt  # 创建空文件

# --- 系统信息 ---
uname -a        # 系统信息
free            # 内存使用（可能不可用）
df -h           # 磁盘空间
ps              # 进程列表（BusyBox 版功能精简）

# --- 网络 ---
ping 192.168.88.1     # 测试连通性
ip addr                # 查看 IP 地址（替代 ifconfig）
ip link set eth0 up    # 启用网络接口

# --- I2C 设备检测（需手动加载 i2c_dev 模块）---
i2cdetect -y 1         # 扫描 I2C-1 总线上的设备

# --- Python ---
python3 script.py      # 运行 Python 3.8.2 脚本
python3 -c "print('hi')"  # 执行单行 Python 代码

# --- 进程控制 ---
Ctrl+C                 # 发送 SIGINT，触发 KeyboardInterrupt
kill PID               # 终止指定进程
```

### 7.3 如何应对"命令不存在"

遇到 `xxx: not found` 时，没有 `apt install` 可用。解决方案：

1. **大部分需求** → 在宿主机编写 Python 脚本，上传后运行
2. **Python 库** → 在 Buildroot 配置阶段加入对应包，重新编译系统
3. **I2C 设备** → Load kernel module: `modprobe i2c_dev`
4. **GPIO 权限** → 以 `root` 用户运行（`/dev/gpiomem` 权限问题）

### 7.4 安全退出 Python 脚本

所有脚本必须响应 `Ctrl+C`（SIGINT），否则 GPIO 引脚状态会残留，可能导致：
- 引脚下次使用时被占用，无法初始化
- LED/外设持续通电烧毁
- GPIO 电平异常

**正确模板：**

```python
import RPi.GPIO as GPIO

try:
    # ... 你的主程序 ...
    while True:
        pass  # 主循环
except KeyboardInterrupt:
    print("\n正在清理并退出...")
    # 关闭所有外设
    GPIO.cleanup()
    print("已安全退出。")
```

---

## 8. 错误记录与教训

> 🎓 **核心教训：仔细阅读课件 PDF，不要自己瞎猜！尤其是 Vibe Coding 时，AI 生成的外设驱动细节往往与实际硬件不兼容。**

### 错误 1：TM1650 I2C 地址用错

**错误现象**：使用 smbus2 向 `0x34-0x37` 写段码，数码管不显示。

**错误代码**：
```python
DIGITS = [0x34, 0x35, 0x36, 0x37]   # 直接用 I2C 7位地址
```

**根因**：TM1650 的位绑定地址（`0x68-0x6E`）和 I2C 7位地址（`0x34-0x37`）不同。前者是 8 位命令字（含 R/W 位），后者是 7 位从机地址（不含 R/W 位）。位绑定时用 `0x68`，smbus2 时应使用 `0x34`（`0x68 >> 1`）。两种方式都能工作，但不能混用。

**教训**：先理解芯片数据手册，确认驱动方式后再写代码。可以先用 `i2cdetect -y 1` 扫描总线上的设备地址。

相关文件：[old/display_zero_i2c.py](old/display_zero_i2c.py)

---

### 错误 2：控制寄存器地址写错

**错误现象**：段码写入成功但数码管不亮。

**错误代码**：
```python
CTRL = 0x24   # 把控制寄存器地址当成了 0x24
bus.write_byte(CTRL, 0x31)
```

**根因**：位绑定模式下控制寄存器是 `0x48`，转换为 smbus2 I2C 地址应为 `0x24`（`0x48 >> 1`）。但早期代码直接照搬了错误的地址，没有正确转换。应使用 `0x48`（位绑定）或 `0x24`（I2C），不能混用驱动模式和地址。

**教训**：位绑定地址和 I2C 地址是不同的地址空间。位绑定使用 8 位地址，I2C 使用 7 位地址。在两种驱动方式间切换时，所有地址都需要重新计算。

相关文件：[old/display_zero_smbus.py](old/display_zero_smbus.py)

---

### 错误 3：供电电压选择混乱（3.3V vs 5V）

**错误现象**：数码管时亮时不亮，通信不稳定。

**分析**：
- 树莓派 GPIO 输出高电平 = 3.3V
- TM1650 用 5V 供电时，芯片 VIH（输入高电平最小电压）约 3.5V，3.3V 处于临界区
- CMOS 输入级长时间处于临界区会产生直通电流，轻则通信不稳，重则烧毁芯片

**初始尝试**：改用 3.3V 供电（引脚 1），让 3.3V = VDD，电平完全匹配。创建了 [old/display_zero_3v3.py](old/display_zero_3v3.py)、[old/display_zero_gpio.py](old/display_zero_gpio.py)。

**最终方案**：经过实际测试，5V 供电（引脚 4）+ 位绑定驱动可以稳定工作。关键是**时序要慢**——用 1ms 延时而不是标准 I2C 的 μs 级延时。

**教训**：
1. 电平匹配是硬件通信的基础，仔细看芯片数据手册的电气特性
2. 不要动不动就怀疑供电问题——先检查软件时序和接线
3. 实际测试比理论分析更可靠

---

### 错误 4：过度依赖 AI 猜测硬件细节

**错误现象**：AI（Vibe Coding）生成的 TM1650 驱动代码使用了标准 I2C 100kHz 时序，导致通信失败。AI 还虚构了不存在的 smbus2 API 用法。

**根因**：TM1650 并非标准 I2C 从设备——它只需要微控制器单向写入数据，不需要读取。而且 TM1650 对时钟速度非常敏感，过快的时钟（标准 I2C 的 100kHz）会导致数据识别失败。

**解决办法**：查阅《Pithon Billingual》教材（PDF 第 3.6 节）中的 TM1650 章节，严格按照教材时序编写位绑定代码，使用 `time.sleep(0.001)`（1ms）作为每个 bit 的延时。

**教训**：
> 🔴 **永远不要完全相信 AI 生成的外设驱动代码！**  
> AI 不认识你的具体硬件，它只会生成"看起来合理"的代码。务必查阅课件 PDF 和芯片数据手册。

---

### 错误 5：`sonar_display.py` 中 smbus2 与 GPIO 混合使用

**错误现象**：[sonar_display.py](sonar_display.py) 使用 `smbus2` 驱动数码管 + `RPi.GPIO` 驱动超声波，两个库各自管理引脚，可能产生资源冲突。

**改进方案**：[dis.py](dis.py) 统一使用 `RPi.GPIO` 位绑定驱动所有外设，避免库冲突。

**教训**：在同一程序中尽量统一 GPIO 管理方式，避免多个库同时操作 GPIO 引脚。

---

### 错误 6：`_pdf_extract.py` 与 `re.py` 文件名冲突

**错误现象**：导入 Python 标准库 `re` 时，由于当前目录下存在 `test.py` 等与标准库同名的文件，导致 shadow import。

**教训**：不要在项目根目录放置与 Python 标准库同名的 `.py` 文件。本项目中的 `test.py` 虽未与标准库同名，但需注意避免 `re.py`、`json.py`、`io.py` 等命名。

---

## 9. 参考资源

| 资源 | 链接 / 路径 |
|:---|:---|
| 树莓派 GPIO 引脚图 | [pinout.xyz](https://pinout.xyz/)（本地副本：[Raspberry Pi GPIO Pinout.html](Raspberry%20Pi%20GPIO%20Pinout.html)） |
| 课程主页 | "_一生一芯_ v24.07 课程主页 _ 官方文档.html"（本地副本） |
| 教材 | `Pithon_billingual.pdf`（中英双语，3.8MB，不上传 GitHub） |
| RPi.GPIO 文档 | https://sourceforge.net/p/raspberry-gpio-python/wiki/ |
| TM1650 数据手册 | 课程教材第 3.6 节 |
| HC-SR04 数据手册 | 课程教材超声波章节 |
| rpi_ws281x 库 | https://github.com/jgarff/rpi_ws281x |
| GitHub 仓库 | https://github.com/Unbengnable/rpi |

---

> 📝 **最后更新**：2026-07-17  
> ✍️ **维护者**：Unbengnable  
> 📋 **许可证**：MIT License
