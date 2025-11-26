import pytest
from src.core_tetris import Pieza, Motor, TETROMINOS

# =============================================================================
# TESTS PARA LA CLASE PIEZA
# =============================================================================

def test_pieza_inicializacion():
    pieza = Pieza("T")
    assert pieza.tipo == "T"
    assert pieza.rot == 0
    assert pieza.x == 3  # (10 - 4) // 2 = 3
    assert pieza.y == -2
    assert pieza.forma == TETROMINOS["T"]["rot"]

def test_pieza_celdas_base():
    pieza = Pieza("O")
    # La pieza O es un cuadrado de 2x2 en el centro de la matriz 4x4
    # Matriz O:
    # 0 1 1 0
    # 0 1 1 0
    # 0 0 0 0
    # 0 0 0 0
    # Coordenadas relativas: (1,0), (2,0), (1,1), (2,1)
    # Coordenadas absolutas (x=3, y=-2): (4,-2), (5,-2), (4,-1), (5,-1)
    celdas = pieza.celdas()
    expected = [(4, -2), (5, -2), (4, -1), (5, -1)]
    assert sorted(celdas) == sorted(expected)

def test_pieza_celdas_rotacion():
    pieza = Pieza("I")
    # I horizontal inicial:
    # 0 0 0 0
    # 1 1 1 1
    # 0 0 0 0
    # 0 0 0 0
    # Coordenadas relativas: (0,1), (1,1), (2,1), (3,1)
    # Coordenadas absolutas (x=3, y=-2): (3,-1), (4,-1), (5,-1), (6,-1)
    celdas_rot0 = pieza.celdas(rot=0)
    expected_rot0 = [(3, -1), (4, -1), (5, -1), (6, -1)]
    assert sorted(celdas_rot0) == sorted(expected_rot0)

    # I vertical (rot=1):
    # 0 0 1 0
    # 0 0 1 0
    # 0 0 1 0
    # 0 0 1 0
    # Coordenadas relativas: (2,0), (2,1), (2,2), (2,3)
    # Coordenadas absolutas (x=3, y=-2): (5,-2), (5,-1), (5,0), (5,1)
    celdas_rot1 = pieza.celdas(rot=1)
    expected_rot1 = [(5, -2), (5, -1), (5, 0), (5, 1)]
    assert sorted(celdas_rot1) == sorted(expected_rot1)

def test_pieza_clonar():
    pieza = Pieza("L")
    pieza.x = 5
    pieza.y = 5
    pieza.rot = 2
    
    clon = pieza.clonar()
    assert clon.tipo == pieza.tipo
    assert clon.x == pieza.x
    assert clon.y == pieza.y
    assert clon.rot == pieza.rot
    assert clon is not pieza  # Debe ser un objeto diferente

# =============================================================================
# TESTS PARA LA CLASE MOTOR
# =============================================================================

@pytest.fixture
def motor():
    return Motor(columnas=10, filas=20)

def test_motor_inicializacion(motor):
    assert motor.columnas == 10
    assert motor.filas == 20
    assert len(motor.tablero) == 20
    assert len(motor.tablero[0]) == 10
    assert motor.puntaje == 0
    assert motor.nivel == 1
    assert motor.lineas_totales == 0
    assert not motor.game_over
    assert motor.pieza_actual is not None
    assert motor.siguiente_pieza is not None

def test_motor_generar_bolsa(motor):
    bolsa = motor._generar_bolsa()
    assert len(bolsa) == 7
    assert set(bolsa) == set(TETROMINOS.keys())

def test_motor_colisiona_limites(motor):
    pieza = Pieza("O")
    pieza.x = -2 # Fuera a la izquierda
    assert motor.colisiona(pieza)
    
    pieza.x = 10 # Fuera a la derecha
    assert motor.colisiona(pieza)
    
    pieza.x = 3
    pieza.y = 20 # Fuera abajo
    assert motor.colisiona(pieza)

def test_motor_colisiona_bloque(motor):
    # Colocar un bloque en el tablero
    motor.tablero[10][5] = "I"
    
    pieza = Pieza("O")
    pieza.x = 4 # Ocupa columnas 4 y 5
    pieza.y = 9 # Ocupa filas 9 y 10. (5,10) colisionará
    
    # La pieza O en (4,9) ocupa:
    # (5,9), (6,9)
    # (5,10), (6,10) -> (5,10) choca con el bloque en tablero[10][5]?
    # Espera, Pieza O coordenadas relativas:
    # 0 1 1 0
    # 0 1 1 0
    # -> (1,0), (2,0), (1,1), (2,1)
    # Absolutas con x=4, y=9:
    # (5,9), (6,9), (5,10), (6,10)
    # Si tablero[10][5] está ocupado, debe colisionar.
    
    assert motor.colisiona(pieza)

def test_motor_mover(motor):
    pieza = motor.pieza_actual
    x_inicial = pieza.x
    y_inicial = pieza.y
    
    # Mover derecha
    assert motor.mover(1, 0)
    assert pieza.x == x_inicial + 1
    assert pieza.y == y_inicial
    
    # Mover abajo
    assert motor.mover(0, 1)
    assert pieza.x == x_inicial + 1
    assert pieza.y == y_inicial + 1
    
    # Mover a colisión (pared derecha)
    pieza.x = 8 # Borde derecho para pieza O/I/etc suele estar cerca
    # Forzamos posición segura
    pieza.x = 0
    pieza.y = 0
    # Intentar mover fuera a la izquierda
    assert not motor.mover(-5, 0)
    assert pieza.x == 0 # No se movió

def test_motor_rotar_basico(motor):
    motor.pieza_actual = Pieza("T")
    motor.pieza_actual.x = 5
    motor.pieza_actual.y = 5
    rot_inicial = motor.pieza_actual.rot
    
    assert motor.rotar()
    assert motor.pieza_actual.rot == (rot_inicial + 1) % 4

def test_motor_rotar_wall_kick(motor):
    # Testear wall kick simple contra pared derecha
    motor.pieza_actual = Pieza("I")
    # Poner la I vertical pegada a la pared derecha
    motor.pieza_actual.rot = 1 
    motor.pieza_actual.x = 8 # Columna 8. Ocupa x=10 en rot 1?
    # I rot 1:
    # 0 0 1 0
    # 0 0 1 0
    # 0 0 1 0
    # 0 0 1 0
    # Relativo x=2. Absoluto = 8+2 = 10 -> Fuera de rango (0-9)
    # Ajustamos x para que esté válida en vertical pero choque al rotar
    motor.pieza_actual.x = 7 # x=9 es la última columna válida
    motor.pieza_actual.y = 5
    
    # Al rotar a horizontal (rot 2), ocupa 4 celdas de ancho.
    # Desde x=7: 7,8,9,10 -> 10 fuera de rango.
    # El kick debería moverla a la izquierda.
    
    assert motor.rotar()
    # Verifica que rotó y se movió
    assert motor.pieza_actual.rot == 2
    assert motor.pieza_actual.x < 7 # Se movió a la izquierda

def test_motor_caida_suave(motor):
    motor.pieza_actual.y = 0
    assert motor.caida_suave()
    assert motor.pieza_actual.y == 1

def test_motor_caida_dura(motor):
    motor.pieza_actual = Pieza("I")
    motor.pieza_actual.x = 3
    motor.pieza_actual.y = 0
    
    # Tablero vacío, debe caer hasta el fondo (fila 19 para la parte baja)
    # I horizontal (rot 0) ocupa fila y+1 = 1.
    # Fondo es 19.
    # Debería caer hasta que la parte baja toque 19.
    
    filas = motor.caida_dura()
    assert filas > 0
    # La pieza debe haberse fijado y generado una nueva
    # Pero caida_dura llama a _fijar_pieza que genera nueva pieza.
    # Difícil verificar posición exacta de la vieja pieza ya que self.pieza_actual cambió.
    # Verificamos que hay bloques en el tablero.
    assert any(any(row) for row in motor.tablero)

def test_motor_limpiar_lineas(motor):
    # Llenar una fila completa
    for x in range(10):
        motor.tablero[19][x] = "I"
    
    # Llenar otra fila parcial
    motor.tablero[18][0] = "I"
    
    limpiadas = motor._limpiar_lineas()
    assert limpiadas == 1
    # La fila 19 debe estar vacía ahora (o tener lo que cayó, en este caso nada)
    # La fila 18 bajó a la 19
    assert motor.tablero[19][0] == "I"
    assert motor.tablero[19][1] is None

def test_motor_puntuacion_nivel(motor):
    motor.nivel = 1
    motor.lineas_totales = 0
    motor.puntaje = 0
    
    # Simular limpiar 4 líneas (Tetris)
    motor._actualizar_puntaje(4)
    
    assert motor.puntaje == 800
    assert motor.lineas_totales == 4
    assert motor.nivel == 1 # 4 lineas no sube nivel (necesita 10)
    
    # Limpiar 6 más para subir nivel
    motor._actualizar_puntaje(4) # 8 lineas
    motor._actualizar_puntaje(2) # 10 lineas
    
    assert motor.lineas_totales == 10
    assert motor.nivel == 2

def test_motor_game_over(motor):
    # Llenar el tablero hasta arriba
    for y in range(20):
        for x in range(10):
            motor.tablero[y][x] = "I"
            
    # La pieza nueva aparece arriba (y=-2).
    # Al hacer caida_dura, debería chocar inmediatamente (no bajar nada)
    # y al fijarse fuera del tablero, debe dar game over.
    motor.caida_dura()
    assert motor.game_over

def test_motor_reiniciar(motor):
    motor.puntaje = 5000
    motor.nivel = 5
    motor.game_over = True
    motor.tablero[19][0] = "I"
    
    motor.reiniciar()
    
    assert motor.puntaje == 0
    assert motor.nivel == 1
    assert not motor.game_over
    assert motor.tablero[19][0] is None

def test_motor_obtener_estado(motor):
    estado = motor.obtener_estado()
    assert "tablero" in estado
    assert "pieza_actual" in estado
    assert "puntaje" in estado
    assert estado["puntaje"] == motor.puntaje
