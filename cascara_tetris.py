# =============================================================================
#                    INTERFAZ Y PRESENTACIÓN DEL TETRIS
# =============================================================================
# Este módulo maneja toda la visualización, sonidos, controles y flujo de UI
# usando pygame. Depende de Core_Tetris.py para la lógica del juego.

import pygame
import sys
import time
import os
from core_tetris import Motor, TETROMINOS
from controlador_manos import crear_controlador_manos_o_nada
# ============================================================
#                      CONFIGURACIÓN VISUAL
# ============================================================
COLUMNAS, FILAS = 10, 20
CELDA = 30
ANCHO_LATERAL = 6 * CELDA
ANCHO, ALTO = COLUMNAS * CELDA + ANCHO_LATERAL, FILAS * CELDA
FPS = 30


NEGRO = (15, 15, 25)  # Azul oscuro profundo
CUADRICULA = (60, 65, 90)  # Gris azulado
BLANCO = (245, 250, 255)  # Blanco con tinte azul
GRIS = (75, 80, 100)  # Gris medio


COLORES_PIEZAS = {
    "I": (0, 240, 255),      # Cyan brillante
    "O": (255, 215, 0),      # Oro
    "T": (200, 50, 255),     # Púrpura neón
    "S": (50, 255, 100),     # Verde esmeralda
    "Z": (255, 60, 100),     # Rosa neón
    "J": (70, 130, 255),     # Azul eléctrico
    "L": (255, 140, 40),     # Naranja ardiente
}


COLOR_FONDO_MENU = (20, 25, 40)  # Azul oscuro
COLOR_OVERLAY = (10, 15, 30, 200)  # Semi-transparente
COLOR_TEXTO_PRINCIPAL = (245, 250, 255)  # Blanco brillante
COLOR_TEXTO_SECUNDARIO = (180, 190, 210)  # Gris claro azulado
COLOR_ACENTO = (100, 200, 255)  # Azul cielo

# Configuración de sonidos
DIRECTORIO_SONIDOS = r"C:\Users\0803570563\Documents\PROYECTO_FUNCIONAL\Sound_Effects"


GRAVEDAD_BASE_S = 0.8
INTERVALO_CAIDA_SUAVE_S = 0.2
# ============================================================
#                     RENDERIZADO
# ============================================================
class RenderizadorTetris:
    """Maneja todo el renderizado visual del juego."""
    
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente = pygame.font.SysFont("Consolas", 16)
        self.fuente_grande = pygame.font.SysFont("Consolas", 36, bold=True)
        self.fuente_media = pygame.font.SysFont("Consolas", 22)
    
    def dibujar_tablero(self, tablero):
        """Dibuja el fondo y celdas del tablero."""
        self.pantalla.fill(NEGRO)
        for y in range(FILAS):
            for x in range(COLUMNAS):
                rect = pygame.Rect(x * CELDA, y * CELDA, CELDA, CELDA)
                if tablero[y][x] is not None:
                    color = COLORES_PIEZAS.get(tablero[y][x], BLANCO)
                    # Dibujar celda con efecto de brillo
                    pygame.draw.rect(self.pantalla, color, rect)
                    # Borde interno más oscuro para profundidad
                    color_oscuro = tuple(max(0, c - 40) for c in color)
                    pygame.draw.rect(self.pantalla, color_oscuro, rect, 2)
                else:
                    # Cuadrícula sutil para celdas vacías
                    pygame.draw.rect(self.pantalla, CUADRICULA, rect, 1)
    
    def dibujar_pieza(self, pieza):
        """Dibuja la pieza actual en movimiento con efecto de brillo."""
        if pieza is None:
            return
        color = COLORES_PIEZAS.get(pieza.tipo, BLANCO)
        for (x, y) in pieza.celdas():
            if y >= 0:
                rect = pygame.Rect(x * CELDA, y * CELDA, CELDA, CELDA)
                # Efecto de brillo con borde más claro
                pygame.draw.rect(self.pantalla, color, rect)
                color_claro = tuple(min(255, c + 30) for c in color)
                pygame.draw.rect(self.pantalla, color_claro, rect, 3)
    
    def dibujar_hud(self, estado, mano_activa):
        """Dibuja el panel lateral con información."""
        x_base = COLUMNAS * CELDA + 8
        y = 8
        
        # Título con color de acento
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
            y += self.fuente.get_linesize() + 2
        
        y += 8
        
        # Estado de manos con color
        estado_mano = "Manos: ON" if mano_activa else "Manos: OFF"
        color_mano = (50, 255, 100) if mano_activa else (255, 100, 100)
        txt = self.fuente.render(estado_mano, True, color_mano)
        self.pantalla.blit(txt, (x_base, y))
        y += self.fuente.get_linesize() + 8
        
        # Controles con colores
        lineas_info = [
            ("CONTROLES:", COLOR_ACENTO),
            ("← → : Mover", COLOR_TEXTO_PRINCIPAL),
            ("↑ X : Rotar", COLOR_TEXTO_PRINCIPAL),
            ("↓ : Caída Suave", COLOR_TEXTO_PRINCIPAL),
            ("SPACE : Caída Dura", COLOR_TEXTO_PRINCIPAL),
            ("", COLOR_TEXTO_PRINCIPAL),
            ("GESTOS:", COLOR_ACENTO),
            ("Pulgar ↑ L/R : Mover", COLOR_TEXTO_SECUNDARIO),
            ("Solo Meñique : Rotar", COLOR_TEXTO_SECUNDARIO),
            ("Pulgar ↓ : Suave", COLOR_TEXTO_SECUNDARIO),
            ("Cualquier dedo libre : Dura", COLOR_TEXTO_SECUNDARIO),
        ]
        
        for linea, color in lineas_info:
            txt = self.fuente.render(linea, True, color)
            self.pantalla.blit(txt, (x_base, y))
            y += self.fuente.get_linesize() + 2
    
    def barrido_game_over(self, tablero):
        """Efecto visual de barrido al terminar el juego."""
        self.dibujar_tablero(tablero)
        pygame.display.flip()
        
        retraso_ms = 12
        for y in range(FILAS - 1, -1, -1):
            for x in range(COLUMNAS):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                
                rect = pygame.Rect(x * CELDA, y * CELDA, CELDA, CELDA)
                # Efecto de desvanecimiento con color oscuro
                pygame.draw.rect(self.pantalla, (40, 40, 60), rect)
                pygame.draw.rect(self.pantalla, CUADRICULA, rect, 1)
                pygame.display.update(rect)
                pygame.time.wait(retraso_ms)
    
    def menu_game_over(self, puntaje, lineas, nivel):
        """Dibuja el menú de game over y retorna True si reiniciar."""
        superposicion = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        superposicion.fill(COLOR_OVERLAY)
        self.pantalla.blit(superposicion, (0, 0))
        
        # Título con color vibrante
        titulo = self.fuente_grande.render("GAME OVER", True, (255, 100, 100))
        stats = self.fuente_media.render(
            f"Puntaje: {puntaje}   Líneas: {lineas}   Nivel: {nivel}",
            True, COLOR_ACENTO
        )
        ayuda1 = self.fuente.render("Presiona R para Reiniciar", True, (100, 255, 150))
        ayuda2 = self.fuente.render("Presiona Q o Esc para Salir", True, COLOR_TEXTO_SECUNDARIO)
        
        self.pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//2 - 80))
        self.pantalla.blit(stats, (ANCHO//2 - stats.get_width()//2, ALTO//2 - 30))
        self.pantalla.blit(ayuda1, (ANCHO//2 - ayuda1.get_width()//2, ALTO//2 + 20))
        self.pantalla.blit(ayuda2, (ANCHO//2 - ayuda2.get_width()//2, ALTO//2 + 50))
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
        """Muestra pantalla de carga inicial."""
        cx, cy = self.pantalla.get_rect().center
        
        self.pantalla.fill(COLOR_FONDO_MENU)
        
        # Título con gradiente simulado
        titulo = self.fuente_grande.render("TETRIS", True, COLOR_ACENTO)
        estado = self.fuente.render(mensaje, True, COLOR_TEXTO_SECUNDARIO)
        ayuda = self.fuente.render("Presiona ENTER para comenzar", True, (100, 255, 150))
        
        self.pantalla.blit(titulo, titulo.get_rect(center=(cx, cy - 60)))
        self.pantalla.blit(estado, estado.get_rect(center=(cx, cy - 10)))
        self.pantalla.blit(ayuda, ayuda.get_rect(center=(cx, cy + 30)))
        pygame.display.flip()
# ============================================================
#                      GESTOR DE AUDIO
# ============================================================
class GestorAudio:
    """Maneja todos los efectos de sonido y música."""
    
    def __init__(self):
        self.sonidos = {}
        self._cargar_sonidos()
    
    def _cargar_sonidos(self):
        """Carga todos los archivos de sonido."""
        try:
            self.sonidos['mover'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "move.wav")
            )
            self.sonidos['rotar'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "rotate.wav")
            )
            self.sonidos['fijar'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "piece_landed.wav")
            )
            self.sonidos['linea'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "line.wav")
            )
            self.sonidos['tetris'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "4_lines.wav")
            )
            self.sonidos['nivel'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "level_up.wav")
            )
            self.sonidos['game_over'] = pygame.mixer.Sound(
                os.path.join(DIRECTORIO_SONIDOS, "game_over.wav")
            )
            
            pygame.mixer.music.load(
                os.path.join(DIRECTORIO_SONIDOS, "background.wav")
            )
        except Exception as e:
            print(f"Error cargando sonidos: {e}")
    
    def reproducir(self, nombre):
        """Reproduce un efecto de sonido."""
        if nombre in self.sonidos:
            self.sonidos[nombre].play()
    
    def iniciar_musica(self):
        """Inicia la música de fondo en bucle."""
        pygame.mixer.music.play(-1)
    
    def detener_musica(self):
        """Detiene la música de fondo."""
        pygame.mixer.music.stop()

# ============================================================
#                    BUCLE PRINCIPAL DEL JUEGO
# ============================================================
def ejecutar_juego(mano=None):
    """Ejecuta una sesión completa de juego."""
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Tetris — Controles Teclado + Mano")
    reloj = pygame.time.Clock()
    
    # Inicializar componentes
    motor = Motor(COLUMNAS, FILAS, GRAVEDAD_BASE_S)
    render = RenderizadorTetris(pantalla)
    audio = GestorAudio()
    
    # Mostrar pantalla de carga
    mensaje = ("Iniciando cámara..." if mano else "Modo solo teclado")
    render.pantalla_carga(mensaje, mano is not None)
    
    # Esperar ENTER
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
    
    # Variables de control
    ultima_gravedad = time.time()
    caida_suave_teclado = False
    caida_suave_mano = False
    ultima_caida_suave = time.time()
    
    # Repetición de teclas
    mover_izq = mover_der = False
    retraso_repeticion = 0.15
    ultimo_mov = 0.0
    
    nivel_anterior = 1
    
    # Bucle principal
    ejecutando = True
    while ejecutando and not motor.game_over:
        ahora = time.time()
        reloj.tick(FPS)
        
        # 1) PROCESAR EVENTOS DE TECLADO
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if motor.mover(-1, 0):
                        audio.reproducir('mover')
                    mover_izq = True
                    ultimo_mov = ahora
                
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if motor.mover(1, 0):
                        audio.reproducir('mover')
                    mover_der = True
                    ultimo_mov = ahora
                
                elif event.key in (pygame.K_UP, pygame.K_x):
                    if motor.rotar(1):
                        audio.reproducir('rotar')
                
                elif event.key == pygame.K_z:
                    if motor.rotar(-1):
                        audio.reproducir('rotar')
                
                elif event.key == pygame.K_DOWN:
                    caida_suave_teclado = True
                
                elif event.key == pygame.K_SPACE:
                    filas = motor.caida_dura()
                    audio.reproducir('fijar')
                    
                    # Actualizar puntaje y nivel
                    estado = motor.obtener_estado()
                    if estado['lineas'] >= 4:
                        audio.reproducir('tetris')
                    elif estado['lineas'] > 0:
                        audio.reproducir('linea')
                    
                    if estado['nivel'] > nivel_anterior:
                        audio.reproducir('nivel')
                        nivel_anterior = estado['nivel']
                    
                    ultima_gravedad = ahora
            
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    mover_izq = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    mover_der = False
                elif event.key == pygame.K_DOWN:
                    caida_suave_teclado = False
        
        # 2) PROCESAR INPUT DE MANOS
        if mano is not None:
            # ¡CORREGIDO! Ahora capturamos caida_dura_borde
            dir_mov, caida_suave_m, rotar_borde, caida_dura_borde = mano.consultar()
            
            # Movimiento lateral
            if dir_mov == -1:
                if motor.mover(-1, 0):
                    audio.reproducir('mover')
            elif dir_mov == 1:
                if motor.mover(1, 0):
                    audio.reproducir('mover')
            
            # Rotación
            if rotar_borde:
                if motor.rotar(1):
                    audio.reproducir('rotar')
            
            #  Caída dura con gesto 
            if caida_dura_borde:
                filas = motor.caida_dura()
                audio.reproducir('fijar')
                
                # Actualizar puntaje y nivel
                estado = motor.obtener_estado()
                lineas_nuevas = estado['lineas']
                
                if lineas_nuevas == 4:
                    audio.reproducir('tetris')
                elif lineas_nuevas > 0:
                    audio.reproducir('linea')
                
                if estado['nivel'] > nivel_anterior:
                    audio.reproducir('nivel')
                    nivel_anterior = estado['nivel']
                
                ultima_gravedad = ahora
            
            # Caída suave
            caida_suave_mano = bool(caida_suave_m)
        
        # 3) REPETICIÓN DE TECLAS
        if mover_izq or mover_der:
            if ahora - ultimo_mov >= retraso_repeticion:
                if mover_izq and motor.mover(-1, 0):
                    audio.reproducir('mover')
                    ultimo_mov = ahora
                if mover_der and motor.mover(1, 0):
                    audio.reproducir('mover')
                    ultimo_mov = ahora
        
        # 4) CAÍDA SUAVE
        caida_suave_activa = caida_suave_teclado or caida_suave_mano
        if caida_suave_activa and (ahora - ultima_caida_suave) >= INTERVALO_CAIDA_SUAVE_S:
            motor.caida_suave()
            ultima_caida_suave = ahora
        
        # 5) GRAVEDAD
        gravedad_s = motor.gravedad_actual()
        if caida_suave_activa:
            gravedad_s *= 0.15
        
        if ahora - ultima_gravedad >= gravedad_s:
            if not motor.caida_suave():
                # Pieza no pudo caer, fijarla
                estado_anterior = motor.obtener_estado()
                motor._fijar_pieza()
                audio.reproducir('fijar')
                
                estado = motor.obtener_estado()
                lineas_nuevas = estado['lineas'] - estado_anterior['lineas']
                
                if lineas_nuevas == 4:
                    audio.reproducir('tetris')
                elif lineas_nuevas > 0:
                    audio.reproducir('linea')
                
                if estado['nivel'] > nivel_anterior:
                    audio.reproducir('nivel')
                    nivel_anterior = estado['nivel']
            
            ultima_gravedad = ahora
        
        # 6) RENDERIZAR
        estado = motor.obtener_estado()
        render.dibujar_tablero(estado['tablero'])
        render.dibujar_pieza(estado['pieza_actual'])
        render.dibujar_hud(estado, mano is not None)
        pygame.display.flip()
    
    # GAME OVER
    audio.detener_musica()
    audio.reproducir('game_over')
    
    estado_final = motor.obtener_estado()
    render.barrido_game_over(estado_final['tablero'])
    
    return render.menu_game_over(
        estado_final['puntaje'],
        estado_final['lineas'],
        estado_final['nivel']
    )

# ============================================================
#                         MAIN
# ============================================================
def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    
    mano = crear_controlador_manos_o_nada(mostrar_camara=True, espejo=False)
    
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
