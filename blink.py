import RPi.GPIO as GPIO
import time

# 严格遵循引脚图规范，采用物理引脚编号模式 (BOARD)
PIN_ANODE = 11    # LED 正极对应的物理引脚 (GPIO 17)
PIN_CATHODE = 13  # LED 负极对应的物理引脚 (GPIO 27)

def init_hardware():
    """初始化 GPIO 状态"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # 将两端引脚都设置为输出模式
    GPIO.setup(PIN_ANODE, GPIO.OUT)
    GPIO.setup(PIN_CATHODE, GPIO.OUT)
    
    # 初始状态：两端同时输出低电平（0V），无电势差，灯灭，绝对安全
    GPIO.output(PIN_ANODE, GPIO.LOW)
    GPIO.output(PIN_CATHODE, GPIO.LOW)

if __name__ == '__main__':
    try:
        init_hardware()
        print("双引脚电平对冲闪烁实验开始...")
        print("提示: 可以在控制台按下 Ctrl + C 安全退出。")
        
        while True:
            # === 状态 1：一端高，一端低 -> 产生 3.3V 电势差 -> 灯亮 ===
            GPIO.output(PIN_ANODE, GPIO.HIGH)
            GPIO.output(PIN_CATHODE, GPIO.LOW)
            print("LED 状态: 亮 (一高一低)")
            time.sleep(0.5)
            
            # === 状态 2：两端同为低电平 -> 0V 电势差 -> 灯灭且零电流 ===
            GPIO.output(PIN_ANODE, GPIO.LOW)
            GPIO.output(PIN_CATHODE, GPIO.LOW)
            print("LED 状态: 灭 (双端皆低)")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n捕获到退出信号 (Ctrl+C)，正在安全善后...")
        # 退出前确保两端电平彻底归零
        GPIO.output(PIN_ANODE, GPIO.LOW)
        GPIO.output(PIN_CATHODE, GPIO.LOW)
        # 释放引脚
        GPIO.cleanup()
        print("GPIO 资源已安全释放。")