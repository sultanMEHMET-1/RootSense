#include "stm32f0xx.h"
#include "stm32f0xx_hal.h"
#include <stdint.h>

/* ------------ Ultrasonic Pins ------------ */
#define TRIG_GPIO_Port GPIOA
#define TRIG_Pin       GPIO_PIN_0

#define ECHO_GPIO_Port GPIOA
#define ECHO_Pin       GPIO_PIN_1

/* ------------ LED Pins ------------ */
/* PC0 = Green (LOW risk)
 * PC1 = Yellow (MED risk)
 * PC2 = Red (HIGH risk)
 */
#define LED_GREEN_GPIO_Port GPIOC
#define LED_GREEN_Pin       GPIO_PIN_0

#define LED_YELLOW_GPIO_Port GPIOC
#define LED_YELLOW_Pin       GPIO_PIN_1

#define LED_RED_GPIO_Port   GPIOC
#define LED_RED_Pin         GPIO_PIN_2

/* ------------ Temperature Sensor (AD8495) ------------ */
/*
 * Wire AD8495:
 *  - V+  -> 3.3V
 *  - GND -> GND
 *  - Vout -> PA4 (ADC1_IN4)
 *
 * We assume AD8495 transfer:
 *   Vout = 1.25V + 5mV/°C * T_C   (approx)
 */
#define TEMP_ADC_GPIO_Port GPIOA
#define TEMP_ADC_Pin       GPIO_PIN_4   // ADC1_IN4

/* ------------ Timer & ADC handles ------------ */
TIM_HandleTypeDef htim3;
ADC_HandleTypeDef hadc;

/* ------------ Farmland metrics types ------------ */
typedef struct {
    float distance_cm;                 // Measured distance from sensor to surface (soil or water)
    float water_depth_cm;              // Estimated water depth above soil
    uint8_t ponding;                   // 1 if ponding present, 0 if not
    float event_max_depth_cm;          // Max ponding depth during current/last event
    float event_duration_minutes;      // Duration of last ponding event
    float avg_infiltration_rate_mm_hr; // Average infiltration rate for last event
    uint8_t runoff_risk;               // 0 = low, 1 = medium, 2 = high
    float temperature_C;               // Current soil/air temperature from AD8495
} FarmlandMetrics;

/* ------------ Function Prototypes ------------ */
void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_TIM3_Init(void);
void MX_ADC_Init(void);

int  Ultrasonic_ReadDistanceCm(float *distance_cm, float temperature_C);
float Ultrasonic_CalibrateBaseline(uint16_t samples, float temperature_C);

int  Temperature_ReadCelsius(float *temperature_C);

void Farmland_UpdateMetrics(FarmlandMetrics *m,
                            float distance_cm,
                            float baseline_dry_cm,
                            uint32_t now_ms);

void LEDs_DisplayRisk(uint8_t runoff_risk, uint8_t ponding);

/* ------------ Main Program ------------ */
int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();
    MX_ADC_Init();

    FarmlandMetrics metrics = {0};
    float tempC = 20.0f;

    /* Read initial temperature */
    if (Temperature_ReadCelsius(&tempC) != 0)
        tempC = 20.0f; // fallback

    /* Calibrate dry baseline distance (sensor -> bare soil) using current temp */
    float baseline_dry_cm = Ultrasonic_CalibrateBaseline(20, tempC);

    float dist_cm = 0.0f;

    while (1)
    {
        /* Update temperature each cycle */
        if (Temperature_ReadCelsius(&tempC) == 0)
            metrics.temperature_C = tempC;

        if (Ultrasonic_ReadDistanceCm(&dist_cm, tempC) == 0)
        {
            uint32_t now = HAL_GetTick(); // ms since startup

            Farmland_UpdateMetrics(&metrics, dist_cm, baseline_dry_cm, now);
            LEDs_DisplayRisk(metrics.runoff_risk, metrics.ponding);
        }

        HAL_Delay(500); // measure ~2 Hz; adjust as needed
    }
}

/* ============================================================
 * Hardware Setup
 * ============================================================ */

/* Timer Configuration: TIM3 at 1 MHz (1 µs tick) */
void MX_TIM3_Init(void)
{
    __HAL_RCC_TIM3_CLK_ENABLE();

    htim3.Instance = TIM3;
    // Assuming APB1 timer clock is 48 MHz
    htim3.Init.Prescaler = 48 - 1;   // 48 MHz / 48 = 1 MHz
    htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim3.Init.Period = 0xFFFF;
    htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;

    HAL_TIM_Base_Init(&htim3);
    HAL_TIM_Base_Start(&htim3);
}

/* GPIO Initialization:
 *  - PA0: TRIG (output)
 *  - PA1: ECHO (input)
 *  - PA4: TEMP_ADC (analog)
 *  - PC0: Green LED (output)
 *  - PC1: Yellow LED (output)
 *  - PC2: Red LED (output)
 */
void MX_GPIO_Init(void)
{
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef GPIO_InitStruct = {0};

    /* Ultrasonic TRIG pin (PA0) as output */
    GPIO_InitStruct.Pin = TRIG_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(TRIG_GPIO_Port, &GPIO_InitStruct);
    HAL_GPIO_WritePin(TRIG_GPIO_Port, TRIG_Pin, GPIO_PIN_RESET);

    /* Ultrasonic ECHO pin (PA1) as input */
    GPIO_InitStruct.Pin = ECHO_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(ECHO_GPIO_Port, &GPIO_InitStruct);

    /* TEMP ADC pin (PA4) as analog */
    GPIO_InitStruct.Pin = TEMP_ADC_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(TEMP_ADC_GPIO_Port, &GPIO_InitStruct);

    /* LED pins (PC0, PC1, PC2) as outputs */
    GPIO_InitStruct.Pin = LED_GREEN_Pin | LED_YELLOW_Pin | LED_RED_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

    /* Turn all LEDs off initially */
    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LED_YELLOW_GPIO_Port, LED_YELLOW_Pin, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LED_RED_GPIO_Port, LED_RED_Pin, GPIO_PIN_RESET);
}

/* ADC Initialization: single-channel ADC1 on PA4 (IN4) */
void MX_ADC_Init(void)
{
    __HAL_RCC_ADC1_CLK_ENABLE();

    hadc.Instance = ADC1;
    hadc.Init.Resolution = ADC_RESOLUTION_12B;
    hadc.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc.Init.ScanConvMode = ADC_SCAN_DIRECTION_FORWARD;
    hadc.Init.ContinuousConvMode = DISABLE;
    hadc.Init.ExternalTrigConv = ADC_SOFTWARE_START;
    // hadc.Init.ExtTrigEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    hadc.Init.Overrun = ADC_OVR_DATA_OVERWRITTEN;
    hadc.Init.SamplingTimeCommon = ADC_SAMPLETIME_55CYCLES_5;

    if (HAL_ADC_Init(&hadc) != HAL_OK)
    {
        // Handle error
        while (1);
    }

    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = ADC_CHANNEL_4; // PA4
    sConfig.Rank = ADC_RANK_CHANNEL_NUMBER;
    if (HAL_ADC_ConfigChannel(&hadc, &sConfig) != HAL_OK)
    {
        // Handle error
        while (1);
    }

    /* Calibrate ADC */
    HAL_ADCEx_Calibration_Start(&hadc);
}

/* ============================================================
 * Temperature Reading from AD8495
 * ============================================================ */
/*
 * AD8495 approx transfer: Vout = 1.25V + 5mV/°C * T_C
 * So: T_C = (Vout - 1.25) / 0.005
 *
 * With 12-bit ADC and Vref=3.3V:
 *   Vout = (adc_value / 4095.0) * 3.3
 */

int Temperature_ReadCelsius(float *temperature_C)
{
    uint32_t adc_val = 0;

    if (HAL_ADC_Start(&hadc) != HAL_OK)
        return -1;

    if (HAL_ADC_PollForConversion(&hadc, 10) != HAL_OK)
    {
        HAL_ADC_Stop(&hadc);
        return -2;
    }

    adc_val = HAL_ADC_GetValue(&hadc);
    HAL_ADC_Stop(&hadc);

    float vout = (adc_val / 4095.0f) * 3.3f;
    float tempC = (vout - 1.25f) / 0.005f; // approx

    *temperature_C = tempC;
    return 0;
}

/* ============================================================
 * Ultrasonic Distance Measurement (temp-compensated)
 * ============================================================ */
/*
 * Speed of sound in air approx:
 *   c(m/s) = 331.3 + 0.606 * T_C
 *
 * Convert to cm/µs:
 *   c_cm_us = (c_m_s * 100 cm/m) / 1e6 µs/s
 *           = (331.3 + 0.606*T) * 0.0001
 */

int Ultrasonic_ReadDistanceCm(float *distance_cm, float temperature_C)
{
    uint32_t start = 0, end = 0, pulse_width = 0;
    uint32_t timeout = 0;

    // Calculate speed of sound (cm/us) based on temp
    float c_cm_us = (331.3f + 0.606f * temperature_C) * 0.0001f;

    // Ensure trigger low
    HAL_GPIO_WritePin(TRIG_GPIO_Port, TRIG_Pin, GPIO_PIN_RESET);
    HAL_Delay(2);

    // Trigger pulse (>=10 µs). Use short busy-wait instead of 1ms.
    HAL_GPIO_WritePin(TRIG_GPIO_Port, TRIG_Pin, GPIO_PIN_SET);
    for (volatile uint32_t i = 0; i < 300; i++) { __NOP(); }
    HAL_GPIO_WritePin(TRIG_GPIO_Port, TRIG_Pin, GPIO_PIN_RESET);

    // Wait for echo to go HIGH
    timeout = __HAL_TIM_GET_COUNTER(&htim3);
    while (HAL_GPIO_ReadPin(ECHO_GPIO_Port, ECHO_Pin) == GPIO_PIN_RESET)
    {
        if ((__HAL_TIM_GET_COUNTER(&htim3) - timeout) > 30000) // ~30 ms timeout
            return -1;
    }
    start = __HAL_TIM_GET_COUNTER(&htim3);

    // Wait for echo to go LOW
    timeout = start;
    while (HAL_GPIO_ReadPin(ECHO_GPIO_Port, ECHO_Pin) == GPIO_PIN_SET)
    {
        if ((__HAL_TIM_GET_COUNTER(&htim3) - timeout) > 30000) // ~30 ms timeout
            return -2;
    }
    end = __HAL_TIM_GET_COUNTER(&htim3);

    // Handle wraparound
    if (end >= start)
        pulse_width = end - start;
    else
        pulse_width = (0xFFFF - start) + end + 1;

    // Convert to cm: distance = (time_us * c_cm_us) / 2
    *distance_cm = (pulse_width * c_cm_us) / 2.0f;

    return 0;
}

/* Baseline Calibration (dry soil distance) */
float Ultrasonic_CalibrateBaseline(uint16_t samples, float temperature_C)
{
    float sum = 0.0f;
    uint16_t valid = 0;
    float d = 0.0f;

    for (uint16_t i = 0; i < samples; i++)
    {
        if (Ultrasonic_ReadDistanceCm(&d, temperature_C) == 0)
        {
            sum += d;
            valid++;
        }
        HAL_Delay(50);
    }

    if (valid == 0)
        return 0.0f;

    return sum / valid;
}

/* ============================================================
 * Farmland Metrics: Ponding & Infiltration
 * ============================================================ */

void Farmland_UpdateMetrics(FarmlandMetrics *m,
                            float distance_cm,
                            float baseline_dry_cm,
                            uint32_t now_ms)
{
    const float PONDING_DEPTH_THRESHOLD_CM = 0.5f;  // ~5 mm threshold
    static uint8_t prev_ponding = 0;
    static uint32_t event_start_ms = 0;
    static float event_max_depth_cm = 0.0f;

    // Update basic fields
    m->distance_cm = distance_cm;

    // Estimate water depth above soil
    float depth = baseline_dry_cm - distance_cm;
    if (depth < 0.0f) depth = 0.0f;
    m->water_depth_cm = depth;

    // Determine if ponding is present
    uint8_t ponding = (depth > PONDING_DEPTH_THRESHOLD_CM) ? 1 : 0;
    m->ponding = ponding;

    if (ponding)
    {
        if (!prev_ponding)
        {
            // Ponding just started
            event_start_ms = now_ms;
            event_max_depth_cm = depth;
            // Reset infiltration & risk until event ends
            m->avg_infiltration_rate_mm_hr = 0.0f;
            m->runoff_risk = 0;
        }
        else
        {
            // Ponding ongoing; update max depth
            if (depth > event_max_depth_cm)
                event_max_depth_cm = depth;
        }

        m->event_max_depth_cm = event_max_depth_cm;
        m->event_duration_minutes = (now_ms - event_start_ms) / 60000.0f;
    }
    else
    {
        if (prev_ponding)
        {
            // Ponding just ended -> finalize event metrics
            uint32_t event_end_ms = now_ms;
            float duration_hr = (event_end_ms - event_start_ms) / 3600000.0f;  // ms -> hr

            if (duration_hr > 0.0f)
            {
                // Average infiltration rate in mm/hr
                float avg_infiltration_mm_hr = (event_max_depth_cm * 10.0f) / duration_hr;
                m->avg_infiltration_rate_mm_hr = avg_infiltration_mm_hr;

                // Classify runoff risk based on max depth & duration
                if (event_max_depth_cm < 0.5f && duration_hr < (10.0f / 60.0f)) // <0.5cm & <10 min
                {
                    m->runoff_risk = 0; // low
                }
                else if (event_max_depth_cm < 1.5f && duration_hr < 1.0f) // moderate & <1hr
                {
                    m->runoff_risk = 1; // medium
                }
                else
                {
                    m->runoff_risk = 2; // high
                }
            }

            // Reset event state
            event_max_depth_cm = 0.0f;
            event_start_ms = 0;
        }
    }

    prev_ponding = ponding;
}

/* ============================================================
 * LED Display
 * ============================================================ */
/*
 * runoff_risk: 0 = LOW, 1 = MED, 2 = HIGH
 *
 * - Green LED ON when risk = LOW
 * - Yellow LED ON when risk = MED
 * - Red LED ON when risk = HIGH
 *
 * If currently ponding, we blink the chosen LED to signify active event.
 */

void LEDs_DisplayRisk(uint8_t runoff_risk, uint8_t ponding)
{
    GPIO_PinState green = GPIO_PIN_RESET;
    GPIO_PinState yellow = GPIO_PIN_RESET;
    GPIO_PinState red = GPIO_PIN_RESET;

    switch (runoff_risk)
    {
        case 0:
            green = GPIO_PIN_SET;
            break;
        case 1:
            yellow = GPIO_PIN_SET;
            break;
        case 2:
        default:
            red = GPIO_PIN_SET;
            break;
    }

    if (ponding)
    {
        static uint32_t last_toggle = 0;
        uint32_t now = HAL_GetTick();
        if ((now - last_toggle) > 500) // toggle every 500 ms
        {
            last_toggle = now;
            // Blink selected LED
            if (green == GPIO_PIN_SET)
                green = (HAL_GPIO_ReadPin(LED_GREEN_GPIO_Port, LED_GREEN_Pin) == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
            if (yellow == GPIO_PIN_SET)
                yellow = (HAL_GPIO_ReadPin(LED_YELLOW_GPIO_Port, LED_YELLOW_Pin) == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
            if (red == GPIO_PIN_SET)
                red = (HAL_GPIO_ReadPin(LED_RED_GPIO_Port, LED_RED_Pin) == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
        }
        else
        {
            HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, green);
            HAL_GPIO_WritePin(LED_YELLOW_GPIO_Port, LED_YELLOW_Pin, yellow);
            HAL_GPIO_WritePin(LED_RED_GPIO_Port, LED_RED_Pin, red);
            return;
        }
    }

    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, green);
    HAL_GPIO_WritePin(LED_YELLOW_GPIO_Port, LED_YELLOW_Pin, yellow);
    HAL_GPIO_WritePin(LED_RED_GPIO_Port, LED_RED_Pin, red);
}

/* ------------ Minimal System Clock Config (placeholder) ------------ */
void SystemClock_Config(void)
{
    // Fill with your CubeMX-generated clock config for real deployment.
}
