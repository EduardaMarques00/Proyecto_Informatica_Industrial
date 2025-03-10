#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

// Configurar os pinos GPIOS dos motores (gui | Testado | Validado)
void configurar_motores(uint8_t pino_esq_frente, uint8_t pino_esq_re, uint8_t pino_dir_frente, uint8_t pino_dir_re);

// Faz o motor girar no sentido horário (gui | Testado | Validado)
void mover_frente(void);

// Faz o motor girar no sentido ant-horário (gui | Testado | Validado)
void mover_re(void);

// Desliga os motores. Freio para os mais chegados. (gui | Testado | Validado)
void parar_motores(void);

// Task para testar os motores (Parâmetros FreeRTOS) (gui | Testado | Validado)
void teste_motores(void *pvParameters);

#endif // MOTOR_CONTROL_H
