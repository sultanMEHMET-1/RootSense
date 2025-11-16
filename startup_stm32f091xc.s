.syntax unified
.cpu cortex-m0
.thumb

.global Reset_Handler
.extern main

.equ STACK_SIZE, 0x400
.section .stack, "aw", %nobits
stack_top:
    .space STACK_SIZE

.section .isr_vector, "a"
    .word stack_top + STACK_SIZE   /* Initial SP */
    .word Reset_Handler            /* Reset Handler */

Reset_Handler:
    ldr r0, =stack_top + STACK_SIZE
    mov sp, r0
    bl main
1:  b 1b
