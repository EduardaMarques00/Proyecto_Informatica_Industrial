#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/timer.h"
#include <stdio.h>
#include "ultrasonic.h"

#define TIMEOUT_US 30000  // Timeout de 30ms para espera de pulso

void setupUltrasonicPins(uint trigPin, uint echoPin) {
    gpio_init(trigPin);
    gpio_set_dir(trigPin, GPIO_OUT);
    gpio_put(trigPin, 0);

    gpio_init(echoPin);
    gpio_set_dir(echoPin, GPIO_IN);
}

uint64_t getPulse(uint trigPin, uint echoPin) {
    gpio_put(trigPin, 1);
    sleep_us(10);
    gpio_put(trigPin, 0);

    // Espera início do pulso (subida do echo) com timeout
    absolute_time_t start_wait = get_absolute_time();
    while (gpio_get(echoPin) == 0) {
        if (absolute_time_diff_us(start_wait, get_absolute_time()) > TIMEOUT_US) {
            return 0xFFFF;  // Timeout: sem pulso de subida
        }
    }

    absolute_time_t startTime = get_absolute_time();

    // Espera fim do pulso (descida do echo) com timeout
    while (gpio_get(echoPin) == 1) {
        if (absolute_time_diff_us(startTime, get_absolute_time()) > TIMEOUT_US) {
            return 0xFFFF;  // Timeout: pulso muito longo
        }
    }

    absolute_time_t endTime = get_absolute_time();
    return absolute_time_diff_us(startTime, endTime);
}

uint64_t getCm(uint trigPin, uint echoPin) {
    uint64_t pulseLength = getPulse(trigPin, echoPin);
    if (pulseLength == 0xFFFF) return 0;
    return pulseLength / 29 / 2;
}
