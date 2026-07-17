"""
display_zero_3v3.py
TM1650 数码管显示 "0000"（3.3V 供电版）

接线方式（与 5V 版本的唯一区别：VCC 接 3.3V）：
  VCC -> 引脚 1  (3.3V，而非引脚 4 的 5V)
  GND -> 引脚 6  (GND)
  SDA -> 引脚 3  (GPIO 2)
  SCL -> 引脚 5  (GPIO 3)

为什么要改用 3.3V？
  树莓派 GPIO 输出高电平为 3.3V，TM1650 用 5V 供电时，
  3.3V 处于 VIH 临界区（~3.5V），会导致 CMOS 输入级
  反复出现直通电流，长期运行触发闩锁效应烧毁芯片。
  改用 3.3V 供电后，3.3V = VDD，电平完全匹配。
"""
import RPi.GPIO as GPIO
import time

SDA = 3
SCL = 5

# 共阴极 7 段数码管字模
NUM_DIGITS = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, '-': 0x40
}

DIGIT_ADDR = [0x68, 0x6a, 0x6c, 0x6e]  # 从左到右四个位
CTRL_ADDR = 0x48                          # 控制寄存器（亮度/开关）


def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(SCL, GPIO.OUT)
    GPIO.setup(SDA, GPIO.OUT)
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)


def write_start():
    GPIO.output(SDA, GPIO.HIGH)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SDA, GPIO.LOW)
    time.sleep(0.001)
    GPIO.output(SCL, GPIO.LOW)


def write_stop():
    GPIO.output(SDA, GPIO.LOW)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SDA, GPIO.HIGH)
    time.sleep(0.001)


def write_byte(byte):
    for _ in range(8):
        if byte & 0x80:
            GPIO.output(SDA, GPIO.HIGH)
        else:
            GPIO.output(SDA, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.LOW)
        byte <<= 1

    # 读取 ACK
    GPIO.setup(SDA, GPIO.IN)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SCL, GPIO.LOW)
    GPIO.setup(SDA, GPIO.OUT)


def send_command(addr, data):
    write_start()
    write_byte(addr)
    write_byte(data)
    write_stop()


def show_string(s):
    s = s.rjust(4)[:4]
    for i in range(4):
        seg_data = NUM_DIGITS.get(s[i], 0x00)
        send_command(DIGIT_ADDR[i], seg_data)


def display_off():
    for addr in DIGIT_ADDR:
        send_command(addr, 0x00)


if __name__ == '__main__':
    try:
        init_gpio()

        # 3.3V 供电时亮度可能需要调高一点，0x37 = 最大亮度
        send_command(CTRL_ADDR, 0x37)
        show_string("0000")
        print("数码管已显示：0000（3.3V 供电模式）")
        print("按 Ctrl+C 退出...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在关闭显示并清理 GPIO...")
        display_off()
        GPIO.cleanup()
        print("已安全退出。")
