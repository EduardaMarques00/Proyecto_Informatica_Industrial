#include "pico/stdlib.h"
#include "FreeRTOS.h"
#include "task.h"
#include "motores.h"


static uint8_t pino_motor_esquerdo_frente;
static uint8_t pino_motor_esquerdo_re;
static uint8_t pino_motor_direito_frente;
static uint8_t pino_motor_direito_re;


void configurar_motores(uint8_t pino_esq_frente, uint8_t pino_esq_re, uint8_t pino_dir_frente, uint8_t pino_dir_re) {
    pino_motor_esquerdo_frente = pino_esq_frente;
    pino_motor_esquerdo_re = pino_esq_re;
    pino_motor_direito_frente = pino_dir_frente;
    pino_motor_direito_re = pino_dir_re;
    
   
    gpio_init(pino_motor_esquerdo_frente);
    gpio_set_dir(pino_motor_esquerdo_frente, GPIO_OUT);
    
    gpio_init(pino_motor_esquerdo_re);
    gpio_set_dir(pino_motor_esquerdo_re, GPIO_OUT);
    
    gpio_init(pino_motor_direito_frente);
    gpio_set_dir(pino_motor_direito_frente, GPIO_OUT);
    
    gpio_init(pino_motor_direito_re);
    gpio_set_dir(pino_motor_direito_re, GPIO_OUT);
}


void mover_frente() {
    gpio_put(pino_motor_esquerdo_frente, 1);  
    gpio_put(pino_motor_esquerdo_re, 0);      
    
    gpio_put(pino_motor_direito_frente, 1);   
    gpio_put(pino_motor_direito_re, 0);       
}


void mover_re() {
    gpio_put(pino_motor_esquerdo_frente, 0);  
    gpio_put(pino_motor_esquerdo_re, 1);      
    
    gpio_put(pino_motor_direito_frente, 0);   
    gpio_put(pino_motor_direito_re, 1);       
}


void parar_motores() {
    gpio_put(pino_motor_esquerdo_frente, 0);  
    gpio_put(pino_motor_esquerdo_re, 0);
    
    gpio_put(pino_motor_direito_frente, 0);  
    gpio_put(pino_motor_direito_re, 0);
}


void teste_motores(void *pvParameters) {
    while (1) {
        mover_frente();
        vTaskDelay(pdMS_TO_TICKS(2000)); 
        
        parar_motores();
        vTaskDelay(pdMS_TO_TICKS(1000)); 
        
        mover_re();
        vTaskDelay(pdMS_TO_TICKS(2000)); 
        
        parar_motores();
        vTaskDelay(pdMS_TO_TICKS(1000)); 
    }
}
