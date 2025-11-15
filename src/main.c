#include "stm32f0xx.h"  // CMSIS header for F0 series

void delay(volatile uint32_t s) {
    while (s--) __asm__("nop");
}

int main(void) {
    // Enable GPIOA clock
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN;

    // Set PA5 as output (01)
    GPIOA->MODER &= ~(3U << (5 * 2));
    GPIOA->MODER |=  (1U << (5 * 2));

    while (1) {
        GPIOA->ODR ^= (1 << 5); // toggle PA5
        delay(200000);
    }
}
