#ifndef __STM32F0xx_HAL_CONF_H
#define __STM32F0xx_HAL_CONF_H

#ifdef __cplusplus
 extern "C" {
#endif

// HAL module selection
#define HAL_MODULE_ENABLED
#define HAL_ADC_MODULE_ENABLED
#define HAL_DMA_MODULE_ENABLED
#define HAL_GPIO_MODULE_ENABLED
#define HAL_RCC_MODULE_ENABLED
#define HAL_CORTEX_MODULE_ENABLED
#define HAL_TIM_MODULE_ENABLED
#define HAL_FLASH_MODULE_ENABLED
#define HAL_PWR_MODULE_ENABLED

// Oscillator values
#define HSE_VALUE    ((uint32_t)8000000U)
#define HSI_VALUE    ((uint32_t)8000000U)
#define HSI48_VALUE  ((uint32_t)48000000U)
#define LSI_VALUE    ((uint32_t)40000U)
#define LSE_VALUE    ((uint32_t)32768U)

// Startup timeouts
#define HSE_STARTUP_TIMEOUT    ((uint32_t)100U)
#define LSE_STARTUP_TIMEOUT    ((uint32_t)5000U)

// System Configuration
#define VDD_VALUE                    ((uint32_t)3300U)
#define TICK_INT_PRIORITY            ((uint32_t)0U)
#define USE_RTOS                     0U
#define PREFETCH_ENABLE              1U
#define INSTRUCTION_CACHE_ENABLE     0U
#define DATA_CACHE_ENABLE            0U

// Assert configuration (disable for now)
#define USE_FULL_ASSERT    0U

#if (USE_FULL_ASSERT == 1U)
  #define assert_param(expr) ((expr) ? (void)0U : assert_failed((uint8_t *)__FILE__, __LINE__))
  void assert_failed(uint8_t* file, uint32_t line);
#else
  #define assert_param(expr) ((void)0U)
#endif

// Include HAL modules
#ifdef HAL_RCC_MODULE_ENABLED
  #include "stm32f0xx_hal_rcc.h"
#endif

#ifdef HAL_DMA_MODULE_ENABLED
  #include "stm32f0xx_hal_dma.h"
#endif

#ifdef HAL_GPIO_MODULE_ENABLED
  #include "stm32f0xx_hal_gpio.h"
#endif

#ifdef HAL_CORTEX_MODULE_ENABLED
  #include "stm32f0xx_hal_cortex.h"
#endif

#ifdef HAL_ADC_MODULE_ENABLED
  #include "stm32f0xx_hal_adc.h"
#endif

#ifdef HAL_TIM_MODULE_ENABLED
  #include "stm32f0xx_hal_tim.h"
#endif

#ifdef HAL_FLASH_MODULE_ENABLED
  #include "stm32f0xx_hal_flash.h"
#endif

#ifdef HAL_PWR_MODULE_ENABLED
  #include "stm32f0xx_hal_pwr.h"
#endif

#ifdef __cplusplus
}
#endif

#endif /* __STM32F0xx_HAL_CONF_H */