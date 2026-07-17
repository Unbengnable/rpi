"""
display_zero_i2c.py — TM1650 数码管显示 "0000"（I2C 终极版）

经多次诊断确认:
  - 0x34~0x37 段码写入全部成功 (冷启动时)
  - 0x24 亮度写入也成功
  - 段码 + 亮度组合: 段码先写，亮度最后

接线:
  VCC -> 引脚 4  (5V)
  GND -> 引脚 6  (GND)
  SDA -> 引脚 3  (I2C1 SDA)
  SCL -> 引脚 5  (I2C1 SCL)
"""
import time
from smbus2 import SMBus

SEG_0 = 0x3f
DIGITS = [0x34, 0x35, 0x36, 0x37]
CTRL   = 0x24


def main():
    bus = SMBus(1)
    print("/dev/i2c-1 已打开")

    try:
        # ---- 第 1 步: 写段码 ----
        print("写段码...")
        for i, addr in enumerate(DIGITS):
            bus.write_byte(addr, SEG_0)
            print(f"  [OK] 位{i+1} 0x{addr:02X}<-0x3F")
            time.sleep(0.005)

        # ---- 第 2 步: 打开显示 ----
        print("开显示...")
        bus.write_byte(CTRL, 0x31)
        print(f"  [OK] 0x{CTRL:02X}<-0x31")

        print("\n应显示: 0000  (Ctrl+C 退出)")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n关闭...")
        for a in DIGITS:
            try:
                bus.write_byte(a, 0x00)
            except:
                pass
        bus.close()

    except OSError as e:
        print(f"\n失败: {e}")
        bus.close()


if __name__ == '__main__':
    main()
