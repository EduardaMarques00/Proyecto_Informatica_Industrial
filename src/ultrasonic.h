#ifndef ultrasonic_h
#define ultrasonic_h
// Configura os pinos GPIOS do sensor ultrasônico (gui | Testado | Validado)
void setupUltrasonicPins(int trigPin, int echoPin);
// Retorna a leitura em CM do sensor ultrasônico  (gui | Testado | Validado)
int getCm(int trigPin, int echoPin);
#endif