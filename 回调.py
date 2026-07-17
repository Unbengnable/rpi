import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
channel = 23
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 任务 A
def action_A(channel):
    print("【任务A】记录日志：引脚 %s 被触发了" % channel)

# 任务 B
def action_B(channel):
    print("【任务B】控制硬件：点亮一盏 LED 灯")

# 1. 必须先用 detect 开启监听（顺便绑定任务 A，防抖时间200ms）
GPIO.add_event_detect(channel, GPIO.RISING, callback=action_A, bouncetime=200)

# 2. 监听开启后，用 callback 追加任务 B
# 注意：add_event_callback 不需要传入 GPIO.RISING 这样的边缘类型，因为它会继承 detect 的配置
GPIO.add_event_callback(channel, action_B)

# 当引脚 23 触发上升沿时，action_A 和 action_B 会在后台线程里排队依次执行。