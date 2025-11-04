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
        
    def colisiona(self, pieza, rot=None, dx=0, dy=0):
        """Verifica si la pieza colisiona con bordes o bloques."""
        for (x, y) in pieza.celdas(rot=rot):
            nx, ny = x + dx, y + dy
            # Fuera de límites
            if nx < 0 or nx >= self.columnas or ny >= self.filas:
                return True
            # Colisión con bloque existente
            if ny >= 0 and self.tablero[ny][nx] is not None:
                return True
        return False
    
    def mover(self, dx, dy):
        """Intenta mover la pieza. Retorna True si tuvo éxito."""
        if self.game_over or self.pieza_actual is None:
            return False
        
        if not self.colisiona(self.pieza_actual, dx=dx, dy=dy):
            self.pieza_actual.x += dx
            self.pieza_actual.y += dy
            return True
        return False
    
    def rotar(self, direccion=1):
        """Intenta rotar la pieza con wall kicks. Retorna True si tuvo éxito."""
        if self.game_over or self.pieza_actual is None:
            return False
        
        nueva_rot = (self.pieza_actual.rot + direccion) % len(self.pieza_actual.forma)
        
        # Sistema de kicks: intentar diferentes posiciones
        kicks = [(0,0), (-1,0), (1,0), (0,-1), (-2,0), (2,0)]
        for dx, dy in kicks:
            if not self.colisiona(self.pieza_actual, rot=nueva_rot, dx=dx, dy=dy):
                self.pieza_actual.rot = nueva_rot
                self.pieza_actual.x += dx
                self.pieza_actual.y += dy
                return True
        return False
    
    def caida_suave(self):
        """Intenta mover la pieza una fila abajo. Retorna True si tuvo éxito."""
        return self.mover(0, 1)
    
    def caida_dura(self):
        """Deja caer la pieza hasta el fondo y la fija. Retorna filas bajadas."""
        if self.game_over or self.pieza_actual is None:
            return 0
        
        filas = 0
        while not self.colisiona(self.pieza_actual, dy=filas+1):
            filas += 1
        
        self.pieza_actual.y += filas
        self._fijar_pieza()
        return filas
    
    def _fijar_pieza(self):
        """Convierte la pieza actual en bloques fijos en el tablero."""
        if self.pieza_actual is None:
            return
        
        topout = False
        for (x, y) in self.pieza_actual.celdas():
            if y < 0:
                topout = True
                continue
            if 0 <= y < self.filas:
                self.tablero[y][x] = self.pieza_actual.tipo
        
        if topout:
            self.game_over = True
            return
        
        # Limpiar líneas y actualizar estadísticas
        lineas_limpiadas = self._limpiar_lineas()
        self._actualizar_puntaje(lineas_limpiadas)
        
        # Generar nueva pieza
        self._generar_nueva_pieza()
        self._generar_siguiente_pieza()
        
