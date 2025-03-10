add_executable(${NAME}  
        main.c
        ultrasonic.c
        motores.c
        ../local-libs/ssd1306/ssd1306.c # SSD1306 OLED DISPLAY LOCAL LIBRARY
        ../local-libs/am2320/am2320.c # AM2320 SENSOR LOCAL LIBRARY
        ../local-libs/am2320/am2320_2.c # AM2320 SENSOR LOCAL LIBRARY
        ../local-libs/helpers/string_operations.c # MY STRING HELPERS
)

# pull in common dependencies
target_link_libraries(${NAME} 
        hardware_uart  # Biblioteca para UART
        hardware_gpio  # Biblioteca para GPIO
        hardware_pwm
        pico_stdlib                                 # for core functionality
        pico_cyw43_arch_lwip_threadsafe_background  # we need Wifi
        FreeRTOS-Kernel-Heap4                       # FreeRTOS kernel and dynamic heap
        hardware_i2c                                # Hardware I2C
        hardware_adc                                # Hardware ADC
        LWIP_PORT                                   # LWIP config files
        FREERTOS_PORT                               # FreeRTOS config files
)

# Enable print functionality on USB & disable on UART
pico_enable_stdio_usb(${NAME}  1) 
pico_enable_stdio_uart(${NAME}  0)

# create map/bin/hex file etc.
pico_add_extra_outputs(${NAME} )

# Include directories for uart.h and gpio.h if they are not already in the path
target_include_directories(${NAME}  
        PRIVATE ${CMAKE_CURRENT_LIST_DIR}
        PRIVATE ../local-libs/ssd1306 # SSD1306 OLED DISPLAY LOCAL LIBRARY
        PRIVATE ../local-libs/am2320 # AM2320 SENSOR LOCAL LIBRARY
        PRIVATE ../local-libs/helpers # ALL HELPER LOCAL LIBRARIES

)


