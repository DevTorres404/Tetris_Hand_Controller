# core_tetris.py
# =============================================================================
#                       NÚCLEO LÓGICO DEL TETRIS
# =============================================================================
# Este módulo contiene toda la lógica del juego sin dependencias de pygame
# o renderizado. Maneja el tablero, piezas, colisiones, rotaciones y puntuación.

import random
from typing import List, Tuple, Optional, Dict, Any

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
    """
    Representa un tetrominó (pieza de juego) con su posición, tipo y rotación actual.

    Attributes:
        tipo (str): El tipo de tetrominó ('I', 'O', 'T', 'S', 'Z', 'J', 'L').
        rot (int): El índice de rotación actual (0-3).
        x (int): La posición horizontal de la pieza en el tablero.
        y (int): La posición vertical de la pieza en el tablero.
        forma (List[List[List[int]]]): La matriz de formas para todas las rotaciones posibles de este tipo.
    """

    def __init__(self, tipo: str, columnas: int = 10):
        """
        Inicializa una nueva pieza.

        Args:
            tipo (str): El identificador del tipo de pieza.
            columnas (int): El ancho del tablero, usado para centrar la pieza inicialmente.
        """
        self.tipo = tipo
        self.rot = 0
        self.x = (columnas - 4) // 2  # Centrar horizontalmente
        self.y = -2  # Empezar arriba del área visible
        self.forma = TETROMINOS[tipo]["rot"]

    def celdas(self, rot: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Calcula las coordenadas absolutas que ocupa la pieza en el tablero.

        Args:
            rot (int, optional): Un índice de rotación específico para calcular.
                                 Si es None, usa la rotación actual de la pieza.

        Returns:
            List[Tuple[int, int]]: Lista de pares (x, y) de las celdas ocupadas.
        """
        r = self.rot if rot is None else rot
        salida = []
        mat = self.forma[r]
        for j in range(4):
            for i in range(4):
                if mat[j][i]:
                    salida.append((self.x + i, self.y + j))
        return salida

    def clonar(self) -> 'Pieza':
        """
        Crea una copia profunda de la pieza actual.

        Returns:
            Pieza: Una nueva instancia de Pieza con el mismo estado.
        """
        nueva = Pieza(self.tipo)
        nueva.rot = self.rot
        nueva.x = self.x
        nueva.y = self.y
        return nueva

# ============================================================
#                     MOTOR DEL JUEGO
# ============================================================
class Motor:
    """
    Maneja la lógica central del juego Tetris, incluyendo el estado del tablero,
    movimiento de piezas, detección de colisiones y sistema de puntuación.
    """

    def __init__(self, columnas: int = 10, filas: int = 20, gravedad_base: float = 0.8):
        """
        Inicializa el motor del juego.

        Args:
            columnas (int): Número de columnas del tablero.
            filas (int): Número de filas del tablero.
            gravedad_base (float): Tiempo base en segundos para la caída automática de piezas.
        """
        self.columnas = columnas
        self.filas = filas
        self.gravedad_base = gravedad_base

        # Estado del juego
        self.tablero: List[List[Optional[str]]] = self._nuevo_tablero()
        self.bolsa: List[str] = self._generar_bolsa()
        self.pieza_actual: Optional[Pieza] = None
        self.siguiente_pieza: Optional[Pieza] = None

        # Estadísticas
        self.puntaje: int = 0
        self.nivel: int = 1
        self.lineas_totales: int = 0

        # Estado de juego
        self.game_over: bool = False

        # Generar primera y segunda pieza
        self._generar_nueva_pieza()
        self._generar_siguiente_pieza()

    def _nuevo_tablero(self) -> List[List[Optional[str]]]:
        """
        Crea un tablero vacío.

        Returns:
            List[List[Optional[str]]]: Matriz de filas x columnas inicializada con None.
        """
        return [[None for _ in range(self.columnas)] for _ in range(self.filas)]

    def _generar_bolsa(self) -> List[str]:
        """
        Genera una nueva bolsa de piezas usando el sistema 7-bag.
        Esto garantiza que cada pieza aparezca una vez antes de repetir.

        Returns:
            List[str]: Lista mezclada de identificadores de piezas.
        """
        bolsa = list(TETROMINOS.keys())
        random.shuffle(bolsa)
        return bolsa

    def _generar_nueva_pieza(self) -> None:
        """
        Toma una pieza de la bolsa y la establece como la pieza actual.
        Si la bolsa está vacía, genera una nueva.
        Si la nueva pieza colisiona inmediatamente al aparecer, se activa Game Over.
        """
        if not self.bolsa:
            self.bolsa = self._generar_bolsa()
        tipo = self.bolsa.pop()
        self.pieza_actual = Pieza(tipo, self.columnas)

        # Verificar si hay game over inmediato
        if self.colisiona(self.pieza_actual):
            self.game_over = True


    def _generar_siguiente_pieza(self) -> None:
        """
        Previsualiza la siguiente pieza sin sacarla de la bolsa (peek).
        Asegura que la bolsa tenga contenido.
        """
        if not self.bolsa:
            self.bolsa = self._generar_bolsa()
        tipo = self.bolsa[-1]  # Peek sin sacar
        self.siguiente_pieza = Pieza(tipo, self.columnas)

    def colisiona(self, pieza: Pieza, rot: Optional[int] = None, dx: int = 0, dy: int = 0) -> bool:
        """
        Verifica si la pieza colisiona con bordes o bloques existentes.

        Args:
            pieza (Pieza): La pieza a verificar.
            rot (int, optional): Rotación hipotética. None para usar la actual.
            dx (int): Desplazamiento horizontal hipotético.
            dy (int): Desplazamiento vertical hipotético.

        Returns:
            bool: True si hay colisión, False si el espacio está libre.
        """
        for (x, y) in pieza.celdas(rot=rot):
            nx, ny = x + dx, y + dy
            # Fuera de límites (paredes o piso)
            if nx < 0 or nx >= self.columnas or ny >= self.filas:
                return True
            # Colisión con bloque existente
            if ny >= 0 and self.tablero[ny][nx] is not None:
                return True
        return False

    def mover(self, dx: int, dy: int) -> bool:
        """
        Intenta mover la pieza actual.

        Args:
            dx (int): Desplazamiento en X (-1 izquierda, 1 derecha).
            dy (int): Desplazamiento en Y (1 abajo).

        Returns:
            bool: True si el movimiento fue exitoso, False si hubo colisión.
        """
        if self.game_over or self.pieza_actual is None:
            return False

        if not self.colisiona(self.pieza_actual, dx=dx, dy=dy):
            self.pieza_actual.x += dx
            self.pieza_actual.y += dy
            return True
        return False

    def rotar(self, direccion: int = 1) -> bool:
        """
        Intenta rotar la pieza usando el sistema de 'Wall Kicks' (SRS simplificado).
        Si la rotación simple falla, intenta desplazar la pieza para encajarla.

        Args:
            direccion (int): 1 para horario, -1 para anti-horario.

        Returns:
            bool: True si la rotación fue exitosa.
        """
        if self.game_over or self.pieza_actual is None:
            return False

        nueva_rot = (self.pieza_actual.rot + direccion) % len(self.pieza_actual.forma)

        # Sistema de kicks: intentar diferentes desplazamientos si la rotación falla
        kicks = [(0,0), (-1,0), (1,0), (0,-1), (-2,0), (2,0)]
        for dx, dy in kicks:
            if not self.colisiona(self.pieza_actual, rot=nueva_rot, dx=dx, dy=dy):
                self.pieza_actual.rot = nueva_rot
                self.pieza_actual.x += dx
                self.pieza_actual.y += dy
                return True
        return False

    def caida_suave(self) -> bool:
        """
        Intenta mover la pieza una fila hacia abajo.

        Returns:
            bool: True si bajó, False si tocó fondo/bloque.
        """
        return self.mover(0, 1)

    def caida_dura(self) -> int:
        """
        Deja caer la pieza instantáneamente hasta el fondo y la fija en el tablero.

        Returns:
            int: Número de filas que cayó la pieza.
        """
        if self.game_over or self.pieza_actual is None:
            return 0

        filas = 0
        while not self.colisiona(self.pieza_actual, dy=filas+1):
            filas += 1

        self.pieza_actual.y += filas
        self._fijar_pieza()
        return filas

    def _fijar_pieza(self) -> None:
        """
        Convierte la pieza actual (móvil) en bloques estáticos en la matriz del tablero.
        Maneja la eliminación de líneas y condiciones de derrota (Game Over).
        """
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

    def _limpiar_lineas(self) -> int:
        """
        Identifica y elimina las filas que están completamente llenas.

        Returns:
            int: Cantidad de líneas eliminadas.
        """
        mantener = [fila for fila in self.tablero if any(celda is None for celda in fila)]
        limpiadas = self.filas - len(mantener)

        # Agregar filas vacías arriba para rellenar
        while len(mantener) < self.filas:
            mantener.insert(0, [None for _ in range(self.columnas)])

        self.tablero = mantener
        return limpiadas

    def _actualizar_puntaje(self, lineas_limpiadas: int, bonus_caida_dura: int = 0) -> bool:
        """
        Calcula y suma el puntaje basado en líneas limpiadas y nivel.

        Args:
            lineas_limpiadas (int): Cantidad de líneas limpiadas simultáneamente.
            bonus_caida_dura (int): Puntos extra por caída dura.

        Returns:
            bool: True si el jugador subió de nivel.
        """
        # Sistema de puntuación: 100, 300, 500, 800 por 1-4 líneas
        puntos_lineas = [0, 100, 300, 500, 800]
        self.puntaje += puntos_lineas[lineas_limpiadas] + bonus_caida_dura * 2

        self.lineas_totales += lineas_limpiadas

        # Nivel aumenta cada 10 líneas
        nivel_anterior = self.nivel
        self.nivel = 1 + self.lineas_totales // 10

        return self.nivel > nivel_anterior

    def gravedad_actual(self) -> float:
        """
        Calcula el intervalo de tiempo entre caídas automáticas según el nivel actual.

        Returns:
            float: Segundos entre caídas.
        """
        return max(0.1, self.gravedad_base * (0.9 ** (self.nivel - 1)))

    def reiniciar(self) -> None:
        """
        Reinicia el juego a su estado inicial, limpiando tablero y puntuación.
        """
        self.tablero = self._nuevo_tablero()
        self.bolsa = self._generar_bolsa()
        self.puntaje = 0
        self.nivel = 1
        self.lineas_totales = 0
        self.game_over = False
        self._generar_nueva_pieza()
        self._generar_siguiente_pieza()

    def obtener_estado(self) -> Dict[str, Any]:
        """
        Empaqueta el estado actual del juego para ser consumido por la interfaz gráfica.

        Returns:
            Dict[str, Any]: Diccionario con tablero, piezas, puntaje, etc.
        """
        return {
            'tablero': self.tablero,
            'pieza_actual': self.pieza_actual,
            'siguiente_pieza': self.siguiente_pieza,
            'puntaje': self.puntaje,
            'nivel': self.nivel,
            'lineas': self.lineas_totales,
            'game_over': self.game_over
        }
