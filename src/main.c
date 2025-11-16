#define STM32F091xC   // in main.c
#include "stm32f0xx.h"
#include <stdint.h>

void delay(volatile uint32_t s) {
    while (s--) __asm__("nop");
}

int main(void) {
    // Enable GPIOA and GPIOC clocks
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOCEN;
    (void)RCC->AHBENR;

    // PC0 as output
    GPIOC->MODER &= ~(3U << (0 * 2));
    GPIOC->MODER |=  (1U << (0 * 2));

    while (1) {
        GPIOC->BSRR = GPIO_BSRR_BS_0;
        delay(100000);

        GPIOC->BSRR = GPIO_BSRR_BR_0;
        delay(100000);
    }
}
