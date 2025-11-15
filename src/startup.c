#include <stdint.h>

extern int main(void);

void Reset_Handler(void);
void Default_Handler(void) { while (1); }

__attribute__((section(".isr_vector")))
void (* const vector_table[])(void) = {
    (void (*)(void))(0x20008000), // Initial stack pointer (32KB RAM)
    Reset_Handler,                // Reset
    Default_Handler,              // NMI
    Default_Handler,              // HardFault
};

void Reset_Handler(void) {
    main();
}
