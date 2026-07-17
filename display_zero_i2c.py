"""
display_zero_i2c.py — TM1650 数码管显示 "0000"（I2C 模式，对照 i2c.py 修正）

接线:
  VCC -> 引脚 4  (5V)
  GND -> 引脚 6  (GND)
  SDA -> 引脚 3  (I2C1 SDA)
  SCL -> 引脚 5  (I2C1 SCL)
"""
import RPi.GPIO as GPIO
import time
from smbus2 import SMBus

DIGITS = [0x34, 0x35, 0x36, 0x37]

SEGMENT = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00,
}


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    bus = SMBus(1)

    print("数码管应显示: 0000  (Ctrl+C 退出)")

    try:
        while True:
            for i in range(4):
                bus.write_byte(DIGITS[i], SEGMENT['0'])
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n清理...")
        for addr in DIGITS:
            bus.write_byte(addr, 0x00)
        bus.close()
        GPIO.cleanup()
        print("已退出。")


if __name__ == '__main__':
    main()
