# =============================================================================
#                      NÚCLEO FUNCIONAL PURO DEL TETRIS
# =============================================================================
import random
from copy import deepcopy
# ============================================================
#                           CONSTANTES
# ============================================================
COLUMNAS, FILAS = 10, 20

# Colores tipo Tetris clásico
C_I = (0, 255, 255)
C_O = (255, 255, 0)
C_T = (160, 0, 240)
C_S = (0, 255, 0)
C_Z = (255, 0, 0)
C_J = (0, 0, 255)
C_L = (255, 128, 0)
# ============================================================
#                        FORMAS DE TETROMINÓS
# ============================================================
TETROMINOS = {
    "I": {"color": C_I, "rot": [
        [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
        [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]],
        [[0,0,0,0],[0,0,0,0],[1,1,1,1],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
    ]},
    "O": {"color": C_O, "rot": [[[0,1,1,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]]]*4},
    "T": {"color": C_T, "rot": [
        [[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,1,0],[0,1,0,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,1,0],[0,1,0,0],[0,0,0,0]],
        [[0,1,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]],
    ]},
    "S": {"color": C_S, "rot": [
        [[0,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,0,0]],
        [[0,0,0,0],[0,1,1,0],[1,1,0,0],[0,0,0,0]],
        [[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]],
    ]},
    "Z": {"color": C_Z, "rot": [
        [[1,1,0,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,0,1,0],[0,1,1,0],[0,1,0,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,0,0],[0,1,1,0],[0,0,0,0]],
        [[0,1,0,0],[1,1,0,0],[1,0,0,0],[0,0,0,0]],
    ]},
    "J": {"color": C_J, "rot": [
        [[1,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,1,0],[0,1,0,0],[0,1,0,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,1,0],[0,0,1,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[1,1,0,0],[0,0,0,0]],
    ]},
    "L": {"color": C_L, "rot": [
        [[0,0,1,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,1,0],[1,0,0,0],[0,0,0,0]],
        [[1,1,0,0],[0,1,0,0],[0,1,0,0],[0,0,0,0]],
    ]},
}
class Pieza:
    def __init__(self, tipo, x=3, y=-2, rot=0):
        self.tipo = tipo
        self.rot = rot
        self.x = x
        self.y = y
        self.forma = TETROMINOS[tipo]["rot"]
        self.color = TETROMINOS[tipo]["color"]

    def celdas(self, rot=None, x=None, y=None):
        r = self.rot if rot is None else rot
        ox = self.x if x is None else x
        oy = self.y if y is None else y
        salida = []
        mat = self.forma[r]
        for j in range(4):
            for i in range(4):
                if mat[j][i]:
                    salida.append((ox + i, oy + j))
        return salida
# ============================================================
#                        ESTRUCTURAS DE DATOS
# ============================================================

class EstadoJuego:
    def __init__(self, tablero=None, pieza_actual=None, siguiente_pieza=None,
                 puntaje=0, nivel=1, lineas_cleared=0, game_over=False):
        self.tablero = tablero or [[None]*COLUMNAS for _ in range(FILAS)]
        self.pieza_actual = pieza_actual
        self.siguiente_pieza = siguiente_pieza
        self.puntaje = puntaje
        self.nivel = nivel
        self.lineas_cleared = lineas_cleared
        self.game_over = game_over
