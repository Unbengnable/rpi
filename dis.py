import RPi.GPIO as GPIO
import time

# ================= 硬件引脚定义 (BOARD 模式) =================
# 1. 数码管引脚
SDA = 3
SCL = 5

# 2. 超声波传感器引脚
TRIG_PIN = 12
ECHO_PIN = 16

# ================= 数码管字模与显存地址 =================
# 扩充字模字典，加入 'c' 字符用作厘米单位 (c 的共阴极字模为 0x58)
NUM_DIGITS = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, '-': 0x40, 'c': 0x58, 'E': 0x79, 'r': 0x50  # Er 用于错误提示
}
DIGIT_ADDR = [0x68, 0x6a, 0x6c, 0x6e]

def init_hardware():
    """初始化所有 GPIO"""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # 1. 初始化数码管引脚
    GPIO.setup(SCL, GPIO.OUT)
    GPIO.setup(SDA, GPIO.OUT)
    GPIO.output(SCL, GPIO.HIGH)
    GPIO.output(SDA, GPIO.HIGH)
    
    # 2. 初始化超声波引脚
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    
    # 给传感器一点稳定时间
    time.sleep(0.5)

# ================= TM1650 驱动底层时序 =================
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
    """在数码管上显示 4 位字符串"""
    s = s.rjust(4)[:4]
    for i in range(4):
        char = s[i]
        seg_data = NUM_DIGITS.get(char, 0x00)
        send_command(DIGIT_ADDR[i], seg_data)

def clear_display():
    for addr in DIGIT_ADDR:
        send_command(addr, 0x00)

# ================= 超声波测距核心逻辑 =================
def get_distance():
    """获取一次距离，带超时保护和多重容错机制"""
    # 1. 先确保 TRIG 处于低电平稳定状态
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.0001)

    # 2. 发送 15μs 触发脉冲（用忙等待保证精度，不依赖 time.sleep）
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    # 忙等待约 15μs：在树莓派上，空循环约 50-100 次对应 15μs
    for _ in range(100):
        pass
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # 3. 等待模块启动测距（模块需要约 200μs 处理触发信号）
    time.sleep(0.0005)

    # 4. 等待 ECHO 变为高电平（超声波开始发射）
    t_timeout = time.time() + 0.04  # 40ms 足够，对应约 7m 测距范围
    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        if time.time() > t_timeout:
            return -1  # 模块未响应
        time.sleep(0.00001)  # 避免 CPU 空转

    # 5. 记录高电平开始，等待 ECHO 变为低电平
    t_start = time.time()
    t_timeout = t_start + 0.04  # 高电平超过 40ms 视为异常
    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        if time.time() > t_timeout:
            return -1  # 信号超时异常
        time.sleep(0.00001)

    t_end = time.time()
    duration = t_end - t_start
    distance = (duration * 34000) / 2
    return distance

# ================= 主循环逻辑 =================
if __name__ == '__main__':
    try:
        init_hardware()
        # 初始化数码管：开显示 + 3级亮度
        send_command(0x48, 0x31)
        
        print("联动系统启动！正在实时测量并将距离渲染至数码管...")
        print("提示: 可以在控制台按下 Ctrl + C 安全退出。")
        
        while True:
            raw_dist = get_distance()

            # 失败时重试最多 3 次，避免单次偶发失败就显示 Err
            retry_count = 0
            while raw_dist < 0 and retry_count < 3:
                time.sleep(0.05)
                raw_dist = get_distance()
                retry_count += 1

            if raw_dist < 0 or raw_dist > 400:
                # 超出测距范围 (HC-SR04 最小 ~2cm，最大约 4 米)
                show_string("Err")
                print("测距失败：超出范围或传感器未响应（已重试 %d 次）" % retry_count)
                time.sleep(0.3)  # 失败后延长等待，让模块恢复
            else:
                # 将距离取整
                dist_cm = int(round(raw_dist))

                # 格式化输出：如果距离为 15，格式化为 " 15c"（c 代表 cm）
                # 限制最大显示为 999 厘米，防止溢出 4 位数码管
                if dist_cm < 2:
                    display_str = "  0c"  # 低于最小量程显示 0
                elif dist_cm > 999:
                    display_str = "999c"
                else:
                    display_str = f"{dist_cm}c"

                # 渲染到数码管
                show_string(display_str)
                print(f"实时距离: {raw_dist:.1f} cm -> 数码管显示: '{display_str}'")

                # 正常测量间隔 200ms
                time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n捕获到退出信号 (Ctrl+C)，正在安全关闭显示并释放引脚...")
        clear_display()
        GPIO.cleanup()
        print("安全退出成功！")