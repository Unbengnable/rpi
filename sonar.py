import RPi.GPIO as GPIO
import time

# ================= 引脚定义 (BOARD 模式) =================
# 1. 超声波引脚
TRIG_PIN = 12
ECHO_PIN = 16

# 2. LED 双引脚控制
PIN_ANODE = 11    # LED 正极
PIN_CATHODE = 13  # LED 负极

def init_hardware():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # 初始化超声波引脚
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    
    # 初始化 LED 引脚
    GPIO.setup(PIN_ANODE, GPIO.OUT)
    GPIO.setup(PIN_CATHODE, GPIO.OUT)
    led_off() # 初始熄灭
    
    time.sleep(0.5)  # 等待硬件稳定

def led_on():
    """点亮 LED"""
    GPIO.output(PIN_ANODE, GPIO.HIGH)
    GPIO.output(PIN_CATHODE, GPIO.LOW)

def led_off():
    """熄灭 LED"""
    GPIO.output(PIN_ANODE, GPIO.LOW)
    GPIO.output(PIN_CATHODE, GPIO.LOW)

def get_distance():
    """获取一次距离，并带超时保护"""
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)  # 10us 脉冲
    GPIO.output(TRIG_PIN, GPIO.LOW)
    
    t_timeout = time.time() + 0.05
    t_start = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        t_start = time.time()
        if t_start > t_timeout:
            return -1
            
    t_timeout = time.time() + 0.05
    t_end = time.time()
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        t_end = time.time()
        if t_end > t_timeout:
            return -1
            
    duration = t_end - t_start
    distance = (duration * 34000) / 2
    return distance

if __name__ == '__main__':
    try:
        init_hardware()
        print("“LED 倒车雷达”系统启动！")
        print("请在传感器前移动手掌，观察 LED 闪烁频率的变化...")
        print("提示: 按 Ctrl + C 安全退出...")
        
        while True:
            dist = get_distance()
            
            if dist < 0 or dist > 150:
                # 距离过远（大于1.5米）或检测失败，LED 保持熄灭
                led_off()
                print(f"当前距离: {dist:.1f} cm -> 安全范围，LED 熄灭")
                time.sleep(0.3)
                
            elif dist <= 10:
                # 极近距离（10cm以内）：极度危险，LED 彻底常亮
                led_on()
                print(f"当前距离: {dist:.1f} cm -> 【极度危险】LED 常亮！")
                time.sleep(0.1)
                
            elif dist <= 30:
                # 较近距离（10cm - 30cm）：紧急，急促暴闪
                print(f"当前距离: {dist:.1f} cm -> 【紧急】LED 急促闪烁")
                led_on()
                time.sleep(0.05)
                led_off()
                time.sleep(0.05)
                
            elif dist <= 60:
                # 中等距离（30cm - 60cm）：警告，普通闪烁
                print(f"当前距离: {dist:.1f} cm -> 【警告】LED 均匀闪烁")
                led_on()
                time.sleep(0.15)
                led_off()
                time.sleep(0.15)
                
            else:
                # 较远距离（60cm - 150cm）：安全提示，慢速闪烁
                print(f"当前距离: {dist:.1f} cm -> 【提示】LED 慢速闪烁")
                led_on()
                time.sleep(0.4)
                led_off()
                time.sleep(0.4)

    except KeyboardInterrupt:
        print("\n正在安全释放 GPIO 并退出...")
        led_off()
        GPIO.cleanup()
        print("安全退出。")