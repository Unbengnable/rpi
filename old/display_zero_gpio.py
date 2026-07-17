"""
display_zero_gpio.py — TM1650 四位数码管显示 "0000"（GPIO 位绑定 + 3.3V 供电）

接线（3.3V 供电，消除电平不匹配问题）：
  VCC -> 引脚 1  (3.3V)
  GND -> 引脚 9  (GND)
  SDA -> 引脚 3  (GPIO 2)
  SCL -> 引脚 5  (GPIO 3)

驱动：基于 test.py 的 TM1650 位绑定协议，改用 3.3V 供电确保 GPIO 高电平 = VDD。
"""
import RPi.GPIO as GPIO
import time

# ---- 引脚定义（BOARD 物理编号）----
SDA = 3
SCL = 5

# ---- 共阴极 7 段字模 ----
SEGMENT = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, '-': 0x40,
}

# ---- TM1650 寄存器地址 ----
CTRL_ADDR  = 0x48                       # 亮度/开关控制
DIGIT_ADDR = [0x68, 0x6a, 0x6c, 0x6e]   # 第 1~4 位段码


def init_gpio():
    """初始化 GPIO"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(SCL, GPIO.OUT)
    GPIO.setup(SDA, GPIO.OUT)
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)


def write_start():
    """I2C 起始信号"""
    GPIO.output(SDA, GPIO.HIGH)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SDA, GPIO.LOW)
    time.sleep(0.001)
    GPIO.output(SCL, GPIO.LOW)


def write_stop():
    """I2C 停止信号"""
    GPIO.output(SDA, GPIO.LOW)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SDA, GPIO.HIGH)
    time.sleep(0.001)


def write_byte(byte):
    """向 TM1650 写入一个字节（高位在前）"""
    for _ in range(8):
        GPIO.output(SDA, GPIO.HIGH if (byte & 0x80) else GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.LOW)
        byte <<= 1

    # 读取 ACK（不检查值，只走时序）
    GPIO.setup(SDA, GPIO.IN)
    GPIO.output(SCL, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(SCL, GPIO.LOW)
    GPIO.setup(SDA, GPIO.OUT)


def send_command(addr, data):
    """发送 TM1650 命令: 起始 -> 命令 -> 数据 -> 停止"""
    write_start()
    write_byte(addr)
    write_byte(data)
    write_stop()


def display_on(brightness=7):
    """打开显示并设置亮度（0~7，3.3V 供电建议用最大值 7）"""
    send_command(CTRL_ADDR, 0x30 | (brightness & 0x07))


def show_string(s):
    """在四位数码管上显示字符串"""
    s = str(s).rjust(4)[:4]
    for i, ch in enumerate(s):
        send_command(DIGIT_ADDR[i], SEGMENT.get(ch, 0x00))


def display_off():
    """关闭所有位"""
    for addr in DIGIT_ADDR:
        send_command(addr, 0x00)


if __name__ == '__main__':
    try:
        init_gpio()

        # 3.3V 供电时用最大亮度
        display_on(7)
        print("亮度已设置（等级 7，最大）")

        # 显示 0000
        show_string("0000")
        print("数码管应显示: 0000")
        print("按 Ctrl+C 退出...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在关闭显示并清理 GPIO...")
        display_off()
        GPIO.cleanup()
        print("已安全退出。")
