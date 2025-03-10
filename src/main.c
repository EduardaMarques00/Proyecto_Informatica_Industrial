
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include "ultrasonic.h"
#include "motores.h"
#include "stdio.h"


#define MOTOR_ESQUERDO_FRENTE_PIN  2
#define MOTOR_ESQUERDO_RE_PIN      3
#define MOTOR_DIREITO_FRENTE_PIN   5
#define MOTOR_DIREITO_RE_PIN       4
#define TRIG_PIN                   6
#define ECHO_PIN                   7

void vUltrasonicTask(void *pvParameters);
void vMotorControlTask(void *pvParameters);

// Distância + Mutex para controlar o acesso a essa variável
volatile float distance = 0;
SemaphoreHandle_t xDistanceMutex;


void vUltrasonicTask(void *pvParameters) {
    while (1) {

        float new_distance = getCm(TRIG_PIN, ECHO_PIN);
        
        xSemaphoreTake(xDistanceMutex, portMAX_DELAY);
        //Região crítica (vozes da minha cabeça)
        distance = new_distance;
        xSemaphoreGive(xDistanceMutex);

    }
}

void vMotorControlTask(void *pvParameters) {
    while (1) {
        
        float current_distance;
        
        xSemaphoreTake(xDistanceMutex, portMAX_DELAY);
        current_distance = distance;
        xSemaphoreGive(xDistanceMutex);

        
        if (current_distance >= 20.0) {
            mover_frente(); 
        } else {
            parar_motores(); 
        }
        
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

int main() {
    
    setupUltrasonicPins(TRIG_PIN, ECHO_PIN);

    
    configurar_motores(MOTOR_ESQUERDO_FRENTE_PIN, MOTOR_ESQUERDO_RE_PIN, MOTOR_DIREITO_FRENTE_PIN, MOTOR_DIREITO_RE_PIN);

  
    xDistanceMutex = xSemaphoreCreateMutex();
   
    if (xDistanceMutex != NULL) {
        
        xTaskCreate(vUltrasonicTask, "Ultrasonic Task", configMINIMAL_STACK_SIZE, NULL, 1, NULL);
        xTaskCreate(vMotorControlTask, "Motor Control Task", configMINIMAL_STACK_SIZE, NULL, 1, NULL);

       
        vTaskStartScheduler();
    }
        //printf("NAO CRIOU ESSA MERDA DE SEMAFORO, FAZ DIREITO INFELIZ\n");
   
    while (1) {
        
    }

    return 0;
}