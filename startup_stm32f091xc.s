/* startup_stm32f0.s - minimal startup */
    .syntax unified
    .cpu cortex-m0
    .thumb
    .section .isr_vector,"a",%progbits
    .type g_pfnVectors, %object
    .size g_pfnVectors, .-g_pfnVectors

    .word   _estack
    .word   Reset_Handler
    .word   NMI_Handler
    .word   HardFault_Handler
    .word   0
    .word   0
    .word   0
    .word   0
    .word   0
    .word   0
    .word   0

    .weak NMI_Handler
    .type NMI_Handler, %function
NMI_Handler:
    b .

    .weak HardFault_Handler
    .type HardFault_Handler, %function
HardFault_Handler:
    b .

    .weak Reset_Handler
    .type Reset_Handler, %function
Reset_Handler:
    /* Copy .data from flash to RAM */
    ldr r0, =_sdata
    ldr r1, =_edata
    ldr r2, =_etext
1:
    cmp r0, r1
    ittt lt
    ldrlt r3, [r2], #4
    strlt r3, [r0], #4
    blt 1b

    /* Zero fill .bss */
    ldr r0, =_sbss
    ldr r1, =_ebss
2:
    cmp r0, r1
    it lt
    movlt r3, #0
    strlt r3, [r0], #4
    blt 2b

    /* Call SystemInit() and main() */
    bl SystemInit
    bl main

    /* If main returns, loop */
    b .

    .section .text
    .size Reset_Handler, .-Reset_Handler
