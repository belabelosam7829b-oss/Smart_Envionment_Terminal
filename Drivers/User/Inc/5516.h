#ifndef __5516_H
#define __5516_H

#include "main.h"

/**
 * @brief 初始化光敏传感器 ADC 并开启转换
 * @return 0: 成功
 */
int LightSensor_Init(void);

/**
 * @brief 读取光照强度百分比
 * @return 0-100 的百分比值
 */
int LightSensor_GetPercentage(void);

/**
 * @brief 读取 ADC 原始值
 * @return 0-4095 的原始数据
 */
uint32_t LightSensor_GetRawValue(void);

#endif
