//Get readings from ultrasonic sensor

#include "pico/stdlib.h"
#include <stdio.h>
#include "hardware/gpio.h"
#include "hardware/timer.h"

int timeout = 26100;

void setupUltrasonicPins(uint trigPin, uint echoPin)
{
    gpio_init(trigPin);
    gpio_init(echoPin);
    gpio_set_dir(trigPin, GPIO_OUT);
    gpio_set_dir(echoPin, GPIO_IN);
}

uint64_t getPulse(uint trigPin, uint echoPin)
{
    gpio_put(trigPin, 1);
    //10 micro
    sleep_us(10);
    gpio_put(trigPin, 0);

    uint64_t width = 0;

    //Espera até entrar no modo ouvinte.
    while (gpio_get(echoPin) == 0) tight_loop_contents();
    
    absolute_time_t startTime = get_absolute_time();
    //Medir a duração do pulso
    while (gpio_get(echoPin) == 1) 
    {
        width++;
        sleep_us(1);
        // Ema Ema Ema, cada gambiarra com seus problemas.
        if (width > timeout) return 0xFFFF; //0;
    }
    
    absolute_time_t endTime = get_absolute_time();
    
    //Calcula a duração do pulso em microsegundos e retorna. (Time.h salvando vidas)
    return absolute_time_diff_us(startTime, endTime);
}

uint64_t getCm(uint trigPin, uint echoPin)
{
    uint64_t pulseLength = getPulse(trigPin, echoPin);
    return pulseLength / 29 / 2;
}

// Indiano abençoado, facilitou meu trabalho de transformar polegadas (Inch) em CM
/*
   (long)pulseLength / 74.f / 2.f;
*/