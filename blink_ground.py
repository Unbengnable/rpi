import RPi.GPIO as GPIO
import time

# 严格遵循引脚图规范，采用物理引脚编号模式 (BOARD)
PIN_ANODE = 11    # LED 正极对应的物理引脚 (GPIO 17)
PIN_CATHODE = 13  # LED 负极对应的物理引脚 (GPIO 27)
INPUT_PIN = 37    # 触发控制输入：物理引脚 37 (GPIO 26)

def init_hardware():
    """初始化所有 GPIO 引脚"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # 1. 初始化 LED 驱动引脚
    GPIO.setup(PIN_ANODE, GPIO.OUT)
    GPIO.setup(PIN_CATHODE, GPIO.OUT)
    # 初始状态：两端同为低电平（0V），无电势差，灯灭且零电流
    GPIO.output(PIN_ANODE, GPIO.LOW)
    GPIO.output(PIN_CATHODE, GPIO.LOW)
    
    # 2. 初始化输入控制引脚（物理引脚 37）
    # 启用内部上拉电阻：平时悬空时稳定在工作电压（高电平1），安全接地时变为低电平0
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def led_on():
    """让 LED 点亮：一端高电平，一端低电平"""
    GPIO.output(PIN_ANODE, GPIO.HIGH)
    GPIO.output(PIN_CATHODE, GPIO.LOW)

def led_off():
    """让 LED 熄灭：两端同时为低电平，绝对安全零电流"""
    GPIO.output(PIN_ANODE, GPIO.LOW)
    GPIO.output(PIN_CATHODE, GPIO.LOW)

if __name__ == '__main__':
    try:
        init_hardware()
        print("系统启动成功！开始安全监听物理引脚 37（GPIO 26）的接地状态...")
        print("提示: 可以在控制台按下 Ctrl + C 安全退出。")
        
        last_state = None
        
        while True:
            # 读取物理引脚 37 的状态
            # GPIO.LOW (0) 代表导线接地了；GPIO.HIGH (1) 代表导线悬空断开
            current_input = GPIO.input(INPUT_PIN)
            
            if current_input == GPIO.LOW:
                # 检测到接地 -> 让 LED 闪烁
                if last_state != GPIO.LOW:
                    print("状态变更: 物理引脚 37 已接地 -> LED 开始闪烁")
                    last_state = GPIO.LOW
                
                # 执行一次闪烁周期
                led_on()
                time.sleep(0.2)
                led_off()
                time.sleep(0.2)
                
            else:
                # 导线悬空/断开 -> 保持 LED 彻底熄灭
                if last_state != GPIO.HIGH:
                    led_off()
                    print("状态变更: 物理引脚 37 已断开 -> LED 保持熄灭")
                    last_state = GPIO.HIGH
                
                # 悬空状态下，保持小幅度的轮询延时，降低 CPU 占用
                time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n捕获到退出信号，正在安全释放硬件...")
        led_off()
        GPIO.cleanup()
        print("GPIO 资源已安全释放，程序安全退出。")