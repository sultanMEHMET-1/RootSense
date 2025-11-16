#define STM32F091xC   // in main.c
#include "stm32f0xx.h"
#include <stdint.h>

void delay(volatile uint32_t s) {
    while (s--) __asm__("nop");
}

int main(void) {
    // Enable GPIOA clock
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN;
    (void)RCC->AHBENR; // ensure clock write completes

    GPIOA->MODER &= ~(0x3 << (8 * 2));  // clear mode bits for pin 8
    GPIOA->MODER |=  (0x1 << (8 * 2));  // set pin 8 as general purpose output

    while (1) {
        GPIOA->ODR ^= (1 << 8); // toggle PA5
        for (volatile uint32_t i = 0; i < 10000000; i++) __asm__("nop");
    }
}
