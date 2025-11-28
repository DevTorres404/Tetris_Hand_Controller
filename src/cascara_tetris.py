import pygame
import sys
import time
import os
import urllib.request
import numpy as np
from core_tetris import Motor, TETROMINOS
from controlador_manos import crear_controlador_manos_o_nada

# ============================================================
#                       CONFIGURACIÓN VISUAL
# ============================================================
COLUMNAS, FILAS = 10, 20
CELDA = 35  
ANCHO_LATERAL = 8 * CELDA 
ANCHO, ALTO = COLUMNAS * CELDA + ANCHO_LATERAL, FILAS * CELDA + 40  
FPS = 30

CAMARA_ANCHO = 280  
CAMARA_ALTO = 210   
CAMARA_MARGEN = 15  
CAMARA_POS_X = COLUMNAS * CELDA + 25  
CAMARA_POS_Y = CAMARA_MARGEN + 20  

NEGRO = (15, 15, 25)
CUADRICULA = (60, 65, 90)
BLANCO = (245, 250, 255)
GRIS = (75, 80, 100)

COLORES_PIEZAS = {
    "I": (0, 240, 255),
    "O": (255, 215, 0),
    "T": (200, 50, 255),
    "S": (50, 255, 100),
    "Z": (255, 60, 100),
    "J": (70, 130, 255),
    "L": (255, 140, 40),
}

COLOR_FONDO_MENU = (20, 25, 40)
COLOR_OVERLAY = (10, 15, 30, 200)
COLOR_TEXTO_PRINCIPAL = (245, 250, 255)
COLOR_TEXTO_SECUNDARIO = (180, 190, 210)
COLOR_ACENTO = (100, 200, 255)

DIRECTORIO_SONIDOS = "Sound_Effects"

GRAVEDAD_BASE_S = 0.8
INTERVALO_CAIDA_SUAVE_S = 0.2

# ============================================================
#                      RENDERIZADO
# ============================================================
class RenderizadorTetris:
    """Maneja todo el renderizado visual del juego."""
    
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("Consolas", 16)
        self.fuente_grande = pygame.font.SysFont("Consolas", 36, bold=True)
        self.fuente_media = pygame.font.SysFont("Consolas", 22)
        self.fuente_pequena = pygame.font.SysFont("Consolas", 12)
    
    def dibujar_tablero(self, tablero):
        self.pantalla.fill(NEGRO)
        margen_y = 20
        for y in range(FILAS):
            for x in range(COLUMNAS):
                rect = pygame.Rect(x * CELDA, y * CELDA + margen_y, CELDA, CELDA)
                if tablero[y][x] is not None:
                    color = COLORES_PIEZAS.get(tablero[y][x], BLANCO)
                    pygame.draw.rect(self.pantalla, color, rect)
                    color_oscuro = tuple(max(0, c - 40) for c in color)
                    pygame.draw.rect(self.pantalla, color_oscuro, rect, 2)
                else:
                    pygame.draw.rect(self.pantalla, CUADRICULA, rect, 1)
    
    def dibujar_pieza(self, pieza):
        if pieza is None:
            return
        margen_y = 20
        color = COLORES_PIEZAS.get(pieza.tipo, BLANCO)
        for (x, y) in pieza.celdas():
            if y >= 0:
                rect = pygame.Rect(x * CELDA, y * CELDA + margen_y, CELDA, CELDA)
                pygame.draw.rect(self.pantalla, color, rect)
                color_claro = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(self.pantalla, color_claro, rect, 3)
    
    def dibujar_camara(self, frame_bgr):
        if frame_bgr is None:
            return
        
        try:
            frame_rgb = frame_bgr[:, :, ::-1]
            h, w = frame_rgb.shape[:2]
            if w != CAMARA_ANCHO or h != CAMARA_ALTO:
                import cv2
                frame_rgb = cv2.resize(frame_rgb, (CAMARA_ANCHO, CAMARA_ALTO))
            
            frame_surface = pygame.surfarray.make_surface(
                np.transpose(frame_rgb, (1, 0, 2))
            )
            
            borde_rect = pygame.Rect(
                CAMARA_POS_X - 2, 
                CAMARA_POS_Y - 2, 
                CAMARA_ANCHO + 4, 
                CAMARA_ALTO + 4
            )
            pygame.draw.rect(self.pantalla, COLOR_ACENTO, borde_rect, 2)
            
            self.pantalla.blit(frame_surface, (CAMARA_POS_X, CAMARA_POS_Y))
            
            etiqueta = self.fuente_pequena.render("CÁMARA", True, COLOR_ACENTO)
            etiqueta_rect = etiqueta.get_rect()
            etiqueta_rect.centerx = CAMARA_POS_X + CAMARA_ANCHO // 2
            etiqueta_rect.bottom = CAMARA_POS_Y - 4
            self.pantalla.blit(etiqueta, etiqueta_rect)
            
        except Exception as e:
            rect = pygame.Rect(CAMARA_POS_X, CAMARA_POS_Y, CAMARA_ANCHO, CAMARA_ALTO)
            pygame.draw.rect(self.pantalla, (40, 40, 60), rect)
            pygame.draw.rect(self.pantalla, COLOR_ACENTO, rect, 2)
            texto = self.fuente_pequena.render("Cámara no disponible", True, COLOR_TEXTO_SECUNDARIO)
            texto_rect = texto.get_rect(center=rect.center)
            self.pantalla.blit(texto, texto_rect)
    
    def dibujar_hud(self, estado, mano_activa):
        x_base = COLUMNAS * CELDA + 15  
        y = CAMARA_POS_Y + CAMARA_ALTO + 30
        
        titulo_lineas = [
            ("Puntaje: ", COLOR_TEXTO_SECUNDARIO, f"{estado['puntaje']}", COLOR_ACENTO),
            ("Líneas: ", COLOR_TEXTO_SECUNDARIO, f"{estado['lineas']}", COLOR_ACENTO),
            ("Nivel: ", COLOR_TEXTO_SECUNDARIO, f"{estado['nivel']}", COLOR_ACENTO),
        ]
        
        for label, color_label, valor, color_valor in titulo_lineas:
            txt_label = self.fuente.render(label, True, color_label)
            txt_valor = self.fuente.render(valor, True, color_valor)
            self.pantalla.blit(txt_label, (x_base, y))
            self.pantalla.blit(txt_valor, (x_base + txt_label.get_width(), y))
            y += self.fuente.get_linesize() + 4  
        
        y += 12  
        
        estado_mano = "Manos: ON" if mano_activa else "Manos: OFF"
        color_mano = (50, 255, 100) if mano_activa else (255, 100, 100)
        txt = self.fuente.render(estado_mano, True, color_mano)
        self.pantalla.blit(txt, (x_base, y))
        y += self.fuente.get_linesize() + 12
        
        lineas_info = [
            ("TECLADO:", COLOR_ACENTO),
            ("← → : Mover", COLOR_TEXTO_PRINCIPAL),
            ("↑ X : Rotar", COLOR_TEXTO_PRINCIPAL),
            ("↓ : Caída Suave", COLOR_TEXTO_PRINCIPAL),
            ("SPACE : Caída Dura", COLOR_TEXTO_PRINCIPAL),
            ("", COLOR_TEXTO_PRINCIPAL),
            ("GESTOS:", COLOR_ACENTO),
            ("Pulgar↑ L/R : Mover", COLOR_TEXTO_SECUNDARIO),
            ("Solo Meñique : Rotar", COLOR_TEXTO_SECUNDARIO),
            ("Pulgar↓ : Suave", COLOR_TEXTO_SECUNDARIO),
            ("Cualquier dedo libre : Dura", COLOR_TEXTO_SECUNDARIO),
        ]
        
        for linea, color in lineas_info:
            txt = self.fuente.render(linea, True, color)
            self.pantalla.blit(txt, (x_base, y))
            y += self.fuente.get_linesize() + 3

    def barrido_game_over(self, tablero):
        self.dibujar_tablero(tablero)
        pygame.display.flip()
        
        margen_y = 20
        retraso_ms = 12
        for y in range(FILAS - 1, -1, -1):
            for x in range(COLUMNAS):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                rect = pygame.Rect(x * CELDA, y * CELDA + margen_y, CELDA, CELDA)
                pygame.draw.rect(self.pantalla, (40, 40, 60), rect)
                pygame.draw.rect(self.pantalla, CUADRICULA, rect, 1)
                pygame.display.update(rect)
                pygame.time.wait(retraso_ms)
    
    def input_nombre(self):
        """Pantalla para ingresar el nombre del jugador."""
        nombre = ""
        activo = True
        
        while activo:
            cx, cy = self.pantalla.get_rect().center
            self.pantalla.fill(COLOR_FONDO_MENU)
            
            titulo = self.fuente_grande.render("NUEVO JUEGO", True, COLOR_ACENTO)
            instruccion = self.fuente.render("Ingresa tu nombre:", True, COLOR_TEXTO_SECUNDARIO)
            
            input_box = pygame.Rect(cx - 100, cy, 200, 32)
            pygame.draw.rect(self.pantalla, (30, 35, 50), input_box)
            pygame.draw.rect(self.pantalla, COLOR_ACENTO, input_box, 2)
            
            texto_surf = self.fuente_media.render(nombre, True, BLANCO)
            self.pantalla.blit(texto_surf, (input_box.x + 5, input_box.y + 5))
            
            ayuda = self.fuente_pequena.render("Presiona ENTER para confirmar", True, (100, 255, 150))
            
            self.pantalla.blit(titulo, titulo.get_rect(center=(cx, cy - 60)))
            self.pantalla.blit(instruccion, instruccion.get_rect(center=(cx, cy - 25)))
            self.pantalla.blit(ayuda, ayuda.get_rect(center=(cx, cy + 50)))
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if not nombre.strip():
                            nombre = "Jugador"
                        activo = False
                    elif event.key == pygame.K_BACKSPACE:
                        nombre = nombre[:-1]
                    else:
                        if len(nombre) < 12: 
                            nombre += event.unicode
        return nombre

    def menu_game_over(self, puntaje, lineas, nivel, nombre_jugador):
        superposicion = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        superposicion.fill(COLOR_OVERLAY)
        self.pantalla.blit(superposicion, (0, 0))
        
        titulo = self.fuente_grande.render("GAME OVER", True, (255, 100, 100))
        
        nombre_txt = self.fuente_media.render(f"JUGADOR: {nombre_jugador}", True, BLANCO)
        
        stats = self.fuente_media.render(
            f"Pts: {puntaje} | Lín: {lineas} | Niv: {nivel}",
            True, COLOR_ACENTO
        )
        ayuda1 = self.fuente.render("Presiona R para Reiniciar", True, (100, 255, 150))
        ayuda2 = self.fuente.render("Presiona Q o Esc para Salir", True, COLOR_TEXTO_SECUNDARIO)
        
        cx, cy = ANCHO // 2, ALTO // 2
        
        self.pantalla.blit(titulo, titulo.get_rect(center=(cx, cy - 80)))
        self.pantalla.blit(nombre_txt, nombre_txt.get_rect(center=(cx, cy - 30)))
        self.pantalla.blit(stats, stats.get_rect(center=(cx, cy + 10)))
        self.pantalla.blit(ayuda1, ayuda1.get_rect(center=(cx, cy + 60)))
        self.pantalla.blit(ayuda2, ayuda2.get_rect(center=(cx, cy + 90)))
        
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        return False
                    if event.key == pygame.K_r:
                        return True
    
    def pantalla_carga(self, mensaje, tiene_mano):
        cx, cy = self.pantalla.get_rect().center
        self.pantalla.fill(COLOR_FONDO_MENU)
        titulo = self.fuente_grande.render("TETRIS", True, COLOR_ACENTO)
        estado = self.fuente.render(mensaje, True, COLOR_TEXTO_SECUNDARIO)
        ayuda = self.fuente.render("Presiona ENTER para comenzar", True, (100, 255, 150))
        self.pantalla.blit(titulo, titulo.get_rect(center=(cx, cy - 60)))
        self.pantalla.blit(estado, estado.get_rect(center=(cx, cy - 10)))
        self.pantalla.blit(ayuda, ayuda.get_rect(center=(cx, cy + 30)))
        pygame.display.flip()

class GestorAudio:
    """Carga audios locales desde la carpeta Sound_Effects (hermana de src)."""

    def __init__(self):
        self.sonidos = {}
        self.audio_disponible = True
        self._cargar_sonidos()

    def _cargar_sonidos(self):
        try:
            if '__file__' in globals():
                dir_actual = os.path.dirname(os.path.abspath(__file__))
            else:
                dir_actual = os.getcwd()

            ruta_sonidos = os.path.join(dir_actual, "..", "Sound_Effects")
            ruta_sonidos = os.path.abspath(ruta_sonidos)

            print(f"--- Buscando sonidos en: {ruta_sonidos} ---")

            if not os.path.exists(ruta_sonidos):
                print(f"[ERROR] No encuentro la carpeta de sonidos en: {ruta_sonidos}")
                self.audio_disponible = False
                return

            archivos = [
                "4_lines.wav", "background.wav", "game_over.wav", 
                "level_up.wav", "line.wav", "move.wav", 
                "piece_landed.wav", "rotate.wav"
            ]

            sonidos_cargados = 0
            for nombre in archivos:
                ruta_completa = os.path.join(ruta_sonidos, nombre)
                
                if os.path.exists(ruta_completa):
                    try:
                        if nombre == "background.wav":
                            pygame.mixer.music.load(ruta_completa)
                        else:
                            self.sonidos[nombre] = pygame.mixer.Sound(ruta_completa)
                        sonidos_cargados += 1
                        print(f"[OK] {nombre}")
                    except Exception as e:
                        print(f"[FALLO] {nombre}: {e}")
                else:
                    print(f"[FALTA] {nombre}")

            if sonidos_cargados == 0:
                print("[ADVERTENCIA] No se cargaron sonidos.")
                self.audio_disponible = False

        except Exception as e:
            print(f"[ERROR CRITICO] Audio deshabilitado: {e}")
            self.audio_disponible = False

    def reproducir(self, nombre):
        if self.audio_disponible and nombre in self.sonidos:
            try:
                self.sonidos[nombre].play()
            except:
                pass
    
    def iniciar_musica(self):
        if self.audio_disponible:
            try:
                pygame.mixer.music.play(-1)
            except:
                pass
    
    def detener_musica(self):
        try:
            pygame.mixer.music.stop()
        except:
            pass

# ============================================================
#                    BUCLE PRINCIPAL DEL JUEGO
# ============================================================
def ejecutar_juego(mano=None):
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Tetris — Controles Teclado + Mano")
    reloj = pygame.time.Clock()
    
    motor = Motor(COLUMNAS, FILAS, GRAVEDAD_BASE_S)
    render = RenderizadorTetris(pantalla)
    audio = GestorAudio()
    
    # 1. Solicitar Nombre del Jugador
    nombre_jugador = render.input_nombre()
    
    # 2. Pantalla de carga / instrucciones
    mensaje = ("Control por gestos activado" if mano else "Modo solo teclado")
    render.pantalla_carga(mensaje, mano is not None)
    
    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    esperando = False
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
    
    audio.iniciar_musica()
    
    ultima_gravedad = time.time()
    caida_suave_teclado = False
    caida_suave_mano = False
    ultima_caida_suave = time.time()
    
    mover_izq = mover_der = False
    retraso_repeticion = 0.15
    ultimo_mov = 0.0
    
    nivel_anterior = 1
    
    ejecutando = True
    while ejecutando and not motor.game_over:
        ahora = time.time()
        reloj.tick(FPS)
        
        # EVENTOS TECLADO
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if motor.mover(-1, 0):
                        audio.reproducir('move.wav')
                    mover_izq = True
                    ultimo_mov = ahora
                
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if motor.mover(1, 0):
                        audio.reproducir('move.wav')
                    mover_der = True
                    ultimo_mov = ahora
                
                elif event.key in (pygame.K_UP, pygame.K_x):
                    if motor.rotar(1):
                        audio.reproducir('rotate.wav')
                
                elif event.key == pygame.K_z:
                    if motor.rotar(-1):
                        audio.reproducir('rotate.wav')
                
                elif event.key == pygame.K_DOWN:
                    caida_suave_teclado = True
                
                elif event.key == pygame.K_SPACE:
                    filas = motor.caida_dura()
                    audio.reproducir('piece_landed.wav')
                    
                    estado = motor.obtener_estado()
                    if estado['lineas'] >= 4:
                        audio.reproducir('4_lines.wav')
                    elif estado['lineas'] > 0:
                        audio.reproducir('line.wav')
                    
                    if estado['nivel'] > nivel_anterior:
                        audio.reproducir('level_up.wav')
                        nivel_anterior = estado['nivel']
                    
                    ultima_gravedad = ahora
            
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    mover_izq = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    mover_der = False
                elif event.key == pygame.K_DOWN:
                    caida_suave_teclado = False
        
        # INPUT MANOS
        frame_camara = None
        if mano is not None:
            dir_mov, caida_suave_m, rotar_borde, caida_dura_borde = mano.consultar()
            
            try:
                frame_camara = mano.ultimo_frame
            except:
                frame_camara = None
            
            if dir_mov == -1:
                if motor.mover(-1, 0):
                    audio.reproducir('move.wav')
            elif dir_mov == 1:
                if motor.mover(1, 0):
                    audio.reproducir('move.wav')
            
            if rotar_borde:
                if motor.rotar(1):
                    audio.reproducir('rotate.wav')
            
            if caida_dura_borde:
                filas = motor.caida_dura()
                audio.reproducir('piece_landed.wav')
                
                estado = motor.obtener_estado()
                lineas_nuevas = estado['lineas']
                
                if lineas_nuevas == 4:
                    audio.reproducir('4_lines.wav')
                elif lineas_nuevas > 0:
                    audio.reproducir('line.wav')
                
                if estado['nivel'] > nivel_anterior:
                    audio.reproducir('level_up.wav')
                    nivel_anterior = estado['nivel']
                
                ultima_gravedad = ahora
            
            caida_suave_mano = bool(caida_suave_m)
        
        # REPETICIÓN TECLAS
        if mover_izq or mover_der:
            if ahora - ultimo_mov >= retraso_repeticion:
                if mover_izq and motor.mover(-1, 0):
                    audio.reproducir('move.wav')
                    ultimo_mov = ahora
                if mover_der and motor.mover(1, 0):
                    audio.reproducir('move.wav')
                    ultimo_mov = ahora
        
        # CAÍDA SUAVE
        caida_suave_activa = caida_suave_teclado or caida_suave_mano
        if caida_suave_activa and (ahora - ultima_caida_suave) >= INTERVALO_CAIDA_SUAVE_S:
            motor.caida_suave()
            ultima_caida_suave = ahora
        
        # GRAVEDAD
        gravedad_s = motor.gravedad_actual()
        if caida_suave_activa:
            gravedad_s *= 0.15
        
        if ahora - ultima_gravedad >= gravedad_s:
            if not motor.caida_suave():
                estado_anterior = motor.obtener_estado()
                motor._fijar_pieza()
                audio.reproducir('piece_landed.wav')
                
                estado = motor.obtener_estado()
                lineas_nuevas = estado['lineas'] - estado_anterior['lineas']
                
                if lineas_nuevas == 4:
                    audio.reproducir('4_lines.wav')
                elif lineas_nuevas > 0:
                    audio.reproducir('line.wav')
                
                if estado['nivel'] > nivel_anterior:
                    audio.reproducir('level_up.wav')
                    nivel_anterior = estado['nivel']
            
            ultima_gravedad = ahora
        
        # DIBUJAR
        estado = motor.obtener_estado()
        render.dibujar_tablero(estado['tablero'])
        render.dibujar_pieza(estado['pieza_actual'])
        render.dibujar_hud(estado, mano is not None)
        
        if mano is not None and frame_camara is not None:
            render.dibujar_camara(frame_camara)
        
        pygame.display.flip()
    
    # GAME OVER
    audio.detener_musica()
    audio.reproducir('game_over.wav')
    
    estado_final = motor.obtener_estado()
    render.barrido_game_over(estado_final['tablero'])
    
    return render.menu_game_over(
        estado_final['puntaje'],
        estado_final['lineas'],
        estado_final['nivel'],
        nombre_jugador  # Pasamos el nombre aquí
    )

# ============================================================
#                          MAIN
# ============================================================
def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    
    mano = crear_controlador_manos_o_nada(mostrar_camara=False, espejo=False)
    
    while True:
        reiniciar = ejecutar_juego(mano)
        if not reiniciar:
            break
    
    if mano is not None:
        try:
            mano.detener()
        except:
            pass
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
