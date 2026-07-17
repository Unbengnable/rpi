import RPi.GPIO as GPIO
import time
from smbus2 import SMBus

# --- 根据你的 i2cdetect 扫描结果修改地址 ---
# 源文件提到显示位通常映射在 0x34-0x37 [1]
DIGIT_ADDRS = [0x34, 0x35, 0x36, 0x37]  

# 0-9 段码表 (共阴极) [4]
SEG_MAP = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    'OFF': 0x00
}

def main():
    bus = SMBus(1)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    try:
        print("正在使用硬件 I2C (地址 0x34-0x37) 显示数字...")
        
        # 准备显示内容：1 2 3 4
        display_data = ['1', '2', '3', '4']
        
        while True:
            for i in range(4):
                # 直接向对应的位地址写入段码 [3]
                bus.write_byte(DIGIT_ADDRS[i], SEG_MAP[display_data[i]])
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n清理并退出...")
        for addr in DIGIT_ADDRS:
            bus.write_byte(addr, 0x00) # 关灯 [5]
        bus.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()