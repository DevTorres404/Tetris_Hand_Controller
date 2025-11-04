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
class Motor:
    """Clase que maneja toda la lógica del juego Tetris."""
    
    def __init__(self, columnas=10, filas=20, gravedad_base=0.8):
        self.columnas = columnas
        self.filas = filas
        self.gravedad_base = gravedad_base
        
        # Estado del juego
        self.tablero = self._nuevo_tablero()
        self.bolsa = self._generar_bolsa()
        self.pieza_actual = None
        self.siguiente_pieza = None
        
        # Estadísticas
        self.puntaje = 0
        self.nivel = 1
        self.lineas_totales = 0
        
        # Estado de juego
        self.game_over = False
        
        # Generar primera y segunda pieza
        self._generar_nueva_pieza()
        self._generar_siguiente_pieza()
    
    def _nuevo_tablero(self):
        """Crea un tablero vacío."""
        return [[None for _ in range(self.columnas)] for _ in range(self.filas)]
    
    def _generar_bolsa(self):
        """Sistema 7-bag: cada pieza aparece una vez por bolsa."""
        bolsa = list(TETROMINOS.keys())
        random.shuffle(bolsa)
        return bolsa
    
    def _generar_nueva_pieza(self):
        """Toma una pieza de la bolsa y la hace actual."""
        if not self.bolsa:
            self.bolsa = self._generar_bolsa()
        tipo = self.bolsa.pop()
        self.pieza_actual = Pieza(tipo, self.columnas)
        
        # Verificar si hay game over inmediato
        if self.colisiona(self.pieza_actual):
            self.game_over = True
    
    def _generar_siguiente_pieza(self):
        """Prepara la siguiente pieza para mostrar."""
        if not self.bolsa:
            self.bolsa = self._generar_bolsa()
        tipo = self.bolsa[-1]  # Peek sin sacar
        self.siguiente_pieza = Pieza(tipo, self.columnas)
        
