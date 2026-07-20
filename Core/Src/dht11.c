#include "dht11.h"
#include "tim.h"

// 微秒级延时函数
static void delay_us(uint16_t us)
{
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    while (__HAL_TIM_GET_COUNTER(&htim2) < us);
}

// 切换 PA9 为输出模式
static void DHT11_Mode_Output(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = DHT11_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(DHT11_PORT, &GPIO_InitStruct);
}

// 切换 PA9 为输入模式
static void DHT11_Mode_Input(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = DHT11_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(DHT11_PORT, &GPIO_InitStruct);
}

// DHT11 初始化
void DHT11_Init(void)
{
    DHT11_Mode_Output();
    HAL_GPIO_WritePin(DHT11_PORT, DHT11_PIN, GPIO_PIN_SET);
    HAL_Delay(1000); // 等待传感器稳定
}

// 从 DHT11 读取一个字节
static uint8_t DHT11_Read_Byte(void)
{
    uint8_t data = 0;
    for (int i = 0; i < 8; i++)
    {
        while (HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN) == GPIO_PIN_RESET);
        delay_us(40);
        data <<= 1;
        if (HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN) == GPIO_PIN_SET)
        {
            data |= 1;
            while (HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN) == GPIO_PIN_SET);
        }
    }
    return data;
}

// 读取 DHT11 温湿度数据
uint8_t DHT11_Read_Data(uint8_t *temp, uint8_t *humi)
{
    uint8_t buffer[5];
    
    // 1. 主机发送起始信号
    DHT11_Mode_Output();
    HAL_GPIO_WritePin(DHT11_PORT, DHT11_PIN, GPIO_PIN_RESET);
    HAL_Delay(18); // 至少 18ms
    HAL_GPIO_WritePin(DHT11_PORT, DHT11_PIN, GPIO_PIN_SET);
    delay_us(30);  // 20~40us
    
    // 2. 切换为输入模式，等待从机响应
    DHT11_Mode_Input();
    if (HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN) == GPIO_PIN_RESET)
    {
        while (HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN) == GPIO_PIN_RESET);
        while (HAL_GPIO_ReadPin(DHT11_PORT, DHT11_PIN) == GPIO_PIN_SET);
        
        // 3. 读取 40 位数据 (5 字节)
        for (int i = 0; i < 5; i++)
        {
            buffer[i] = DHT11_Read_Byte();
        }
        
        // 4. 校验和检查
        if (buffer[4] == (buffer[0] + buffer[1] + buffer[2] + buffer[3]))
        {
            *humi = buffer[0];
            *temp = buffer[2];
            return 0; // 成功
        }
    }
    return 1; // 失败
}
