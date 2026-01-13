#include "pico/stdlib.h"
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include "ultrasonic.h"
#include "motores.h"
#include <stdio.h>
#include <string.h>
#include "hardware/uart.h"
#include "hardware/irq.h"

// Requisitos do FreeRTOS
void init_run_time_timer(void) {}
unsigned long get_run_time_counter(void) { return (unsigned long) time_us_32(); }
void vApplicationIdleHook(void) {}
volatile absolute_time_t ultimo_parar = 0;

volatile bool parado_por_bluetooth = false;

// Pinos
#define MOTOR_ESQUERDO_FRENTE_PIN  2
#define MOTOR_ESQUERDO_RE_PIN      3
#define MOTOR_DIREITO_RE_PIN       4
#define MOTOR_DIREITO_FRENTE_PIN   5
#define TRIG_PIN 6
#define ECHO_PIN 7

#define UART_ID uart0
#define BAUD_RATE 9600
#define UART_TX_PIN 0
#define UART_RX_PIN 1

// Variáveis globais
volatile float distance = 0;
volatile bool motor_ativo = true;
SemaphoreHandle_t xDistanceMutex;

// Task do sensor ultrassônico
void vUltrasonicTask(void *pvParameters) {
    while (1) {
        if (!motor_ativo) {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        float new_distance = getCm(TRIG_PIN, ECHO_PIN);
        xSemaphoreTake(xDistanceMutex, portMAX_DELAY);
        distance = new_distance;
        xSemaphoreGive(xDistanceMutex);

      printf("[Ultrasonic] Leitura: %.2f cm\n", new_distance);

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// Task de controle dos motores
void vMotorControlTask(void *pvParameters) {
    while (1) {
        if (!motor_ativo || parado_por_bluetooth) {
          printf("[Motor] Desativado pelo Bluetooth\n");
            parar_motores();
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        float current_distance;
        xSemaphoreTake(xDistanceMutex, portMAX_DELAY);
        current_distance = distance;
        xSemaphoreGive(xDistanceMutex);

        if (current_distance >= 20.0) {
            printf("[Motor] Livre - andando para frente\n");
            mover_frente();
        } else if (current_distance > 0) {
           printf("[Motor] Obstáculo detectado - desviando\n");
            parar_motores();
            vTaskDelay(pdMS_TO_TICKS(200));

            printf("[Motor] Ré\n");
            gpio_put(MOTOR_ESQUERDO_FRENTE_PIN, 0);
            gpio_put(MOTOR_ESQUERDO_RE_PIN, 1);
            gpio_put(MOTOR_DIREITO_FRENTE_PIN, 0);
            gpio_put(MOTOR_DIREITO_RE_PIN, 1);
            vTaskDelay(pdMS_TO_TICKS(400));

            printf("[Motor] Gira para a direita\n");
            gpio_put(MOTOR_ESQUERDO_FRENTE_PIN, 1);
            gpio_put(MOTOR_ESQUERDO_RE_PIN, 0);
            gpio_put(MOTOR_DIREITO_FRENTE_PIN, 0);
            gpio_put(MOTOR_DIREITO_RE_PIN, 1);
            vTaskDelay(pdMS_TO_TICKS(500));

            printf("[Motor] Parando após desvio\n");
            parar_motores();
            vTaskDelay(pdMS_TO_TICKS(200));
        } else {
            printf("[Motor] Sem leitura de distância válida\n");
            parar_motores();
        }

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void vBluetoothTask(void *pvParameters) {
    while (1) {
        if (uart_is_readable(uart0)) {
            char c = uart_getc(uart0);
            if (c == '\n' || c == '\r') continue;

            if (c == 'p') {
                parado_por_bluetooth = true;
                parar_motores();
                ultimo_parar = get_absolute_time();
                printf("[Bluetooth] PARAR recebido\n");
            } else {
                printf("[Bluetooth] Ignorado: %c\n", c);
            }
        }

        // Verifica timeout: se já se passaram 2 segundos sem 'p', continuar andando
        if (parado_por_bluetooth &&
            absolute_time_diff_us(ultimo_parar, get_absolute_time()) > 2 * 1000 * 1000) {
            mover_frente();
            parado_por_bluetooth = false;
            printf("[Bluetooth] Timeout → CONTINUAR\n");
        }

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}


int main() {
    stdio_init_all();

    // Inicia UART do Bluetooth
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(UART_ID, false);

    printf("Inicializando motores e sensores...\n");

    configurar_motores(
        MOTOR_ESQUERDO_FRENTE_PIN,
        MOTOR_ESQUERDO_RE_PIN,
        MOTOR_DIREITO_FRENTE_PIN,
        MOTOR_DIREITO_RE_PIN
    );

    setupUltrasonicPins(TRIG_PIN, ECHO_PIN);

    xDistanceMutex = xSemaphoreCreateMutex();
    if (!xDistanceMutex) {
        printf("Erro ao criar mutex\n");
        while (1);
    }


    xTaskCreate(vUltrasonicTask, "Ultrasonic", 256, NULL, 2, NULL);
   xTaskCreate(vMotorControlTask, "Motor", 256, NULL, 1, NULL);
    xTaskCreate(vBluetoothTask, "Bluetooth", 256, NULL, 1, NULL);

    printf("Iniciando FreeRTOS Scheduler...\n");
    vTaskStartScheduler();

    while (1); // Nunca alcançado
}
