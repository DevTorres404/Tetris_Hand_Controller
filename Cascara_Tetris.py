# =============================================================================
#                    INTERFAZ Y PRESENTACIÓN DEL TETRIS
# =============================================================================
# Este módulo maneja toda la visualización, sonidos, controles y flujo de UI
# usando pygame. Depende de Core_Tetris.py para la lógica del juego.

import pygame
import sys
import time
import os
from Core_Tetris import Motor, TETROMINOS
from Controlador_Manos import crear_controlador_manos_o_nada
# ============================================================
#                      CONFIGURACIÓN VISUAL
# ============================================================
COLUMNAS, FILAS = 10, 20
CELDA = 30
ANCHO_LATERAL = 6 * CELDA
ANCHO, ALTO = COLUMNAS * CELDA + ANCHO_LATERAL, FILAS * CELDA
FPS = 30

# Colores - ESQUEMA MODERNO Y VIBRANTE
NEGRO = (15, 15, 25)  # Azul oscuro profundo
CUADRICULA = (60, 65, 90)  # Gris azulado
BLANCO = (245, 250, 255)  # Blanco con tinte azul
GRIS = (75, 80, 100)  # Gris medio

# Colores de piezas - PALETA NEÓN VIBRANTE
COLORES_PIEZAS = {
    "I": (0, 240, 255),      # Cyan brillante
    "O": (255, 215, 0),      # Oro
    "T": (200, 50, 255),     # Púrpura neón
    "S": (50, 255, 100),     # Verde esmeralda
    "Z": (255, 60, 100),     # Rosa neón
    "J": (70, 130, 255),     # Azul eléctrico
    "L": (255, 140, 40),     # Naranja ardiente
}

# Colores para UI
COLOR_FONDO_MENU = (20, 25, 40)  # Azul oscuro
COLOR_OVERLAY = (10, 15, 30, 200)  # Semi-transparente
COLOR_TEXTO_PRINCIPAL = (245, 250, 255)  # Blanco brillante
COLOR_TEXTO_SECUNDARIO = (180, 190, 210)  # Gris claro azulado
COLOR_ACENTO = (100, 200, 255)  # Azul cielo

# Configuración de sonidos
DIRECTORIO_SONIDOS = r"C:\Users\0803570563\Documents\PROYECTO_FUNCIONAL\Sound_Effects"

# Temporización
GRAVEDAD_BASE_S = 0.8
INTERVALO_CAIDA_SUAVE_S = 0.2
