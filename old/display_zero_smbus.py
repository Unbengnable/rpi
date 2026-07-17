"""
display_zero_smbus.py — 使用 smbus2 驱动 TM1650 四位数码管显示 "0000"

接线（与 history.md 一致，走硬件 I2C）：
  VCC -> 引脚 4  (5V)
  GND -> 引脚 6  (GND)
  SDA -> 引脚 3  (I2C1 SDA)
  SCL -> 引脚 5  (I2C1 SCL)

参考：Pithon 教材第 3.6 节（PDF 第 143-145 页）— smbus2 I2C 编程
"""
import time

# ---- 7 段共阴极字模 ----
SEGMENT = {
    '0': 0x3f, '1': 0x06, '2': 0x5b, '3': 0x4f, '4': 0x66,
    '5': 0x6d, '6': 0x7d, '7': 0x07, '8': 0x7f, '9': 0x6f,
    ' ': 0x00, '-': 0x40,
}

# ---- TM1650 硬件 I2C 地址映射 ----
# bit-banging 命令字右移 1 位 = I2C 7 位从机地址
ADDR_CTRL  = 0x24    # 0x48 >> 1  (亮度/开关控制)
ADDR_DIGIT = [        # 四位数码管段码地址
    0x34,             # 0x68 >> 1  (第 1 位，左)
    0x35,             # 0x6a >> 1  (第 2 位)
    0x36,             # 0x6c >> 1  (第 3 位)
    0x37,             # 0x6e >> 1  (第 4 位，右)
]

# 亮度等级: 0x30~0x37 (0 最暗 / 7 最亮)
BRIGHTNESS = 0x31


def main():
    # 按课件第 143 页方式导入 smbus2 并打开 I2C 总线
    try:
        from smbus2 import SMBus
        bus = SMBus(1)
        print("smbus2: /dev/i2c-1 已打开")
    except ImportError:
        print("错误: 未安装 smbus2，请执行: pip install smbus2")
        return
    except FileNotFoundError:
        print("错误: /dev/i2c-1 不存在")
        print("  请加载内核模块: modprobe i2c_dev")
        return
    except OSError as e:
        print(f"错误: 无法访问 I2C 总线: {e}")
        return

    try:
        # ---- 第 1 步: 打开显示 + 设置亮度 ----
        # smbus2 write_byte: S Addr+W A Data A P
        # 对应 TM1650: S 0x48 A 0x31 A P
        bus.write_byte(ADDR_CTRL, BRIGHTNESS)
        print(f"已发送亮度命令: write_byte(0x{ADDR_CTRL:02x}, 0x{BRIGHTNESS:02x})")

        # ---- 第 2 步: 写入四个位的段码 "0000" ----
        for i, addr in enumerate(ADDR_DIGIT):
            bus.write_byte(addr, SEGMENT['0'])
            print(f"第 {i + 1} 位: write_byte(0x{addr:02x}, 0x{SEGMENT['0']:02x})")

        print("\n数码管应显示: 0000")
        print("按 Ctrl+C 退出...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n正在关闭显示...")
        for addr in ADDR_DIGIT:
            try:
                bus.write_byte(addr, 0x00)
            except Exception:
                pass
        bus.close()
        print("已安全退出。")

    except OSError as e:
        print(f"\nI2C 通信失败: {e}")
        bus.close()


if __name__ == '__main__':
    main()
