#include "led.h"

void LED_Init(void)
{
    // LED 已经在 CubeMX 中通过 MX_GPIO_Init() 初始化
    // 这里可以添加额外的初始化代码
}

void LED_On(void)
{
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
}

void LED_Off(void)
{
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
}

void LED_Toggle(void)
{
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
}

void LED_Blink(uint32_t delay_ms)
{
    LED_Toggle();
    HAL_Delay(delay_ms);
}