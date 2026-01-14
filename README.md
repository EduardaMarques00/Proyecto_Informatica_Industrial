# Proyecto: Vehículo Robótico con Detección de Fatiga Integrada

## Descripción del Sistema
Sistema integrado que combina:
- **Vehículo robótico autónomo** (Raspberry Pi Pico W + FreeRTOS)
- **Sistema de detección de fatiga** (Python + MediaPipe + OpenCV)
- **Protocolo de seguridad** con verificación en dos fases

##  Características Principales
- ✅ **Detección robusta de fatiga** con algoritmo EAR+MAR
- ✅ **FreeRTOS en Pico W** con 3 tareas independientes
- ✅ **Navegación autónoma** con evasión de obstáculos
- ✅ **Protocolo Bluetooth** de seguridad
- ✅ **Coste ultrabajo** (< 50€ en componentes)

##  Instrucciones Rápidas

### Para probar solo el detector de fatiga (2 minutos):
```bash
git clone https://github.com/EduardaMarques00/Proyecto_Informatica_Industrial.git
cd Proyecto_Informatica_Industrial/software/pc_fatiga_detector
pip install opencv-python mediapipe numpy
python prueba_rapida.py
