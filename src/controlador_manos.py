# controlador_manos.py — Controlador por gestos de mano MODIFICADO para Tetris
# VERSIÓN INTEGRADA: Guarda frames para renderizado externo
"""
GESTOS:
-------
• PULGAR ARRIBA MANO DERECHA   → Mover Derecha (un paso)
• PULGAR ARRIBA MANO IZQUIERDA → Mover Izquierda (un paso)
• PULGAR ABAJO (cualquier mano) → Caída Suave (continua mientras se mantiene)
• Dedo índice, medio o anular libre (cualquier mano) → Caída Dura (un disparo)
• SOLO MEÑIQUE extendido (cualquier mano) → ROTAR (un disparo)

NOTA: Las manos están invertidas (espejo manejado internamente)
"""
from __future__ import annotations

import threading
import math
import time
from typing import Tuple, Optional, List

# Silenciar logs
import os, warnings
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")
warnings.filterwarnings("ignore", category=UserWarning, module=r"google\.protobuf")
try:
    from absl import logging as absl_logging
    absl_logging.set_verbosity(absl_logging.ERROR)
except Exception:
    pass

try:
    import cv2
    import mediapipe as mp
    MEDIAPIPE_DISPONIBLE = True
except Exception:
    MEDIAPIPE_DISPONIBLE = False


class ControladorMano:
    """Controlador de gestos de mano para Tetris."""

    def __init__(
        self,
        indice_cam: int = 0,
        ancho: int = 640,
        alto: int = 480,
        dist_min_dedo: float = 0.15,
        umbral_dir_pulgar: float = 0.10,
        pose_activar_ms: int = 220,
        pose_desactivar_ms: int = 120,
        rotar_debounce_s: float = 0.18,
        caida_dura_debounce_s: float = 0.5,
        movimiento_debounce_s: float = 0.18,
        mostrar_camara: bool = False,  # Ahora por defecto False
        espejar_previsualizacion: bool = False,
        escala_previsualizacion: float = 1.5,
        depurar: bool = False,
    ) -> None:
        if not MEDIAPIPE_DISPONIBLE:
            raise RuntimeError("MediaPipe / OpenCV no disponibles")

        self.ancho = ancho
        self.alto = alto
        self.dist_min_dedo = dist_min_dedo
        self.umbral_dir_pulgar = umbral_dir_pulgar
        self.pose_activar_ms = pose_activar_ms
        self.pose_desactivar_ms = pose_desactivar_ms
        self.rotar_debounce_s = rotar_debounce_s
        self.caida_dura_debounce_s = caida_dura_debounce_s
        self.movimiento_debounce_s = movimiento_debounce_s
        self.mostrar_camara = mostrar_camara
        self.espejar_previsualizacion = espejar_previsualizacion
        self.escala_previsualizacion = escala_previsualizacion
        self.depurar = depurar

        # Cámara
        self.cap = cv2.VideoCapture(indice_cam)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, ancho)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, alto)

        # MediaPipe
        self.mp_manos = mp.solutions.hands
        self.mp_dibujar = mp.solutions.drawing_utils
        self.mp_estilo = mp.solutions.drawing_styles
        self.manos = self.mp_manos.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        # Estado público
        self.dir_mov: int = 0
        self.caida_suave: bool = False
        self.borde_rotar_hor: bool = False
        self.borde_caida_dura: bool = False
        
        # NUEVO: Frame actual para renderizado externo
        self.ultimo_frame = None
        self._lock_frame = threading.Lock()

        # Estado interno para debouncing
        self._izq_armado: bool = True
        self._der_armado: bool = True
        self._rotar_armado: bool = True
        self._caida_dura_armado: bool = True
        
        self._ultimo_tiempo_rotar: float = 0.0
        self._ultimo_tiempo_caida_dura: float = 0.0
        self._ultimo_tiempo_izq: float = 0.0
        self._ultimo_tiempo_der: float = 0.0

        # HUD
        self._pasos_izq: int = 0
        self._pasos_der: int = 0
        self._contador_rotar: int = 0
        self._contador_caida_dura: int = 0
        self._rotar_destellar_hasta: float = 0.0
        self._caida_dura_destellar_hasta: float = 0.0

        # Hilo
        self._ejecutando = False
        self._hilo = threading.Thread(target=self._bucle, daemon=True)

    def iniciar(self) -> None:
        """Iniciar el bucle de cámara en segundo plano."""
        self._ejecutando = True
        self._hilo.start()

    def detener(self) -> None:
        """Detener el bucle y limpiar recursos."""
        self._ejecutando = False
        try:
            self._hilo.join(timeout=1.0)
        except Exception:
            pass
        try:
            self.manos.close()
        except Exception:
            pass
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception:
            pass
        try:
            if self.mostrar_camara:
                cv2.destroyAllWindows()
        except Exception:
            pass

    def consultar(self) -> Tuple[int, bool, bool, bool]:
        """Retorna (dir_mov, caida_suave, borde_rotar, borde_caida_dura)."""
        brh = self.borde_rotar_hor
        bcd = self.borde_caida_dura
        self.borde_rotar_hor = False
        self.borde_caida_dura = False
        return self.dir_mov, self.caida_suave, brh, bcd

    @staticmethod
    def _distancia(a, b) -> float:
        """Distancia euclidiana entre dos puntos."""
        return math.hypot(a.x - b.x, a.y - b.y)

    def _es_dedo_extendido(self, lm, id_punta: int, id_pip: int, id_mcp: int) -> bool:
        """Verifica si un dedo está extendido usando distancia uniforme."""
        punta, pip, mcp = lm[id_punta], lm[id_pip], lm[id_mcp]
        return (punta.y < pip.y - 0.008) and (math.hypot(punta.x - mcp.x, punta.y - mcp.y) >= self.dist_min_dedo)

    def _contar_dedos_extendidos(self, lm) -> Tuple[bool, bool, bool, bool]:
        """Retorna (índice, medio, anular, meñique) extendidos."""
        ind = self._es_dedo_extendido(lm, 8, 6, 5)
        med = self._es_dedo_extendido(lm, 12, 10, 9)
        anl = self._es_dedo_extendido(lm, 16, 14, 13)
        men = self._es_dedo_extendido(lm, 20, 18, 17)
        return ind, med, anl, men

    def _pulgar_arriba_abajo(self, lm) -> Tuple[bool, bool]:
        """Detecta pulgar arriba o abajo."""
        punta, ip_, mcp = lm[4], lm[3], lm[2]
        vy = punta.y - mcp.y
        vx = punta.x - mcp.x
        punta_vs_ip = punta.y - ip_.y

        suficientemente_vertical = abs(vy) > abs(vx) * 0.6

        abajo = (vy >= self.umbral_dir_pulgar) and (punta_vs_ip > 0.005) and suficientemente_vertical
        arriba = (vy <= -self.umbral_dir_pulgar) and (punta_vs_ip < -0.005) and suficientemente_vertical
        return arriba, abajo

    def _pulgar_extendido(self, lm) -> bool:
        """Detecta si el pulgar está extendido."""
        punta, mcp = lm[4], lm[2]
        muneca = lm[0]
        dist = math.hypot(punta.x - muneca.x, punta.y - muneca.y)
        return dist >= self.dist_min_dedo

    def _bucle(self) -> None:
        """Bucle principal de detección."""
        if self.mostrar_camara:
            cv2.namedWindow("Cámara Mano", cv2.WINDOW_NORMAL)
            try:
                cv2.resizeWindow(
                    "Cámara Mano",
                    int(self.ancho * self.escala_previsualizacion),
                    int(self.alto * self.escala_previsualizacion),
                )
            except Exception:
                pass

        tiempo_previo = time.time()
        fps = 0.0

        while self._ejecutando:
            ok, cuadro_bgr = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            ahora_cuadro = time.time()
            dt = ahora_cuadro - tiempo_previo
            tiempo_previo = ahora_cuadro
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt)

            dibujar_bgr = cuadro_bgr.copy()
            cuadro_rgb = cv2.cvtColor(cuadro_bgr, cv2.COLOR_BGR2RGB)
            resultados = self.manos.process(cuadro_rgb)

            # Reiniciar intenciones
            self.dir_mov = 0
            self.caida_suave = False

            ahora = time.time()

            mano_izq_usuario = None
            mano_der_usuario = None

            if resultados.multi_hand_landmarks:
                for idx, mano_lms in enumerate(resultados.multi_hand_landmarks):
                    etiqueta_camara = None
                    if hasattr(resultados, 'multi_handedness') and resultados.multi_handedness:
                        if idx < len(resultados.multi_handedness):
                            md = resultados.multi_handedness[idx]
                            if hasattr(md, 'classification') and len(md.classification):
                                etiqueta_camara = md.classification[0].label

                    lm = mano_lms.landmark
                    ind, med, anl, men = self._contar_dedos_extendidos(lm)
                    pulgar_arriba, pulgar_abajo = self._pulgar_arriba_abajo(lm)
                    pulgar_ext = self._pulgar_extendido(lm)

                    datos_mano = {
                        'lm': lm,
                        'landmarks': mano_lms,
                        'pulgar_arriba': pulgar_arriba,
                        'pulgar_abajo': pulgar_abajo,
                        'pulgar_extendido': pulgar_ext,
                        'ind': ind,
                        'med': med,
                        'anl': anl,
                        'men': men,
                        'solo_menique': men and not ind and not med and not anl,
                    }

                    if etiqueta_camara == 'Left':
                        mano_der_usuario = datos_mano
                    elif etiqueta_camara == 'Right':
                        mano_izq_usuario = datos_mano

                    # Dibujar landmarks
                    self.mp_dibujar.draw_landmarks(
                        dibujar_bgr,
                        mano_lms,
                        self.mp_manos.HAND_CONNECTIONS,
                        self.mp_estilo.get_default_hand_landmarks_style(),
                        self.mp_estilo.get_default_hand_connections_style(),
                    )

            # ===== PROCESAR GESTOS =====
            dedo_libre_detectado = False
            
            if mano_izq_usuario:
                dedos_sin_menique = [mano_izq_usuario['ind'], mano_izq_usuario['med'], 
                                     mano_izq_usuario['anl']]
                if sum(dedos_sin_menique) == 1 and not mano_izq_usuario['men']:
                    if not mano_izq_usuario['pulgar_arriba'] and not mano_izq_usuario['pulgar_abajo']:
                        dedo_libre_detectado = True
            
            if mano_der_usuario:
                dedos_sin_menique = [mano_der_usuario['ind'], mano_der_usuario['med'], 
                                     mano_der_usuario['anl']]
                if sum(dedos_sin_menique) == 1 and not mano_der_usuario['men']:
                    if not mano_der_usuario['pulgar_arriba'] and not mano_der_usuario['pulgar_abajo']:
                        dedo_libre_detectado = True

            if dedo_libre_detectado:
                if self._caida_dura_armado and (ahora - self._ultimo_tiempo_caida_dura) >= self.caida_dura_debounce_s:
                    self.borde_caida_dura = True
                    self._ultimo_tiempo_caida_dura = ahora
                    self._caida_dura_destellar_hasta = ahora + 0.40
                    self._contador_caida_dura += 1
                    self._caida_dura_armado = False
            else:
                self._caida_dura_armado = True

            solo_menique_izq = (mano_izq_usuario and mano_izq_usuario['solo_menique'] 
                               and not dedo_libre_detectado)
            solo_menique_der = (mano_der_usuario and mano_der_usuario['solo_menique']
                               and not dedo_libre_detectado)
            solo_menique_detectado = solo_menique_izq or solo_menique_der

            if solo_menique_detectado and not dedo_libre_detectado:
                if self._rotar_armado and (ahora - self._ultimo_tiempo_rotar) >= self.rotar_debounce_s:
                    self.borde_rotar_hor = True
                    self._ultimo_tiempo_rotar = ahora
                    self._rotar_destellar_hasta = ahora + 0.30
                    self._contador_rotar += 1
                    self._rotar_armado = False
            else:
                self._rotar_armado = True

            if (mano_izq_usuario and mano_izq_usuario['pulgar_arriba'] 
                and not solo_menique_izq 
                and not dedo_libre_detectado):
                if self._izq_armado and (ahora - self._ultimo_tiempo_izq) >= self.movimiento_debounce_s:
                    self.dir_mov = -1
                    self._pasos_izq += 1
                    self._ultimo_tiempo_izq = ahora
                    self._izq_armado = False
            else:
                self._izq_armado = True

            if (mano_der_usuario and mano_der_usuario['pulgar_arriba'] 
                and not solo_menique_der 
                and not dedo_libre_detectado):
                if self._der_armado and (ahora - self._ultimo_tiempo_der) >= self.movimiento_debounce_s:
                    self.dir_mov = 1
                    self._pasos_der += 1
                    self._ultimo_tiempo_der = ahora
                    self._der_armado = False
            else:
                self._der_armado = True

            pulgar_abajo_detectado = False
            if not dedo_libre_detectado:
                if mano_izq_usuario and mano_izq_usuario['pulgar_abajo']:
                    pulgar_abajo_detectado = True
                if mano_der_usuario and mano_der_usuario['pulgar_abajo']:
                    pulgar_abajo_detectado = True
            self.caida_suave = pulgar_abajo_detectado

            # ===== GUARDAR FRAME PARA RENDERIZADO EXTERNO =====
            with self._lock_frame:
                self.ultimo_frame = dibujar_bgr.copy()

            # ===== HUD (solo si mostrar_camara está activado) =====
            if self.mostrar_camara:
                def poner(y, texto):
                    cv2.putText(dibujar_bgr, texto, (8, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1, cv2.LINE_AA)

                poner(24,  f"IZQUIERDA: {self._pasos_izq} | Armado: {'SI' if self._izq_armado else 'NO'}")
                poner(48,  f"DERECHA: {self._pasos_der} | Armado: {'SI' if self._der_armado else 'NO'}")
                
                rotar_on = (time.time() <= self._rotar_destellar_hasta)
                poner(72,  f"ROTAR: {self._contador_rotar} | {'ACTIVO!' if rotar_on else 'listo'}")
                
                caida_dura_on = (time.time() <= self._caida_dura_destellar_hasta)
                poner(96,  f"CAIDA DURA: {self._contador_caida_dura} | {'ACTIVO!' if caida_dura_on else 'listo'}")
                
                poner(120, f"Caida Suave: {'ACTIVA' if self.caida_suave else 'inactiva'}")
                poner(144, f"Manos: Izq={'SI' if mano_izq_usuario else 'NO'} | Der={'SI' if mano_der_usuario else 'NO'} | FPS: {fps:4.1f}")

                if self.espejar_previsualizacion:
                    dibujar_bgr = cv2.flip(dibujar_bgr, 1)

                cv2.imshow("Cámara Mano", dibujar_bgr)

                tecla = cv2.waitKey(1) & 0xFF
                if tecla == ord('q'):
                    self.detener()
                    return
                elif tecla == ord('m'):
                    self.espejar_previsualizacion = not self.espejar_previsualizacion

            time.sleep(1/60.0)


def crear_controlador_manos_o_nada(mostrar_camara: bool = False, espejo: bool = False, **kwargs) -> Optional[ControladorMano]:
    """Crea y retorna un controlador de manos o None si falla."""
    if not MEDIAPIPE_DISPONIBLE:
        return None
    try:
        cm = ControladorMano(mostrar_camara=mostrar_camara, espejar_previsualizacion=espejo, **kwargs)
        cm.iniciar()
        return cm
    except Exception:
        return None


if __name__ == "__main__":
    ctrl = crear_controlador_manos_o_nada(mostrar_camara=True, espejo=False)
    if ctrl is None:
        print("Falló al iniciar ControladorMano")
    else:
        print("Controlador ejecutándose. Presiona 'q' para salir.")
        try:
            while True:
                resultado = ctrl.consultar()
                if any(resultado):
                    print(resultado)
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            ctrl.detener()