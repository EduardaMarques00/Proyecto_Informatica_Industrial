# Sistema de Detecção de Fadiga para Motoristas

## Descrição do Projeto
Sistema embarcado baseado em Raspberry Pi Pico W e FreeRTOS para detecção precoce de sinais de fadiga em motoristas.

## Estrutura do Projeto

Proyecto_Informatica_Industrial/
├── README.md # Documentación principal (este arquivo)
├── requirements.txt # Dependencias Python
├── software/detector_fatiga.py # Sistema completo de detecção
├── software/prueba_rapida.py # Versión simplificada para prueba
├── firmware/ # Código FreeRTOS para Pico W
├── hardware/ # Esquemas y listas de componentes
├── docs/guia_prueba_rapida.md # Instrucciones detalladas
└── docs/memoria_proyecto.pdf # Memoria completa del proyecto


##  Instalação e Uso

### Requisitos
- Raspberry Pi Pico W
- Python 3.8+
- FreeRTOS Kernel

### Instalação
```bash
git clone https://github.com/EduardaMarques00/Proyecto_Informatica_Industrial.git
cd Proyecto_Informatica_Industrial
pip install -r requirements.txt