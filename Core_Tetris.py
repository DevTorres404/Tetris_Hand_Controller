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
# ============================================================
#                        FUNCIONES PURAS
# ============================================================
#Generar bolsa usando seed para mantener la pureza
def generar_bolsa_pura(seed=None):
    bolsa = list(TETROMINOS.keys())
    rnd = random.Random(seed)  # Raíz
    rnd.shuffle(bolsa)
    return bolsa
    
def colisiona(tablero, pieza, rot=None, dx=0, dy=0):
    for x, y in pieza.celdas(rot=rot, x=pieza.x+dx, y=pieza.y+dy):
        if x < 0 or x >= COLUMNAS or y >= FILAS:
            return True
        if y >= 0 and tablero[y][x] is not None:
            return True
    return False

def colocar_pieza(tablero, pieza):
    nuevo_tablero = deepcopy(tablero)
    topout = False
    for x, y in pieza.celdas():
        if y < 0:
            topout = True
            continue
        if 0 <= y < FILAS:
            nuevo_tablero[y][x] = pieza.color
    return nuevo_tablero, topout
        
def eliminar_lineas_completas(tablero):
    nuevo_tablero = [fila for fila in tablero if any(c is None for c in fila)]
    lineas_eliminadas = FILAS - len(nuevo_tablero)
    for _ in range(lineas_eliminadas):
        nuevo_tablero.insert(0, [None]*COLUMNAS)
    return nuevo_tablero, lineas_eliminadas

def generar_nueva_pieza_pura(bolsa, seed=0):
    """
    Genera una nueva pieza de Tetris de manera pura.
    - bolsa: lista de tipos de tetrominós restantes.
    - seed: semilla para mezclar la bolsa si está vacía.
    Retorna: (pieza, nueva_bolsa)
    """
    from random import Random

    bolsa = bolsa.copy()  # no mutamos la bolsa original

    # Si la bolsa está vacía, regenerarla y mezclarla con semilla fija
    if not bolsa:
        bolsa = list(TETROMINOS.keys())
        rnd = Random(seed)
        rnd.shuffle(bolsa)

    tipo = bolsa[-1]       # tomamos la última pieza
    pieza = Pieza(tipo)
    nueva_bolsa = bolsa[:-1]

    return pieza, nueva_bolsa

def verificar_game_over(tablero, pieza):
    return colisiona(tablero, pieza)
