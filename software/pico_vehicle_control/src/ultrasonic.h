#ifndef ULTRASONIC_H
#define ULTRASONIC_H

#include "pico/stdlib.h"

void setupUltrasonicPins(uint trigPin, uint echoPin);
uint64_t getPulse(uint trigPin, uint echoPin);
uint64_t getCm(uint trigPin, uint echoPin);

#endif
