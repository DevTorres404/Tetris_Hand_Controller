# =============================================================================
#                       NÚCLEO LÓGICO DEL TETRIS
# =============================================================================
# Este módulo contiene toda la lógica del juego sin dependencias de pygame
# o renderizado. Maneja el tablero, piezas, colisiones, rotaciones y puntuación.

import random

# ============================================================
#                    FORMAS DE TETROMINÓS
# ============================================================
TETROMINOS = {
    "I": {"rot": [
        [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
        [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]],
        [[0,0,0,0],[0,0,0,0],[1,1,1,1],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
    ]},
    "O": {"rot": [[[0,1,1,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]]]*4},
    "T": {"rot": [
        [[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,1,0],[0,1,0,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,1,0],[0,1,0,0],[0,0,0,0]],
        [[0,1,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]],
    ]},
    "S": {"rot": [
        [[0,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,0,0]],
        [[0,0,0,0],[0,1,1,0],[1,1,0,0],[0,0,0,0]],
        [[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]],
    ]},
    "Z": {"rot": [
        [[1,1,0,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,0,1,0],[0,1,1,0],[0,1,0,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,0,0],[0,1,1,0],[0,0,0,0]],
        [[0,1,0,0],[1,1,0,0],[1,0,0,0],[0,0,0,0]],
    ]},
    "J": {"rot": [
        [[1,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,1,0],[0,1,0,0],[0,1,0,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,1,0],[0,0,1,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[1,1,0,0],[0,0,0,0]],
    ]},
    "L": {"rot": [
        [[0,0,1,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
        [[0,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,0,0]],
        [[0,0,0,0],[1,1,1,0],[1,0,0,0],[0,0,0,0]],
        [[1,1,0,0],[0,1,0,0],[0,1,0,0],[0,0,0,0]],
    ]},
}


class Pieza:
    """Representa un tetrominó con posición y rotación."""
    
    def __init__(self, tipo, columnas=10):
        self.tipo = tipo
        self.rot = 0
        self.x = (columnas - 4) // 2  # Centrar horizontalmente
        self.y = -2  # Empezar arriba del área visible
        self.forma = TETROMINOS[tipo]["rot"]
    
    def celdas(self, rot=None):
        """Retorna lista de coordenadas (x, y) ocupadas por la pieza."""
        r = self.rot if rot is None else rot
        salida = []
        mat = self.forma[r]
        for j in range(4):
            for i in range(4):
                if mat[j][i]:
                    salida.append((self.x + i, self.y + j))
        return salida
    
    def clonar(self):
        """Crea una copia de esta pieza."""
        nueva = Pieza(self.tipo)
        nueva.rot = self.rot
        nueva.x = self.x
        nueva.y = self.y
        return nueva

# ============================================================
#                        MOTOR DEL JUEGO
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
