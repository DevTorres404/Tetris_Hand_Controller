# Tetris con Control de Gestos

Este proyecto es una implementación moderna del clásico juego Tetris, desarrollado en Python utilizando `pygame`. Lo que lo hace único es su capacidad de ser controlado mediante gestos de mano en tiempo real, gracias a la integración de visión por computadora con MediaPipe y OpenCV.

## Características

*   **Jugabilidad Clásica**: Mecánicas de Tetris auténticas con sistema de rotación, bolsa de 7 piezas (7-bag system), y niveles de dificultad progresiva.
*   **Control por Gestos**: Juega sin tocar el teclado utilizando gestos intuitivos frente a tu cámara web.
*   **Interfaz Moderna**: Gráficos vibrantes, efectos de partículas (brillo en piezas), y un HUD limpio.
*   **Cámara Integrada**: Visualización en tiempo real de tu cámara y el estado de detección de gestos dentro del juego.
*   **Audio Inmersivo**: Efectos de sonido para movimientos, rotaciones, líneas completadas y música de fondo (descarga automática de assets).
*   **Sistema de Puntuación**: Puntuación estándar de Tetris 

## Requisitos

El proyecto requiere Python 3.7+ y las siguientes librerías:

*   `pygame`: Para la interfaz gráfica y el bucle del juego.
*   `opencv-python`: Para capturar el video de la cámara web.
*   `mediapipe`: Para la detección y seguimiento de manos.
*   `numpy`: Para operaciones numéricas y manipulación de arrays.

## Instalación

1.  Clona este repositorio o descarga el código fuente.
2.  Instala las dependencias necesarias ejecutando:

```bash
pip install pygame opencv-python mediapipe numpy
```

## Uso

Para iniciar el juego, ejecuta el archivo principal `cascara_tetris.py` desde la terminal:

```bash
python src/cascara_tetris.py
```

Al iniciar, el juego intentará detectar tu cámara web. Si se detecta correctamente, se activará el modo de control por gestos. Si no, o si prefieres, puedes jugar usando solo el teclado.

## Controles

El juego soporta tanto entrada por teclado como por gestos simultáneamente.

### Teclado

| Acción | Tecla |
| :--- | :--- |
| **Mover Izquierda** | Flecha Izquierda / A |
| **Mover Derecha** | Flecha Derecha / D |
| **Rotar (Horario)** | Flecha Arriba / X |
| **Rotar (Anti-horario)** | Z |
| **Caída Suave** | Flecha Abajo |
| **Caída Dura** | Espacio |
| **Reiniciar** | R (en pantalla de Game Over) |
| **Salir** | Q / Esc |

### Gestos de Mano

Asegúrate de que tu mano sea visible para la cámara. El sistema distingue entre mano izquierda y derecha (aunque el efecto es simétrico para movimiento).

| Acción | Gesto | Descripción |
| :--- | :--- | :--- |
| **Mover Izquierda** | 👍 **Pulgar Arriba** (Mano Izquierda) | Mantén el pulgar hacia arriba con la mano izquierda. |
| **Mover Derecha** | 👍 **Pulgar Arriba** (Mano Derecha) | Mantén el pulgar hacia arriba con la mano derecha. |
| **Caída Suave** | 👎 **Pulgar Abajo** | Apunta el pulgar hacia abajo con cualquier mano. |
| **Rotar** | 🤙 **Solo Meñique** | Extiende *solo* el dedo meñique (haciendo el gesto de "shaka" o similar pero solo meñique). |
| **Caída Dura** | ☝️ **Dedo Extendido** | Extiende cualquier otro dedo (Índice, Medio, Anular) de forma clara. |

**Nota**: La visualización de la cámara en el juego te mostrará el estado de detección (puntos de referencia de la mano) para ayudarte a realizar los gestos correctamente.

## Estructura del Proyecto

*   `src/core_tetris.py`: Lógica pura del juego (tablero, piezas, colisiones). Independiente de la interfaz gráfica.
*   `src/cascara_tetris.py`: Interfaz gráfica con Pygame, manejo de audio y bucle principal.
*   `src/controlador_manos.py`: Módulo de visión por computadora que procesa la entrada de la cámara y detecta gestos.



