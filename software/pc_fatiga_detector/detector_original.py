# detector_fatiga_original.py - CÓDIGO ORIGINAL DEL PROYECTO
# Sistema completo de detección de fatiga con Bluetooth
# Desarrollado por: Maria Eduarda Santana Marques
# Asignatura: Informática Industrial - Enero 2026

import cv2
import mediapipe as mp
import numpy as np
import time
import serial

print("=" * 70)
print("SISTEMA ORIGINAL DE DETECCIÓN DE FATIGA CON BLUETOOTH")
print("Desarrollado por: Maria Eduarda Santana Marques")
print("Informática Industrial - Enero 2026")
print("=" * 70)
print("\n[NOTA] Este es el código EXACTO usado en el proyecto")
print("       Incluye comunicación Bluetooth real con vehículo")
print("=" * 70)

# Inicializar MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Puntos faciales para EAR (Eye Aspect Ratio)
p_olho_esq = [385, 380, 387, 373, 362, 263]   # Ojo izquierdo
p_olho_dir = [160, 144, 158, 153, 33, 133]    # Ojo derecho
p_olhos = p_olho_esq + p_olho_dir

# Puntos faciales para MAR (Mouth Aspect Ratio)
p_boca = [82, 87, 13, 14, 312, 317, 78, 308]  # Boca

def calculo_ear(face, p_olho_dir, p_olho_esq):
    """Calcular Eye Aspect Ratio (EAR) - Relación de Aspecto del Ojo"""
    try:
        # Convertir landmarks a coordenadas 2D
        face = np.array([[coord.x, coord.y] for coord in face])
        face_esq = face[p_olho_esq, :]
        face_dir = face[p_olho_dir, :]

        # Cálculo EAR para ojo izquierdo
        ear_esq = (np.linalg.norm(face_esq[0] - face_esq[1]) + 
                  np.linalg.norm(face_esq[2] - face_esq[3])) / (2.0 * np.linalg.norm(face_esq[4] - face_esq[5]))
        
        # Cálculo EAR para ojo derecho
        ear_dir = (np.linalg.norm(face_dir[0] - face_dir[1]) + 
                  np.linalg.norm(face_dir[2] - face_dir[3])) / (2.0 * np.linalg.norm(face_dir[4] - face_dir[5]))
        
    except Exception as e:
        # En caso de error en el cálculo
        ear_esq = 0.0
        ear_dir = 0.0
    
    # EAR promedio de ambos ojos
    media_ear = (ear_esq + ear_dir) / 2.0
    return media_ear

def calculo_mar(face, p_boca):
    """Calcular Mouth Aspect Ratio (MAR) - Relación de Aspecto de la Boca"""
    try:
        # Convertir landmarks a coordenadas 2D
        face = np.array([[coord.x, coord.y] for coord in face])
        boca = face[p_boca, :]
        
        # Cálculo MAR (distancia vertical / distancia horizontal)
        mar = (np.linalg.norm(boca[0] - boca[1]) + 
               np.linalg.norm(boca[2] - boca[3]) + 
               np.linalg.norm(boca[4] - boca[5])) / (2.0 * np.linalg.norm(boca[6] - boca[7]))
    except Exception as e:
        mar = 0.0
    
    return mar

# PARÁMETROS CALIBRADOS EXPERIMENTALMENTE
ear_limiar = 0.25   # Umbral EAR: si < 0.25 → ojos cerrados
mar_limiar = 0.2    # Umbral MAR: si > 0.2 → boca abierta

# Variables de estado del sistema
dormindo = 0                # 0 = despierto, 1 = posible fatiga
contagem_piscadas = 0       # Contador de detecciones
c_tempo = 0                 # Contador de tiempo
contagem_temporaria = 0     # Contador temporal
contagem_lista = []         # Historial de detecciones

t_piscadas = time.time()    # Tiempo de referencia

# Inicializar captura de video
cap = cv2.VideoCapture(0)
print("[INFO] Iniciando cámara...")

# CONFIGURACIÓN BLUETOOTH (conexión real con vehículo)
porta_bt = "/dev/rfcomm0"  # Puerto Bluetooth en Linux
try:
    bt_serial = serial.Serial(porta_bt, 9600, timeout=1)
    print(f"[OK] Bluetooth conectado en {porta_bt}")
    print("[INFO] Comandos Bluetooth: 'p' = parar, 'c' = continuar")
except Exception as e:
    print(f"[ADVERTENCIA] Bluetooth no disponible: {e}")
    print("[INFO] Sistema funcionando en modo local (sin Bluetooth)")
    bt_serial = None

print("\n[INSTRUCCIONES]")
print("• Cerrar ojos + boca neutra > 1.5s → Alerta ROJA + comando Bluetooth 'p'")
print("• Sonreír con ojos cerrados → NO alerta (algoritmo EAR+MAR funcionando)")
print("• Presione 'c' para salir del programa")
print("-" * 60)

# Configurar FaceMesh de MediaPipe
with mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as facemesh:
    
    # Bucle principal del sistema
    while cap.isOpened():
        sucesso, frame = cap.read()
        if not sucesso:
            print('[ADVERTENCIA] Ignorando frame vacío de la cámara.')
            continue
        
        comprimento, largura, _ = frame.shape

        # Procesar frame para detección facial
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        saida_facemesh = facemesh.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        try:
            # Si se detecta un rostro
            for face_landmarks in saida_facemesh.multi_face_landmarks:
                # Dibujar landmarks faciales (visualización)
                mp_drawing.draw_landmarks(
                    frame, 
                    face_landmarks, 
                    mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(
                        color=(255, 102, 102), 
                        thickness=1, 
                        circle_radius=1
                    ),
                    connection_drawing_spec=mp_drawing.DrawingSpec(
                        color=(102, 204, 0), 
                        thickness=1, 
                        circle_radius=1
                    )
                )
                
                face = face_landmarks.landmark
                
                # Dibujar puntos de interés (ojos y boca)
                for id_coord, coord_xyz in enumerate(face):
                    if id_coord in p_olhos:
                        coord_cv = mp_drawing._normalized_to_pixel_coordinates(
                            coord_xyz.x, coord_xyz.y, largura, comprimento
                        )
                        cv2.circle(frame, coord_cv, 2, (255, 0, 0), -1)
                    
                    if id_coord in p_boca:
                        coord_cv = mp_drawing._normalized_to_pixel_coordinates(
                            coord_xyz.x, coord_xyz.y, largura, comprimento
                        )
                        cv2.circle(frame, coord_cv, 2, (255, 0, 0), -1)

                # Calcular métricas EAR y MAR
                ear = calculo_ear(face, p_olho_dir, p_olho_esq)
                mar = calculo_mar(face, p_boca)
                
                # Panel de información (fondo gris)
                cv2.rectangle(frame, (0, 1), (290, 140), (58, 58, 55), -1)
                
                # Mostrar EAR
                cv2.putText(
                    frame, 
                    f"EAR: {round(ear, 2)}", 
                    (1, 24),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.9, 
                    (255, 255, 255), 
                    2
                )
                
                # Mostrar MAR con estado
                estado_boca = "Abierto" if mar >= mar_limiar else "Cerrado"
                cv2.putText(
                    frame, 
                    f"MAR: {round(mar, 2)} {estado_boca}", 
                    (1, 50),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.9, 
                    (255, 255, 255), 
                    2
                )
                
                # LÓGICA DE DETECCIÓN EAR+MAR (ALGORITMO PRINCIPAL)
                # Condición 1: Posible fatiga (ojos cerrados + boca neutra)
                if ear < ear_limiar and mar < mar_limiar:
                    t_inicial = time.time() if dormindo == 0 else t_inicial
                    contagem_piscadas = contagem_piscadas + 1 if dormindo == 0 else contagem_piscadas
                    dormindo = 1
                
                # Condición 2: Fin de posible fatiga o risa/bostezo
                if (dormindo == 1 and ear >= ear_limiar) or (ear <= ear_limiar and mar >= mar_limiar):
                    dormindo = 0
                
                # Cálculo de tiempo y estadísticas
                t_final = time.time()
                tempo_decorrido = t_final - t_piscadas

                if tempo_decorrido >= (c_tempo + 1):
                    c_tempo = tempo_decorrido
                    piscadas_ps = contagem_piscadas - contagem_temporaria
                    contagem_temporaria = contagem_piscadas
                    contagem_lista.append(piscadas_ps)
                    contagem_lista = contagem_lista if (len(contagem_lista) <= 60) else contagem_lista[-60:]
                
                piscadas_pm = 15 if tempo_decorrido <= 60 else sum(contagem_lista)

                # Mostrar estadísticas
                cv2.putText(
                    frame, 
                    f"Pestaneos: {contagem_piscadas}", 
                    (1, 120),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.9, 
                    (109, 233, 219), 
                    2
                )
                
                tempo = (t_final - t_inicial) if dormindo == 1 else 0.0
                cv2.putText(
                    frame, 
                    f"Tiempo: {round(tempo, 3)}", 
                    (1, 80),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.9, 
                    (255, 255, 255), 
                    2
                )
                
                # CONDICIÓN DE ALERTA: Fatiga detectada
                # 1. Pocos pestaneos por minuto (< 10) O
                # 2. Ojos cerrados por más de 1.5 segundos
                if piscadas_pm < 10 or tempo >= 1.5:
                    # Barra de alerta ROJA
                    cv2.rectangle(frame, (30, 400), (610, 452), (0, 0, 255), -1)
                    cv2.putText(
                        frame, 
                        "Puede ser que esté con sueño,", 
                        (60, 420),
                        cv2.FONT_HERSHEY_DUPLEX, 
                        0.85, 
                        (255, 255, 255), 
                        1
                    )
                    cv2.putText(
                        frame, 
                        "considere descansar.", 
                        (180, 450),
                        cv2.FONT_HERSHEY_DUPLEX, 
                        0.85, 
                        (255, 255, 255), 
                        1
                    )
                    
                    # ENVÍO DE COMANDO BLUETOOTH (si está disponible)
                    if bt_serial:
                        try:
                            bt_serial.write(b"p\n")  # Comando 'p' = PARAR
                            print(f"[BLUETOOTH] Enviado comando 'p' - Vehículo debe detenerse")
                        except Exception as e:
                            print(f"[ERROR] Fallo al enviar por Bluetooth: {e}")
        
        except Exception as e:
            # Manejo de errores en el procesamiento
            pass

        # Mostrar frame en ventana
        cv2.imshow('Sistema de Detección de Fatiga - Código Original', frame)
        
        # Control de teclado: 'c' para salir
        if cv2.waitKey(10) & 0xFF == ord('c'):
            print("\n[INFO] Programa finalizado por el usuario")
            break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

# Cerrar conexión Bluetooth si existe
if bt_serial:
    bt_serial.close()
    print("[INFO] Conexión Bluetooth cerrada")

print("\n" + "=" * 70)
print("RESUMEN DEL SISTEMA:")
print(f"Total de detecciones de posible fatiga: {contagem_piscadas}")
print(f"Parámetros usados: EAR < {ear_limiar}, MAR < {mar_limiar}")
print("=" * 70)
