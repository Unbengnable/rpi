import time
from rpi_ws281x import PixelStrip, Color
# 如果您的环境使用的是文档中的旧版库接口，也可以使用:
# from neopixel import Adafruit_NeoPixel as PixelStrip, Color

# ==================== LED 灯带参数配置 ====================
LED_COUNT      = 16      # 灯带上的 LED 总数量（根据实际情况修改）
LED_PIN        = 18      # GPIO 引脚号（GPIO 18，对应物理引脚 Pin 12）
LED_FREQ_HZ    = 800000  # 信号频率 (常规 WS2812 为 800kHz)
LED_DMA        = 10      # 用于生成信号的 DMA 通道
LED_BRIGHTNESS = 255     # 亮度等级 (0-255)
LED_INVERT     = False   # 信号反转 (使用 NPN 三极管驱动时设为 True)
LED_CHANNEL    = 0       # PWM 通道 (GPIO 18 对应 PWM 通道 0)

# Color(red, green, blue) 颜色转换函数 (24位颜色：R<<16 | G<<8 | B)
def color_rgb(r, g, b):
    return Color(r, g, b)

if __name__ == '__main__':
    # 初始化 PixelStrip 对象
    strip = PixelStrip(
        LED_COUNT, 
        LED_PIN, 
        LED_FREQ_HZ, 
        LED_DMA, 
        LED_INVERT, 
        LED_BRIGHTNESS, 
        LED_CHANNEL
    )
    
    # 初始化库
    strip.begin()

    print("正在点亮灯带...")

    # 设置颜色：RGB(200, 100, 150)
    # 按照文档公式：(200 << 16) | (100 << 8) | 150
    target_color = Color(200, 100, 150)

    # 点亮前 4 颗 LED (索引为 0, 1, 2, 3)
    for i in range(16):
        strip.setPixelColor(i, target_color)

    # 将设置刷新发送到灯带
    strip.show()

    print("已成功点亮前 16 颗 LED！按 Ctrl+C 退出。")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 退出时熄灭所有灯珠
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        print("\n灯带已关闭。")