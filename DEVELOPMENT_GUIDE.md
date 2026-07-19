# STM32 工程开发指南

## 重要规则（必须严格遵守）

### 1. 不要删除或修改 CubeMX 自动生成代码结构
- 保持 CubeMX 生成的文件结构和代码布局不变

### 2. 所有业务代码必须放在指定区域
- 所有自定义代码必须写在 /* USER CODE BEGIN xxx */ 和 /* USER CODE END xxx */ 标记之间
- 例如：
  `c
  /* USER CODE BEGIN 3 */
  // 您的业务代码写在这里
  HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
  HAL_Delay(500);
  /* USER CODE END 3 */
  `

### 3. 不要把代码写到 CubeMX 自动生成区域
- 不要在标记区域之外添加任何自定义代码
- CubeMX 重新生成代码时会覆盖这些区域

### 4. 新增功能建议
- 如需新增功能，优先考虑新建独立的 .c 和 .h 文件
- 不要大量修改 main.c 文件

### 5. Git 工作流程
- 修改代码前先检查 Git 状态：git status
- 确保不会覆盖已有代码
- 及时提交代码变更

## 文件结构
`
Project1/
├── Core/
│   ├── Inc/          # 用户头文件
│   └── Src/          # 用户源文件
├── Drivers/          # STM32 HAL 驱动（不要修改）
├── cmake/            # CMake 构建配置（不要修改）
├── CMakeLists.txt    # 主构建文件（谨慎修改）
└── DEVELOPMENT_GUIDE.md  # 本文件
`
