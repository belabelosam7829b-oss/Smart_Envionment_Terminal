@echo off
set "PATH=C:\Users\花名\.local\stm32-tools\arm-gcc\bin;C:\Users\花名\.local\stm32-tools\cmake\bin;C:\Users\花名\.local\stm32-tools;C:\Users\花名\.local\stm32-tools\openocd\bin;%PATH%"

cd /d "D:\cubemx first example\Project1\build\Debug"

echo Flashing firmware to STM32...
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg -c "init" -c "reset halt" -c "flash erase_sector 0 0 last" -c "flash write_image erase Project1.elf" -c "verify_image Project1.elf" -c "reset run" -c "exit"

if %errorlevel% equ 0 (
    echo Flashing successful!
) else (
    echo Flashing failed!
)