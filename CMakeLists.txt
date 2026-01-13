cmake_minimum_required(VERSION 3.13)

# Nome do projeto
set(NAME PICO_FREERTOS)
set(PICO_BOARD "pico_w")
set(PICO_SDK_PATH /home/eduarda/2025.1/RTOS/pico/pico-sdk)

# SDK da Pico
include(pico_sdk_import.cmake)

project(${NAME} C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Caminho correto para o FreeRTOS Kernel
set(FREERTOS_KERNEL_PATH "/home/eduarda/2025.1/RTOS/FreeRTOS/FreeRTOS/Source")
set(FREERTOS_CONFIG_FILE_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/configs/FreeRTOS-Kernel")
include_directories("${FREERTOS_CONFIG_FILE_DIRECTORY}")

# Importa o FreeRTOS
include(FreeRTOS_Kernel_import.cmake)

# (Se necessário) configura suporte a lwIP
include(lwip_import.cmake)

# Código-fonte
add_subdirectory(src)

# USB e UART
pico_enable_stdio_usb(${NAME} 1)
pico_enable_stdio_uart(${NAME} 0)

# Geração de UF2 e deploy opcional
install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.uf2
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}
)

set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY OFF)
set(CPACK_GENERATOR "ZIP" "TGZ")
include(CPack)

# Script de deploy opcional
install(CODE "execute_process(COMMAND $ENV{HOME}/bin/picoDeploy.sh ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.elf)")
