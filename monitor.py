import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import re
import time
import csv
import os

# --- 配置参数（CSV 时间戳使用本机系统时间，而非 STM32 RTC） ---
import sys

# 从命令行参数读取串口号（如: monitor.py COM5），默认为 COM9
SERIAL_PORT = sys.argv[1] if len(sys.argv) > 1 else 'COM9'
BAUD_RATE = 115200    # 必须与单片机代码中的波特率一致
MAX_POINTS = 50       # 横轴显示的最近数据点数量

# 自动定位项目根目录下的 date/ 文件夹
if getattr(sys, 'frozen', False):
    # PyInstaller 打包的 exe：以 exe 所在目录为起点
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 直接运行 .py 脚本：以脚本所在目录为起点
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 向上搜索项目根目录（以 Project1.ioc 或 .mxproject 为标志）
# 如果搜不到（如 exe 放在桌面运行），回退到本项目固定路径
_KNOWN_PROJECT = r'D:\cubemx first example\Project1 - 副本'

def _find_project_root(start_dir):
    d = os.path.abspath(start_dir)
    for _ in range(5):  # 最多向上搜 5 层
        if os.path.exists(os.path.join(d, 'Project1.ioc')) or \
           os.path.exists(os.path.join(d, '.mxproject')):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    # 兜底：使用已知的项目路径
    if os.path.exists(_KNOWN_PROJECT):
        return _KNOWN_PROJECT
    return start_dir  # 都找不到就回退到起点

PROJECT_ROOT = _find_project_root(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'date')
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, 'sensor_data.csv')

# 初始化 CSV 文件头
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Temperature(C)', 'Humidity(%)', 'Light(%)'])

# 数据缓存
times = deque(maxlen=MAX_POINTS)
temp_data = deque(maxlen=MAX_POINTS)
humi_data = deque(maxlen=MAX_POINTS)
light_data = deque(maxlen=MAX_POINTS)

# 正则表达式解析传感器数值（忽略 STM32 串口号中的 RTC 时间戳，CSV 时间由本机提供）
data_pattern = re.compile(r'T:(\d+)C, H:(\d+)%, L:(\d+)%')

# 初始化串口
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    import ctypes
    ctypes.windll.user32.MessageBoxW(0,
        f"无法打开 {SERIAL_PORT}\n\n原因: {e}\n\n请检查串口是否被占用，或拔插 USB 串口线重试。\n也可使用命令行指定端口: monitor.exe COM5",
        "串口连接失败", 0x10)
    sys.exit(1)

# 设置绘图界面
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
fig.canvas.manager.set_window_title('STM32 传感器实时监控')

def init():
    for ax, label, color, y_range in zip([ax1, ax2, ax3], 
                                         ['Temp (C)', 'Humi (%)', 'Light (%)'],
                                         ['r', 'g', 'b'],
                                         [(0, 50), (0, 100), (0, 100)]):
        ax.set_ylabel(label)
        ax.set_ylim(y_range)
        ax.grid(True, linestyle='--', alpha=0.6)
    return []

def update(frame):
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                match = data_pattern.search(line)
                if match:
                    t, h, l = map(int, match.groups())
                    
                    # 时间戳取自本机系统时间（PC时钟），不依赖 STM32 RTC
                    current_time = time.strftime('%H:%M:%S')
                    
                    times.append(current_time)
                    temp_data.append(t)
                    humi_data.append(h)
                    light_data.append(l)
                    
                    # 保存数据到 CSV（时间戳使用本机系统时间）
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([time.strftime('%Y-%m-%d %H:%M:%S'), t, h, l])
                    
                    # 清除并重绘
                    ax1.clear()
                    ax2.clear()
                    ax3.clear()
                    
                    init()
                    
                    ax1.plot(list(times), list(temp_data), 'r-o', markersize=4)
                    ax2.plot(list(times), list(humi_data), 'g-o', markersize=4)
                    ax3.plot(list(times), list(light_data), 'b-o', markersize=4)
                    
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    
        except Exception as e:
            print(f"解析错误: {e}")

    return []

ani = FuncAnimation(fig, update, init_func=init, interval=100, cache_frame_data=False)
plt.show()

ser.close()
