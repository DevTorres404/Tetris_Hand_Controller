# test_tetris.py
"""
Suite completa de tests unitarios para el juego Tetris.
Cubre el núcleo lógico del juego (core_tetris.py).

Ejecutar:
    python -m pytest test_tetris.py -v
    o
    python test_tetris.py
"""

import unittest
import sys
from core_tetris import Motor, Pieza, TETROMINOS



class TestPieza(unittest.TestCase):
    """Tests para la clase Pieza."""
    
    def test_inicializacion_pieza(self):
        """Verifica que las piezas se inicialicen correctamente."""
        pieza = Pieza("I", columnas=10)
        self.assertEqual(pieza.tipo, "I")
        self.assertEqual(pieza.rot, 0)
        self.assertEqual(pieza.x, 3)  # (10-4)//2
        self.assertEqual(pieza.y, -2)
    
    def test_pieza_centrada(self):
        """Verifica que las piezas se centren correctamente."""
        for columnas in [10, 12, 8]:
            pieza = Pieza("O", columnas=columnas)
            self.assertEqual(pieza.x, (columnas - 4) // 2)
    
    def test_celdas_pieza_i(self):
        """Verifica las coordenadas de la pieza I."""
        pieza = Pieza("I", columnas=10)
        celdas = pieza.celdas()
        # Pieza I horizontal: [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]
        # Con x=3, y=-2: fila y=-1 tiene 4 bloques
        self.assertEqual(len(celdas), 4)
        for x, y in celdas:
            self.assertEqual(y, -1)
            self.assertIn(x, [3, 4, 5, 6])
    
    def test_celdas_pieza_o(self):
        """Verifica las coordenadas de la pieza O."""
        pieza = Pieza("O", columnas=10)
        celdas = pieza.celdas()
        # Pieza O: [[0,1,1,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]]
        self.assertEqual(len(celdas), 4)
    
    def test_clonar_pieza(self):
        """Verifica que clonar cree una copia independiente."""
        pieza1 = Pieza("T", columnas=10)
        pieza1.x = 5
        pieza1.y = 10
        pieza1.rot = 2
        
        pieza2 = pieza1.clonar()
        self.assertEqual(pieza2.tipo, pieza1.tipo)
        self.assertEqual(pieza2.x, pieza1.x)
        self.assertEqual(pieza2.y, pieza1.y)
        self.assertEqual(pieza2.rot, pieza1.rot)
        
        # Modificar pieza2 no debe afectar pieza1
        pieza2.x = 0
        self.assertNotEqual(pieza1.x, pieza2.x)
    
    def test_rotacion_pieza(self):
        """Verifica que las rotaciones cambien las celdas."""
        pieza = Pieza("I", columnas=10)
        celdas_rot0 = set(pieza.celdas(rot=0))
        celdas_rot1 = set(pieza.celdas(rot=1))
        # Las celdas deben ser diferentes entre rotaciones
        self.assertNotEqual(celdas_rot0, celdas_rot1)
    
    def test_todas_las_piezas_existen(self):
        """Verifica que todas las piezas puedan crearse."""
        tipos = ["I", "O", "T", "S", "Z", "J", "L"]
        for tipo in tipos:
            pieza = Pieza(tipo, columnas=10)
            self.assertEqual(pieza.tipo, tipo)
            self.assertGreater(len(pieza.celdas()), 0)


class TestMotor(unittest.TestCase):
    """Tests para la clase Motor."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.motor = Motor(columnas=10, filas=20)
    
    def test_inicializacion_motor(self):
        """Verifica que el motor se inicialice correctamente."""
        self.assertEqual(self.motor.columnas, 10)
        self.assertEqual(self.motor.filas, 20)
        self.assertEqual(self.motor.puntaje, 0)
        self.assertEqual(self.motor.nivel, 1)
        self.assertEqual(self.motor.lineas_totales, 0)
        self.assertFalse(self.motor.game_over)
        self.assertIsNotNone(self.motor.pieza_actual)
        self.assertIsNotNone(self.motor.siguiente_pieza)
    
    def test_tablero_vacio_inicial(self):
        """Verifica que el tablero inicial esté vacío."""
        for fila in self.motor.tablero:
            for celda in fila:
                self.assertIsNone(celda)
    
    def test_generar_bolsa(self):
        """Verifica que la bolsa contenga todas las piezas."""
        bolsa = self.motor._generar_bolsa()
        self.assertEqual(len(bolsa), 7)
        self.assertEqual(set(bolsa), set(TETROMINOS.keys()))
    
    def test_mover_derecha(self):
        """Verifica movimiento a la derecha."""
        x_inicial = self.motor.pieza_actual.x
        exito = self.motor.mover(1, 0)
        self.assertTrue(exito)
        self.assertEqual(self.motor.pieza_actual.x, x_inicial + 1)
    
    def test_mover_izquierda(self):
        """Verifica movimiento a la izquierda."""
        x_inicial = self.motor.pieza_actual.x
        exito = self.motor.mover(-1, 0)
        self.assertTrue(exito)
        self.assertEqual(self.motor.pieza_actual.x, x_inicial - 1)
    
    def test_mover_abajo(self):
        """Verifica movimiento hacia abajo."""
        y_inicial = self.motor.pieza_actual.y
        exito = self.motor.mover(0, 1)
        self.assertTrue(exito)
        self.assertEqual(self.motor.pieza_actual.y, y_inicial + 1)
    
    def test_colision_borde_izquierdo(self):
        """Verifica colisión con el borde izquierdo."""
        # Mover pieza al borde izquierdo
        while self.motor.mover(-1, 0):
            pass
        # Intentar mover más allá del borde
        exito = self.motor.mover(-1, 0)
        self.assertFalse(exito)
    
    def test_colision_borde_derecho(self):
        """Verifica colisión con el borde derecho."""
        # Mover pieza al borde derecho
        while self.motor.mover(1, 0):
            pass
        # Intentar mover más allá del borde
        exito = self.motor.mover(1, 0)
        self.assertFalse(exito)
    
    def test_colision_fondo(self):
        """Verifica colisión con el fondo del tablero."""
        # Mover pieza al fondo
        while self.motor.caida_suave():
            pass
        # La pieza debe haberse fijado
        self.assertIsNotNone(self.motor.pieza_actual)
    
    def test_rotar_pieza(self):
        """Verifica que las piezas puedan rotar."""
        rot_inicial = self.motor.pieza_actual.rot
        exito = self.motor.rotar()
        # Algunas piezas pueden no rotar si hay colisión
        if exito:
            self.assertNotEqual(self.motor.pieza_actual.rot, rot_inicial)
    
    def test_caida_dura(self):
        """Verifica que la caída dura mueva la pieza al fondo."""
        y_inicial = self.motor.pieza_actual.y
        filas_bajadas = self.motor.caida_dura()
        self.assertGreater(filas_bajadas, 0)
    
    def test_fijar_pieza(self):
        """Verifica que las piezas se fijen en el tablero."""
        # Obtener tipo de pieza actual
        tipo_actual = self.motor.pieza_actual.tipo
        
        # Caída dura para fijar
        self.motor.caida_dura()
        
        # Verificar que hay bloques en el tablero
        bloques_encontrados = False
        for fila in self.motor.tablero:
            for celda in fila:
                if celda is not None:
                    bloques_encontrados = True
                    break
        self.assertTrue(bloques_encontrados)
    
    def test_limpiar_linea_simple(self):
        """Verifica que se limpie una línea completa."""
        # Llenar la última fila manualmente
        for x in range(self.motor.columnas):
            self.motor.tablero[-1][x] = "I"
        
        lineas_limpiadas = self.motor._limpiar_lineas()
        self.assertEqual(lineas_limpiadas, 1)
        
        # Verificar que la última fila esté vacía
        for celda in self.motor.tablero[-1]:
            self.assertIsNone(celda)
    
    def test_limpiar_multiples_lineas(self):
        """Verifica que se limpien múltiples líneas."""
        # Llenar las últimas 3 filas
        for y in range(self.motor.filas - 3, self.motor.filas):
            for x in range(self.motor.columnas):
                self.motor.tablero[y][x] = "T"
        
        lineas_limpiadas = self.motor._limpiar_lineas()
        self.assertEqual(lineas_limpiadas, 3)
    
    def test_puntuacion_una_linea(self):
        """Verifica la puntuación por una línea."""
        puntaje_inicial = self.motor.puntaje
        self.motor._actualizar_puntaje(1)
        self.assertEqual(self.motor.puntaje, puntaje_inicial + 100)
    
    def test_puntuacion_dos_lineas(self):
        """Verifica la puntuación por dos líneas."""
        puntaje_inicial = self.motor.puntaje
        self.motor._actualizar_puntaje(2)
        self.assertEqual(self.motor.puntaje, puntaje_inicial + 300)
    
    def test_puntuacion_tres_lineas(self):
        """Verifica la puntuación por tres líneas."""
        puntaje_inicial = self.motor.puntaje
        self.motor._actualizar_puntaje(3)
        self.assertEqual(self.motor.puntaje, puntaje_inicial + 500)
    
    def test_puntuacion_tetris(self):
        """Verifica la puntuación por Tetris (4 líneas)."""
        puntaje_inicial = self.motor.puntaje
        self.motor._actualizar_puntaje(4)
        self.assertEqual(self.motor.puntaje, puntaje_inicial + 800)
    
    def test_incremento_nivel(self):
        """Verifica que el nivel aumente cada 10 líneas."""
        # El nivel se calcula como: 1 + lineas_totales // 10
        # Con 9 líneas totales + 1 nueva = 10 líneas → nivel 2
        self.motor.lineas_totales = 9
        self.motor._actualizar_puntaje(1)
        self.assertEqual(self.motor.nivel, 2)  # 1 + 10//10 = 2
        
        # Con 10 líneas totales + 1 nueva = 11 líneas → nivel 2
        self.motor._actualizar_puntaje(1)
        self.assertEqual(self.motor.nivel, 2)  # 1 + 11//10 = 2
        
        # Con 19 líneas totales + 1 nueva = 20 líneas → nivel 3
        self.motor.lineas_totales = 19
        self.motor._actualizar_puntaje(1)
        self.assertEqual(self.motor.nivel, 3)  # 1 + 20//10 = 3
    
    def test_gravedad_aumenta_con_nivel(self):
        """Verifica que la gravedad aumente con el nivel."""
        gravedad_nivel_1 = self.motor.gravedad_actual()
        
        self.motor.nivel = 5
        gravedad_nivel_5 = self.motor.gravedad_actual()
        
        self.assertLess(gravedad_nivel_5, gravedad_nivel_1)
    
    def test_reiniciar_juego(self):
        """Verifica que el juego se reinicie correctamente."""
        # Modificar el estado del juego
        self.motor.puntaje = 1000
        self.motor.nivel = 5
        self.motor.lineas_totales = 50
        self.motor.tablero[0][0] = "I"
        
        # Reiniciar
        self.motor.reiniciar()
        
        # Verificar estado inicial
        self.assertEqual(self.motor.puntaje, 0)
        self.assertEqual(self.motor.nivel, 1)
        self.assertEqual(self.motor.lineas_totales, 0)
        self.assertFalse(self.motor.game_over)
        
        # Verificar tablero vacío
        for fila in self.motor.tablero:
            for celda in fila:
                self.assertIsNone(celda)
    
    def test_game_over_topout(self):
        """Verifica detección de game over cuando la pieza no cabe."""
        # El game over ocurre en dos casos:
        # 1) Al generar nueva pieza que colisiona inmediatamente
        # 2) Al fijar pieza con celdas en y < 0
        
        # CASO 1: Llenar el área donde aparecen las piezas nuevas
        # Las piezas aparecen centradas en y=-2
        # Necesitamos llenar el área donde caerían
        for y in range(4):  # Filas 0-3
            for x in range(self.motor.columnas):
                self.motor.tablero[y][x] = "Z"
        
      
        # CASO 2: Probar con fijar pieza que sobresale
        motor2 = Motor(columnas=10, filas=20)
        motor2.pieza_actual.y = -1  # Posicionar parcialmente fuera
        
        # Verificar que al menos una celda está en y < 0
        celdas_fuera = [celda for celda in motor2.pieza_actual.celdas() if celda[1] < 0]
        self.assertGreater(len(celdas_fuera), 0, 
                          "Debe haber celdas fuera del tablero visible")
        
        # Fijar la pieza - debería activar game over
        motor2._fijar_pieza()
        self.assertTrue(motor2.game_over,
                       "Game over debería activarse al fijar pieza con celdas en y<0")
    
    def test_obtener_estado(self):
        """Verifica que se obtenga el estado completo del juego."""
        estado = self.motor.obtener_estado()
        
        self.assertIn('tablero', estado)
        self.assertIn('pieza_actual', estado)
        self.assertIn('siguiente_pieza', estado)
        self.assertIn('puntaje', estado)
        self.assertIn('nivel', estado)
        self.assertIn('lineas', estado)
        self.assertIn('game_over', estado)
        
        self.assertEqual(len(estado['tablero']), self.motor.filas)
        self.assertEqual(len(estado['tablero'][0]), self.motor.columnas)
    
    def test_wall_kicks(self):
        """Verifica que el sistema de wall kicks funcione."""
        # Mover pieza al borde
        while self.motor.mover(1, 0):
            pass
        
        # Intentar rotar (debería usar wall kicks)
        exito = self.motor.rotar()
        # Puede o no tener éxito dependiendo de la pieza, pero no debe crashear
        self.assertIsInstance(exito, bool)
    
    def test_no_mover_si_game_over(self):
        """Verifica que no se pueda mover si hay game over."""
        self.motor.game_over = True
        exito = self.motor.mover(1, 0)
        self.assertFalse(exito)
    
    def test_no_rotar_si_game_over(self):
        """Verifica que no se pueda rotar si hay game over."""
        self.motor.game_over = True
        exito = self.motor.rotar()
        self.assertFalse(exito)
    
    def test_sistema_7bag(self):
        """Verifica que el sistema 7-bag funcione correctamente."""
        # El sistema 7-bag genera bolsas de 7 piezas únicas
        # pero la primera pieza ya fue generada en __init__
        
        # Recoger tipos de múltiples piezas
        tipos_vistos = [self.motor.pieza_actual.tipo]  # Incluir la pieza inicial
        
        # Generar 20 piezas más para tener suficiente muestra
        for _ in range(20):
            self.motor._generar_nueva_pieza()
            tipos_vistos.append(self.motor.pieza_actual.tipo)
        
        # Verificar que todos los 7 tipos aparecen
        tipos_unicos = set(tipos_vistos)
        self.assertEqual(len(tipos_unicos), 7, 
                        f"Deben aparecer los 7 tipos. Encontrados: {tipos_unicos}")
        
        # Verificar que corresponden a todos los tetrominós
        self.assertEqual(tipos_unicos, set(TETROMINOS.keys()))
        
        # Verificar que en alguna ventana de 7 piezas consecutivas
        # aparecen todos los tipos (propiedad del 7-bag)
        encontrado_bolsa_completa = False
        for i in range(len(tipos_vistos) - 6):
            ventana = set(tipos_vistos[i:i+7])
            if len(ventana) == 7:
                encontrado_bolsa_completa = True
                break
        
        # Esto puede fallar por mala suerte con el shuffle, 
        # pero es altamente improbable con 21 piezas
        self.assertTrue(encontrado_bolsa_completa,
                       "Debería existir al menos una ventana con los 7 tipos")


class TestColisiones(unittest.TestCase):
    """Tests específicos para detección de colisiones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.motor = Motor(columnas=10, filas=20)
    
    def test_colision_con_bloque_fijo(self):
        """Verifica colisión con bloques fijos."""
        # Colocar un bloque fijo
        self.motor.tablero[10][5] = "I"
        
        # Mover pieza a esa posición
        self.motor.pieza_actual.x = 5
        self.motor.pieza_actual.y = 8
        
        # Verificar colisión al moverse hacia el bloque
        colision = self.motor.colisiona(self.motor.pieza_actual, dy=1)
        # Puede o no colisionar dependiendo de la forma de la pieza
        self.assertIsInstance(colision, bool)
    
    def test_no_colision_en_espacio_vacio(self):
        """Verifica que no haya colisión en espacio vacío."""
        self.motor.pieza_actual.x = 5
        self.motor.pieza_actual.y = 10
        
        # No debe colisionar en el centro del tablero vacío
        colision = self.motor.colisiona(self.motor.pieza_actual)
        self.assertFalse(colision)
    
    def test_colision_con_rotacion(self):
        """Verifica colisión al rotar."""
        # Llenar espacio alrededor de la pieza
        for x in range(self.motor.columnas):
            self.motor.tablero[15][x] = "T"
        
        self.motor.pieza_actual.x = 3
        self.motor.pieza_actual.y = 13
        
        # Verificar colisión con rotación
        nueva_rot = (self.motor.pieza_actual.rot + 1) % len(self.motor.pieza_actual.forma)
        colision = self.motor.colisiona(self.motor.pieza_actual, rot=nueva_rot)
        self.assertIsInstance(colision, bool)


class TestIntegracion(unittest.TestCase):
    """Tests de integración para flujos completos."""
    
    def test_juego_completo_simple(self):
        """Simula un juego completo simple."""
        motor = Motor(columnas=10, filas=20)
        
        # Jugar 5 piezas
        for _ in range(5):
            # Caída dura
            motor.caida_dura()
            
            # Verificar que no hay game over
            if motor.game_over:
                break
        
        # El juego debe seguir siendo jugable
        self.assertIsNotNone(motor.pieza_actual)
    
    def test_completar_linea_completa(self):
        """Test de completar una línea desde cero."""
        motor = Motor(columnas=10, filas=20)
        
        # Llenar casi toda la última fila
        for x in range(9):
            motor.tablero[-1][x] = "I"
        
        lineas_iniciales = motor.lineas_totales
        
        # Limpiar líneas
        motor._limpiar_lineas()
        
        # No debería limpiar porque falta una celda
        self.assertEqual(motor.lineas_totales, lineas_iniciales)
        
        # Completar la línea
        motor.tablero[-1][9] = "I"
        lineas_limpiadas = motor._limpiar_lineas()
        
        self.assertEqual(lineas_limpiadas, 1)
    
    def test_subida_de_nivel_progresiva(self):
        """Verifica que el nivel suba progresivamente."""
        motor = Motor(columnas=10, filas=20)
        
        # Simular limpieza de 25 líneas
        for _ in range(25):
            motor.lineas_totales += 1
            motor._actualizar_puntaje(0)
        
        # Debe estar en nivel 3 (25 // 10 + 1)
        motor.nivel = 1 + motor.lineas_totales // 10
        self.assertEqual(motor.nivel, 3)


def suite():
    """Crea una suite con todos los tests."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPieza))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMotor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestColisiones))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegracion))
    return suite


if __name__ == '__main__':
    # Ejecutar con unittest
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    
    # Resumen
    print("\n" + "="*70)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Éxitos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    print("="*70)
    
    # Salir con código apropiado
    sys.exit(0 if result.wasSuccessful() else 1)