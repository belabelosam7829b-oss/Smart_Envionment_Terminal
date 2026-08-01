#include "Serial.h"
#include "usart.h"
#include <stdio.h>
#include <stdarg.h>

/**
 * @brief 初始化串口（USART3 已经在 usart.c 中初始化，这里主要做逻辑准备）
 */
void Serial_Init(void)
{
    // MX_USART3_UART_Init() 已经在 main.c 中被调用
}

/**
 * @brief 发送一个字节
 */
/**
 * @brief 串口传输超时时间（毫秒），避免阻塞主循环
 */
#define SERIAL_TIMEOUT_MS 100

void Serial_SendByte(uint8_t Byte)
{
    HAL_UART_Transmit(&huart3, &Byte, 1, SERIAL_TIMEOUT_MS);
}

/**
 * @brief 发送数组
 */
void Serial_SendArray(uint8_t *Array, uint16_t Length)
{
    HAL_UART_Transmit(&huart3, Array, Length, SERIAL_TIMEOUT_MS);
}

/**
 * @brief 发送字符串
 */
void Serial_SendString(char *String)
{
    uint16_t len = 0;
    while (String[len] != '\0') len++;
    HAL_UART_Transmit(&huart3, (uint8_t *)String, len, SERIAL_TIMEOUT_MS);
}

/**
 * @brief 内部函数：计算次方
 */
static uint32_t Serial_Pow(uint32_t X, uint32_t Y)
{
    uint32_t Result = 1;
    while (Y--)
    {
        Result *= X;
    }
    return Result;
}

/**
 * @brief 发送数字（十进制）
 */
void Serial_SendNumber(uint32_t Number, uint8_t Length)
{
    uint8_t i;
    for (i = 0; i < Length; i++)
    {
        Serial_SendByte(Number / Serial_Pow(10, Length - i - 1) % 10 + '0');
    }
}

/**
 * @brief printf 重定向 (针对 Keil/ARMCC 或部分 GCC 环境)
 */
int fputc(int ch, FILE *f)
{
    Serial_SendByte(ch);
    return ch;
}

/**
 * @brief printf 重定向 (针对 GCC 环境，如 STM32CubeIDE/VSCode CMake)
 */
int _write(int file, char *ptr, int len)
{
    HAL_UART_Transmit(&huart3, (uint8_t *)ptr, len, SERIAL_TIMEOUT_MS);
    return len;
}

/**
 * @brief 封装的 Printf 函数
 */
void Serial_Printf(char *format, ...)
{
    char String[128];
    va_list arg;
    va_start(arg, format);
    vsnprintf(String, sizeof(String), format, arg);
    va_end(arg);
    Serial_SendString(String);
}
