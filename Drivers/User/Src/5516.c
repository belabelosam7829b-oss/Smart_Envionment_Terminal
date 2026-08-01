#include "5516.h"
#include "adc.h"

/**
 * @brief 初始化光敏传感器 ADC 并开启转换
 */
int LightSensor_Init(void)
{
    // ADC 校准
    if (HAL_ADCEx_Calibration_Start(&hadc1) != HAL_OK)
    {
        return -1;
    }
    // 开启 ADC 连续转换
    if (HAL_ADC_Start(&hadc1) != HAL_OK)
    {
        return -1;
    }
    return 0;
}

/**
 * @brief 读取 ADC 原始值
 */
uint32_t LightSensor_GetRawValue(void)
{
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK)
    {
        return HAL_ADC_GetValue(&hadc1);
    }
    return 0;
}

/**
 * @brief 读取光照强度百分比
 */
int LightSensor_GetPercentage(void)
{
    uint32_t raw = LightSensor_GetRawValue();
    
    // ADC 12位映射到 0-100
    // 用户反馈手遮挡数值变高，说明当前电路中光越强 ADC 值越小
    // 因此需要反转映射逻辑：100 - (raw * 100 / 4095)
    int percentage = 100 - (int)((raw * 100) / 4095);
    
    if (percentage > 100) percentage = 100;
    if (percentage < 0) percentage = 0;
    
    return percentage;
}
