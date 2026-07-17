import RPi.GPIO as GPIO
import time

# 严格采用物理引脚编号模式 (BOARD)
SDA = 3          # 对应引脚图中的物理引脚 3 (GPIO 2)
SCL = 5          # 对应引脚图中的物理引脚 5 (GPIO 3)
INPUT_PIN = 37   # 对应引脚图中的 GPIO 26 (物理引脚 37)

# 数码管字模与地址定义
NUM_DIGITS = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    'L': 0x38, 'O': 0x3f, 'W': 0x3e, ' ': 0x00
}
DIGIT_ADDR = [0x68, 0x6a, 0x6c, 0x6e]

def init_hardware():
    """初始化所有外设引脚"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # 1. 初始化数码管 I2C 引脚
    GPIO.setup(SCL, GPIO.OUT)
    GPIO.setup(SDA, GPIO.OUT)
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)
    
    # 2. 初始化输入引脚（GPIO 26 / 物理引脚 37）
    # 启用内部上拉电阻：平时悬空时为高电平(1)，导线接地(GND)时为低电平(0)
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- TM1650 驱动底层时序 ---
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

def clear_display():
    for addr in DIGIT_ADDR:
        send_command(addr, 0x00)

# --- 主程序逻辑 ---
if __name__ == '__main__':
    try:
        init_hardware()
        # 初始化数码管配置命令：开显示 + 3级亮度
        send_command(0x48, 0x31)
        
        print("系统启动成功！开始监听 GPIO 26（物理引脚 37）的接地状态...")
        
        # 记录上一次的状态，避免重复刷新屏幕导致闪烁
        last_state = None
        
        while True:
            # 读取引脚状态：GPIO.LOW (0) 代表接地，GPIO.HIGH (1) 代表悬空/断开
            current_input = GPIO.input(INPUT_PIN)
            
            if current_input == GPIO.LOW:
                # 检测到接地
                if last_state != GPIO.LOW:
                    show_string("LOW")               # 数码管显示 LOW
                    print("状态变更: GPIO 26 已接地 -> 屏幕显示 'LOW'")
                    last_state = GPIO.LOW
            else:
                # 悬空/断开状态
                if last_state != GPIO.HIGH:
                    clear_display()                  # 清空屏幕内容
                    print("状态变更: GPIO 26 已断开 -> 屏幕清空")
                    last_state = GPIO.HIGH
            
            # 轮询微调延时（50毫秒），兼顾响应速度与低 CPU 占用率
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n正在清理硬件环境并退出...")
        clear_display()
        GPIO.cleanup()
        print("安全退出。")