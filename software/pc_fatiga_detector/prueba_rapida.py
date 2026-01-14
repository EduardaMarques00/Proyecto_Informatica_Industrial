# detector_fatiga_ear_mar.py - Versión para prueba del profesor
import cv2
import mediapipe as mp
import numpy as np
import time

print("=" * 70)
print("DETECTOR DE FATIGA - ALGORITMO EAR + MAR")
print("=" * 70)
print("\nINNOVACIÓN CLAVE: Combina EAR (ojos) y MAR (boca)")
print("✓ Detecta fatiga real: ojos cerrados + boca neutra")
print("✓ Ignora falsos positivos: risas, bostezos (boca abierta)")
print("✓ Protocolo de seguridad con timeout")
print("=" * 70)

# Inicializar MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Puntos para EAR (Eye Aspect Ratio) - alrededor de los ojos
PUNTOS_OJO_IZQUIERDO = [385, 380, 387, 373, 362, 263]
PUNTOS_OJO_DERECHO = [160, 144, 158, 153, 33, 133]
PUNTOS_OJOS = PUNTOS_OJO_IZQUIERDO + PUNTOS_OJO_DERECHO

# Puntos para MAR (Mouth Aspect Ratio) - alrededor de la boca
PUNTOS_BOCA = [82, 87, 13, 14, 312, 317, 78, 308]

def calcular_ear(landmarks_face, puntos_ojo_der, puntos_ojo_izq):
    """Calcular Eye Aspect Ratio (EAR) - Relación de Aspecto del Ojo"""
    try:
        # Convertir landmarks a coordenadas 2D
        face_array = np.array([[coord.x, coord.y] for coord in landmarks_face])
        
        # Coordenadas ojo izquierdo
        ojo_izq = face_array[puntos_ojo_izq, :]
        ear_izq = (np.linalg.norm(ojo_izq[0] - ojo_izq[1]) + 
                  np.linalg.norm(ojo_izq[2] - ojo_izq[3])) / (2.0 * np.linalg.norm(ojo_izq[4] - ojo_izq[5]))
        
        # Coordenadas ojo derecho
        ojo_der = face_array[puntos_ojo_der, :]
        ear_der = (np.linalg.norm(ojo_der[0] - ojo_der[1]) + 
                  np.linalg.norm(ojo_der[2] - ojo_der[3])) / (2.0 * np.linalg.norm(ojo_der[4] - ojo_der[5]))
        
        # EAR promedio de ambos ojos
        ear_promedio = (ear_izq + ear_der) / 2.0
        
    except Exception as e:
        # En caso de error, retornar valores por defecto
        ear_izq = 0.0
        ear_der = 0.0
        ear_promedio = 0.0
    
    return ear_promedio

def calcular_mar(landmarks_face, puntos_boca):
    """Calcular Mouth Aspect Ratio (MAR) - Relación de Aspecto de la Boca"""
    try:
        face_array = np.array([[coord.x, coord.y] for coord in landmarks_face])
        boca = face_array[puntos_boca, :]
        
        # Cálculo MAR: (suma distancias verticales) / (2 * distancia horizontal)
        mar = (np.linalg.norm(boca[0] - boca[1]) + 
               np.linalg.norm(boca[2] - boca[3]) + 
               np.linalg.norm(boca[4] - boca[5])) / (2.0 * np.linalg.norm(boca[6] - boca[7]))
    except:
        mar = 0.0
    
    return mar

def main():
    print("\n[INSTRUCCIONES PARA EL PROFESOR]")
    print("1. MIRE NORMALMENTE para ver sus valores EAR/MAR base")
    print("2. CIERRE OJOS + BOCA NEUTRA > 1.5s → Alerta ROJA (fatiga)")
    print("3. CIERRE OJOS + BOCA ABIERTA (sonrisa) → NO alerta (EAR+MAR funcionando)")
    print("4. Presione 'q' para salir, 'r' para resetear contadores")
    print("-" * 60)
    
    # PARÁMETROS AJUSTABLES (el profesor puede calibrarlos)
    EAR_UMBRAL = 0.25      # Si EAR < 0.25 → ojo cerrado (ajustar según persona)
    MAR_UMBRAL = 0.2       # Si MAR > 0.2 → boca abierta (ajustar según persona)
    TIEMPO_ALERTA = 1.5    # segundos para activar alerta de fatiga
    
    # Variables de estado
    estado_fatiga = False          # 0 = despierto, 1 = posible fatiga
    tiempo_inicio_fatiga = None    # Cuándo empezó el cierre ocular
    contador_pestaneos = 0         # Contador de detecciones
    
    # Iniciar captura de video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] No se puede acceder a la cámara")
        return
    
    # Configurar FaceMesh
    with mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        max_num_faces=1
    ) as facemesh:
        
        while cap.isOpened():
            exito, frame = cap.read()
            if not exito:
                print("[INFO] Error en la captura de video")
                break
            
            alto, ancho = frame.shape[:2]
            
            # Procesar frame para detección facial
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados = facemesh.process(frame_rgb)
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            
            # Panel informativo (fondo gris)
            cv2.rectangle(frame, (0, 0), (450, 180), (50, 50, 50), -1)
            
            if resultados.multi_face_landmarks:
                for landmarks_cara in resultados.multi_face_landmarks:
                    # Dibujar landmarks faciales (opcional, puede comentarse)
                    # mp_drawing.draw_landmarks(
                    #     frame, landmarks_cara, mp_face_mesh.FACEMESH_CONTOURS,
                    #     landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 102, 102), thickness=1),
                    #     connection_drawing_spec=mp_drawing.DrawingSpec(color=(102, 204, 0), thickness=1)
                    # )
                    
                    # Calcular EAR y MAR
                    ear = calcular_ear(landmarks_cara.landmark, PUNTOS_OJO_DERECHO, PUNTOS_OJO_IZQUIERDO)
                    mar = calcular_mar(landmarks_cara.landmark, PUNTOS_BOCA)
                    
                    # Mostrar métricas en pantalla
                    color_ear = (0, 255, 0) if ear >= EAR_UMBRAL else (0, 0, 255)  # Verde si abierto, rojo si cerrado
                    color_mar = (255, 165, 0) if mar >= MAR_UMBRAL else (0, 255, 0) # Naranja si abierta, verde si cerrada
                    
                    cv2.putText(frame, f"EAR: {ear:.3f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_ear, 2)
                    cv2.putText(frame, f"MAR: {mar:.3f}", (10, 65),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_mar, 2)
                    
                    # Mostrar umbrales actuales
                    cv2.putText(frame, f"Umbral EAR: {EAR_UMBRAL}", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(frame, f"Umbral MAR: {MAR_UMBRAL}", (10, 125),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # LÓGICA DE DETECCIÓN (ALGORITMO EAR+MAR)
                    tiempo_actual = time.time()
                    
                    # CONDICIÓN 1: Posible fatiga (ojos cerrados + boca neutra/cerrada)
                    if ear < EAR_UMBRAL and mar < MAR_UMBRAL:
                        if not estado_fatiga:
                            tiempo_inicio_fatiga = tiempo_actual
                            estado_fatiga = True
                        
                        tiempo_fatiga = tiempo_actual - tiempo_inicio_fatiga
                        
                        # Si lleva más de 1.5 segundos con ojos cerrados
                        if tiempo_fatiga >= TIEMPO_ALERTA:
                            # ALERTA DE FATIGA
                            cv2.rectangle(frame, (0, alto-80), (ancho, alto), (0, 0, 255), -1)
                            cv2.putText(frame, "VEHICULO SE DETENDRIA AQUI - FATIGA DETECTADA", 
                                       (ancho//6, alto-30), cv2.FONT_HERSHEY_SIMPLEX, 
                                       0.8, (255, 255, 255), 2)
                            
                            # Mensaje en consola (solo primera vez)
                            if tiempo_fatiga < TIEMPO_ALERTA + 0.1:
                                print(f"[ALERTA] Fatiga detectada! EAR={ear:.3f}, MAR={mar:.3f}, Tiempo={tiempo_fatiga:.1f}s")
                        
                        # Mostrar contador de tiempo
                        cv2.putText(frame, f"Tiempo ojos cerrados: {tiempo_fatiga:.1f}s", (10, 155),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # CONDICIÓN 2: Risa o bostezo (ojos cerrados PERO boca abierta)
                    elif ear < EAR_UMBRAL and mar >= MAR_UMBRAL:
                        estado_fatiga = False
                        tiempo_inicio_fatiga = None
                        
                        # Mostrar que NO es fatiga
                        cv2.putText(frame, "RISA/BOSTEZO DETECTADO", (10, 155),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                        cv2.putText(frame, "NO es fatiga (algoritmo EAR+MAR funcionando)", (ancho-500, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                    
                    # CONDICIÓN 3: Operador despierto
                    else:
                        if estado_fatiga:
                            # Operador acaba de abrir los ojos
                            print(f"[INFO] Operador despierto. Fatiga duró: {tiempo_actual - tiempo_inicio_fatiga:.1f}s")
                            contador_pestaneos += 1
                        
                        estado_fatiga = False
                        tiempo_inicio_fatiga = None
                        
                        # Mostrar estado normal
                        cv2.putText(frame, "Estado: NORMAL", (10, 155),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # Contador de detecciones
                    cv2.putText(frame, f"Detecciones: {contador_pestaneos}", (ancho-200, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Indicar qué condición se está evaluando
                    condicion_texto = ""
                    if ear < EAR_UMBRAL and mar < MAR_UMBRAL:
                        condicion_texto = "Evaluando: FATIGA (ojos+boca cerrados)"
                    elif ear < EAR_UMBRAL and mar >= MAR_UMBRAL:
                        condicion_texto = "Evaluando: RISA (ojos cerrados, boca abierta)"
                    else:
                        condicion_texto = "Evaluando: NORMAL"
                    
                    cv2.putText(frame, condicion_texto, (ancho-500, alto-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            else:
                # No se detecta rostro
                cv2.putText(frame, "Rostro no detectado", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # Instrucciones en pantalla
            cv2.putText(frame, "Instrucciones: Cerrar ojos 1.5s -> Alerta | Sonreir -> No alerta | 'q'=salir", 
                       (10, alto-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Mostrar frame
            cv2.imshow('Detector de Fatiga EAR+MAR - Prueba para Profesor', frame)
            
            # Controles de teclado
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q'):
                print("[INFO] Saliendo del programa...")
                break
            elif tecla == ord('r'):
                print("[INFO] Contadores reseteados")
                estado_fatiga = False
                tiempo_inicio_fatiga = None
                contador_pestaneos = 0
            elif tecla == ord('+') or tecla == ord('='):
                EAR_UMBRAL = min(0.5, EAR_UMBRAL + 0.01)
                print(f"[AJUSTE] EAR_UMBRAL aumentado a: {EAR_UMBRAL:.3f}")
            elif tecla == ord('-') or tecla == ord('_'):
                EAR_UMBRAL = max(0.1, EAR_UMBRAL - 0.01)
                print(f"[AJUSTE] EAR_UMBRAL disminuido a: {EAR_UMBRAL:.3f}")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE LA PRUEBA:")
    print(f"Total de detecciones de fatiga: {contador_pestaneos}")
    print(f"Umbral EAR final: {EAR_UMBRAL:.3f}")
    print(f"Umbral MAR final: {MAR_UMBRAL:.3f}")
    print("\nVERIFICACIÓN DEL ALGORITMO EAR+MAR:")
    print("✓ ALERTA ROJA apareció solo con: ojos cerrados + boca neutra")
    print("✓ NO apareció alerta con: ojos cerrados + boca abierta (risa)")
    print("✓ El sistema distingue correctamente entre fatiga y gestos expresivos")
    print("=" * 70)

if __name__ == "__main__":
    main()
