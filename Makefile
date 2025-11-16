TARGET = main
BUILD = build

CPU = -mcpu=cortex-m0 -mthumb
CFLAGS = $(CPU) -O2 -Wall -Wextra -ffreestanding -nostdlib \
         -Iinclude \
         -IDrivers/CMSIS/Include \
         -IDrivers/CMSIS/Device/ST/STM32F0xx/Include \
         -DSTM32F091xC

LDFLAGS = $(CPU) -T linker.ld -Wl,--gc-sections -nostdlib

SRCS = $(wildcard src/*.c)
OBJS = $(SRCS:src/%.c=$(BUILD)/%.o)

all: $(BUILD) $(BUILD)/$(TARGET).elf $(BUILD)/$(TARGET).bin

STARTUP = startup_stm32f091xc.s
$(BUILD)/$(TARGET).elf: $(OBJS) $(STARTUP)
	arm-none-eabi-gcc $(OBJS) $(STARTUP) $(LDFLAGS) -o $@


$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.o: src/%.c
	arm-none-eabi-gcc $(CFLAGS) -c $< -o $@

$(BUILD)/$(TARGET).elf: $(OBJS)
	arm-none-eabi-gcc $(OBJS) $(LDFLAGS) -o $@

$(BUILD)/$(TARGET).bin: $(BUILD)/$(TARGET).elf
	arm-none-eabi-objcopy -O binary $< $@

flash: all
	openocd -f interface/stlink.cfg \
	        -f target/stm32f0x.cfg \
	        -c "program $(BUILD)/$(TARGET).elf verify reset exit"

clean:
	rm -rf $(BUILD)
