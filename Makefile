# Makefile for STM32F091RCT6 RootSense Project

PROJECT = rootsense-firmware
SRCDIR  = src
BUILD_DIR = build

# Main application source
SRC = $(SRCDIR)/main.c

# CMSIS System file
SRC += Drivers/CMSIS/Device/ST/STM32F0xx/Source/Templates/system_stm32f0xx.c

# HAL sources
HAL_SRC = \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_gpio.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_rcc.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_adc.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_adc_ex.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_tim.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_tim_ex.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_dma.c \
  Drivers/STM32F0xx_HAL_Driver/Src/stm32f0xx_hal_cortex.c

# Startup assembly file (use the correct one from CMSIS)
ASM_SRC = Drivers/CMSIS/Device/ST/STM32F0xx/Source/Templates/gcc/startup_stm32f091xc.s

ALLSRC = $(SRC) $(HAL_SRC)
OBJ = $(patsubst %.c,$(BUILD_DIR)/%.o,$(filter %.c,$(ALLSRC))) \
	$(patsubst %.s,$(BUILD_DIR)/%.o,$(ASM_SRC))

# Include paths
INC = -IDrivers/CMSIS/Device/ST/STM32F0xx/Include \
	-IDrivers/CMSIS/Include \
	-IDrivers/STM32F0xx_HAL_Driver/Inc \
	-I.

# Toolchain
CC = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
SIZE = arm-none-eabi-size

# Compiler flags
CFLAGS = -mcpu=cortex-m0 -mthumb -Os -ffunction-sections -fdata-sections \
	   -Wall -Wextra -std=gnu17 $(INC) -DSTM32F091xC -DUSE_HAL_DRIVER

# Linker flags (use correct linker script)
LDFLAGS = -TSTM32F091RCTX_FLASH.ld --specs=nosys.specs -Wl,--gc-sections \
		-Wl,-Map=$(BUILD_DIR)/$(PROJECT).map

.PHONY: all clean flash

all: $(BUILD_DIR)/$(PROJECT).elf $(BUILD_DIR)/$(PROJECT).bin $(BUILD_DIR)/$(PROJECT).hex
	@echo "Build complete."
	@$(SIZE) $(BUILD_DIR)/$(PROJECT).elf

# Compile C sources
$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

# Compile assembly
$(BUILD_DIR)/%.o: %.s | $(BUILD_DIR)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

# Link
$(BUILD_DIR)/$(PROJECT).elf: $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) $(LDFLAGS) -o $@

# Generate BIN
$(BUILD_DIR)/$(PROJECT).bin: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJCOPY) -O binary $< $@

# Generate HEX
$(BUILD_DIR)/$(PROJECT).hex: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJCOPY) -O ihex $< $@

# Create build directory
$(BUILD_DIR):
	mkdir -p $@

# Flash using st-flash
flash: $(BUILD_DIR)/$(PROJECT).bin
	st-flash write $< 0x8000000

# Clean
clean:
	rm -rf $(BUILD_DIR) $(PROJECT).elf $(PROJECT).bin $(PROJECT).hex

# VPATH for finding source files
vpath %.c $(sort $(dir $(ALLSRC)))
vpath %.s $(sort $(dir $(ASM_SRC)))
