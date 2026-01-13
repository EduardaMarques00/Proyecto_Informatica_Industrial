#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

void configurar_motores(uint8_t pino_esq_frente, uint8_t pino_esq_re, uint8_t pino_dir_frente, uint8_t pino_dir_re);

void mover_frente(void);

void mover_re(void);

void parar_motores(void);

void teste_motores(void *pvParameters);

#endif // MOTOR_CONTROL_H