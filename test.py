import RPi.GPIO as GPIO
import time

# 采用物理引脚编号模式 (BOARD)
SDA = 3
SCL = 5

# 数字 0-9 的共阴极字模数据
NUM_DIGITS = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, '-': 0x40
}

# 4个数字位对应的寄存器控制地址
DIGIT_ADDR = [0x68, 0x6a, 0x6c, 0x6e]

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
        if (byte & 0x80):
            GPIO.output(SDA, GPIO.HIGH)
        else:
            GPIO.output(SDA, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(SCL, GPIO.LOW)
        byte <<= 1
    
    # 模拟接收应答信号
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
        char = s[i]
        seg_data = NUM_DIGITS.get(char, 0x00)
        send_command(DIGIT_ADDR[i], seg_data)

if __name__ == '__main__':
    try:
        init_gpio()
        send_command(0x48, 0x31)
        
        #0854
        show_string("0854")
        print("屏幕已成功显示：0854")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在清理 GPIO 并退出...")
        for addr in DIGIT_ADDR:
            send_command(addr, 0x00)
        GPIO.cleanup()