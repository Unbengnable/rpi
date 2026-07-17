"""
sonar_display.py — 超声波测距 + TM1650 数码管实时显示距离

接线:
  超声波 VCC  -> 引脚 4  (5V)
  超声波 GND  -> 引脚 6  (GND)
  超声波 Trig -> 引脚 12 (GPIO 18)
  超声波 Echo -> 引脚 16 (GPIO 23)

  数码管 VCC  -> 引脚 4  (5V)
  数码管 GND  -> 引脚 6  (GND)
  数码管 SDA  -> 引脚 3  (I2C1 SDA)
  数码管 SCL  -> 引脚 5  (I2C1 SCL)

来源: 综合 i2c.py (显示) + sonar.py (测距)
"""
import RPi.GPIO as GPIO
import time
from smbus2 import SMBus

# ---- 引脚 ----
TRIG = 12
ECHO = 16

# ---- TM1650 I2C 地址 ----
DIGITS = [0x34, 0x35, 0x36, 0x37]

# ---- 段码（含 'c' 用于厘米标记）----
SEGMENT = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, '-': 0x40, 'c': 0x58, 'E': 0x79, 'r': 0x50,
}


def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)


def get_distance():
    """测距 (cm)，超时/失败返回 -1"""
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    t_timeout = time.time() + 0.05
    while GPIO.input(ECHO) == GPIO.LOW:
        if time.time() > t_timeout:
            return -1

    t_start = time.time()

    t_timeout = time.time() + 0.05
    while GPIO.input(ECHO) == GPIO.HIGH:
        if time.time() > t_timeout:
            return -1

    t_end = time.time()
    return (t_end - t_start) * 34000 / 2


def show(bus, s):
    """在数码管上显示 4 个字符"""
    for i in range(4):
        bus.write_byte(DIGITS[i], SEGMENT.get(s[i], 0x00))


def off(bus):
    for addr in DIGITS:
        bus.write_byte(addr, 0x00)


if __name__ == '__main__':
    init()
    bus = SMBus(1)

    print("超声波测距 + 数码管显示 (Ctrl+C 退出)")
    print("数码管显示格式: 距离值 + 'c' (厘米)\n")

    try:
        while True:
            dist = get_distance()

            if dist < 0:
                show(bus, " Err")
            elif dist > 999:
                show(bus, "999c")
            else:
                cm = int(round(dist))
                show(bus, f"{cm:>3d}c")  # 右对齐 + c: e.g. "  5c", " 15c"

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n清理...")
        off(bus)
        bus.close()
        GPIO.cleanup()
        print("已退出。")
