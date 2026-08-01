# STM32 智能环境采集终端

> 基于 STM32F103C8T6 + Python 双端协同的实时环境监测系统

---

## 项目简介

本项目是一个低成本、可扩展的嵌入式环境监测系统：

- **STM32 端**：负责采集环境数据（温湿度、光照），驱动 OLED 本地显示，并通过串口将数据上报 PC。
- **PC 端**：使用 Python 上位机接收串口数据，实时绘制温度 / 湿度 / 光照曲线，并将数据持久化保存到 CSV 文件。

系统适用于家庭环境监测、温室大棚、实验室数据记录等场景。

---

## 硬件平台

| 组件 | 型号 | 接口 | 说明 |
|------|------|------|------|
| 主控芯片 | STM32F103C8T6 | — | Cortex-M3，72MHz，64KB Flash，20KB RAM |
| 温湿度传感器 | DHT11 | PA9 | 单总线协议 |
| 光照传感器 | 5516 光敏电阻 | PA0 | ADC1 模拟采样 |
| OLED 显示屏 | SSD1306 128×64 | PB8/PB9 (I2C1) | 本地实时显示 |
| 串口模块 | CH340 USB-Serial | PB10/PB11 (USART3) | 与 PC 通信 |
| LED 指示灯 | 普通 LED | PA1 | 心跳指示 |

### 系统时钟

- HSE 8MHz 经 PLL ×9 倍频 → SYSCLK 72MHz
- RTC 使用内部 LSI 时钟

---

## 软件架构

```
┌─────────────────────────────────────────────────────────────┐
│                       PC 上位机                              │
│  pyserial 串口读取 → matplotlib 实时绘图 → CSV 数据存档      │
└─────────────────────────────────────────────────────────────┘
                              │ USART3 (115200-8N1)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   STM32F103C8T6 下位机                       │
│                                                              │
│   DHT11 ──┐                                                  │
│   5516  ──┼──→ main.c 主循环 ──→ OLED 显示                  │
│           │                  └──→ USART3 串口输出           │
│   RTC   ──┘                                                  │
└─────────────────────────────────────────────────────────────┘
```

### 主循环流程

1. LED 翻转（PA1）
2. OLED 清屏
3. 读取 DHT11 温湿度数据
4. 读取 5516 光照百分比
5. OLED 填充 4 行显示：LED 状态 / 温度 / 湿度 / 光照
6. `printf` 通过 USART3 输出带 RTC 时间戳的数据
7. OLED 整屏刷新
8. 延时 1 秒，循环执行

### 串口数据格式

```
[2026-07-21 12:25:45] T:28C, H:47%, L:24%
```

### CSV 数据格式

```csv
Time,Temperature(C),Humidity(%),Light(%)
2026-07-21 12:25:45,28,47,24
```

CSV 时间戳使用 **PC 系统时间**，不依赖 STM32 RTC，便于历史数据追溯。

---

## 项目结构

```
Project1/
├── Core/                       # CubeMX 生成的应用代码
│   ├── Inc/                    # 头文件
│   └── Src/                    # 源文件（main.c 入口）
├── Drivers/
│   ├── STM32F1xx_HAL_Driver/   # STM32 HAL 库
│   ├── CMSIS/                  # CMSIS 核心库
│   └── User/                   # 用户自定义驱动
│       ├── Inc/                # led.h, dht11.h, 5516.h, OLED.h, Serial.h
│       └── Src/                # led.c, dht11.c, 5516.c, OLED.c, Serial.c
├── cmake/                      # CMake 工具链配置
├── CMakeLists.txt              # 根 CMake 文件
├── CMakePresets.json           # CMake 预设
├── Project1.ioc                # STM32CubeMX 工程文件
├── monitor.py                  # Python 上位机
├── monitor.spec                # PyInstaller 打包配置
├── 启动监测程序.bat            # 一键启动脚本
├── date/                       # CSV 数据目录
│   └── sensor_data.csv
├── PROJECT_ANALYSIS.md         # 项目分析文档
├── PPT_GENERATION_PROMPT.md    # PPT 生成指令
└── README.md                   # 本文件
```

---

## 快速开始

### 1. 编译 STM32 固件

确保已安装 ARM GCC、CMake、Ninja，然后执行：

```bash
cmake --preset Debug
cmake --build --preset Debug
```

编译产物：`build/Debug/Project1.elf`、`Project1.hex`、`Project1.bin`

### 2. 烧录到 STM32

使用 ST-Link 和 OpenOCD：

```bash
flash.bat
```

### 3. 启动 Python 监控

方式一：双击 `启动监测程序.bat`

方式二：指定串口号

```bash
启动监测程序.bat COM5
```

方式三：打包好的独立程序

```bash
dist/monitor.exe
```

---

## 技术栈

### 嵌入式端

- STM32CubeMX + STM32 HAL 库
- CMake + Ninja + ARM GCC
- OpenOCD + ST-Link（烧录）

### PC 端

- Python 3.12
- pyserial（串口通信）
- matplotlib（实时绘图）
- PyInstaller（打包为 exe）

---

## 项目亮点

- **上下位机协同**：STM32 负责实时采集与显示，Python 负责可视化与存储，职责清晰。
- **全工具链自动化**：一键安装、编译、烧录、启动。
- **TIM2 硬件微秒延时**：为 DHT11 单总线时序提供高精度延时。
- **双平台 printf 兼容**：同时支持 GCC `_write` 和 ARMCC `fputc`。
- **OLED 地址自动检测**：适配 0x78 / 0x7A 两种常见 I2C 地址。
- **双重时间戳体系**：RTC 用于本地显示，PC 时间用于 CSV 存档。
- **高资源余量**：Flash 占用 40%，RAM 占用 16%，扩展空间充足。

---

## 后续扩展方向

- 增加 Wi-Fi / ESP8266 模块，实现云端数据上传
- 增加蜂鸣器、继电器，实现阈值报警与联动控制
- 增加更多传感器（气压、PM2.5、土壤湿度）
- Python 端增加 Web 仪表盘
- 低功耗优化，支持电池供电

---

## 许可证

本项目基于 STMicroelectronics HAL 许可证，仅供学习与交流使用。

---

*作者：belabelosam7829b-oss*  
*创建日期：2026年7月*  
*版本：v1.0*
