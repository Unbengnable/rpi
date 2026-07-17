"""
sonar_test.py — 用超声波传感器测试 TM1650 所用的 GPIO 引脚

接线：
  超声波 VCC  -> 引脚 1  (3.3V) 或 引脚 4 (5V，看传感器规格)
  超声波 GND  -> 引脚 9  (GND)
  超声波 Trig -> 引脚 7  (GPIO 4)   ← TM1650 SDA 用的引脚
  超声波 Echo -> 引脚 11 (GPIO 17)  ← TM1650 SCL 用的引脚

如果正常输出距离 → 引脚 7 和 11 是好的 → 问题确认在 TM1650 模块。
"""
import RPi.GPIO as GPIO
import time

TRIG = 7    # 引脚 7,  GPIO 4
ECHO = 11   # 引脚 11, GPIO 17


def get_distance():
    """获取距离 (cm)，超时返回 -1。与 dis.py 一致。"""
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    t_timeout = time.time() + 0.1
    t_start = time.time()
    while GPIO.input(ECHO) == GPIO.LOW:
        t_start = time.time()
        if t_start > t_timeout:
            return -1

    t_timeout = time.time() + 0.1
    t_end = time.time()
    while GPIO.input(ECHO) == GPIO.HIGH:
        t_end = time.time()
        if t_end > t_timeout:
            return -1

    return (t_end - t_start) * 34000 / 2


if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(TRIG, GPIO.OUT)
        GPIO.setup(ECHO, GPIO.IN)
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(0.5)

        print(f"超声波 Trig=引脚{TRIG}, Echo=引脚{ECHO}")
        print("移动物体靠近传感器，Ctrl+C 退出:\n")

        while True:
            d = get_distance()
            if d < 0:
                print(f"  [FAIL] 超时 — 引脚{TRIG}或{ECHO}可能损坏/接线错误")
            else:
                print(f"  [OK] {d:.1f} cm — 引脚{TRIG}和{ECHO}正常")
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n测试结束。")
        GPIO.cleanup()
