# Calculadora por gestos

Práctica 3 (Unidad IV) de Sistemas Interactivos Inteligentes, Universidad Intercontinental de la Empresa (UIE).

Calculadora controlada con gestos de la mano captados por la webcam. Realiza suma, resta, multiplicación y división, además de borrado y reset.

## Sistema operativo empleado

Windows 11, ejecutado con **uv** (sin Docker).

## Ejecución

### Windows y macOS (uv)

Desde la carpeta del proyecto:

    uv venv
    uv pip install -r requirements.txt
    uv run python src/gest-calc/webcam_test.py
    uv run python src/gest-calc/main.py

`webcam_test.py` sirve para comprobar la cámara. Se cierra con `q` o `Esc`.

### Linux (Docker)

    make build
    make run

Importante: la receta `run` del Makefile debe apuntar a `main.py` en lugar de `sample_main.py`. Esta opción no se ha probado, ya que el desarrollo se hizo en Windows.

## Requisitos

- Python 3.12 (indicado en `.python-version`)
- Dependencias con versiones fijadas en `requirements.txt` (MediaPipe 0.10.21, se mantiene la versión del enunciado)
- Webcam en el índice 0 (`CAMERA_INDEX` en `main.py`)

## Gestos

Se usa la mano y el recuento de dedos extendidos.

| Situación | Gesto | Acción |
|---|---|---|
| Dos manos visibles | Suma de dedos extendidos de ambas manos (0-9) | Escribe ese dígito |
| Una mano | Solo índice | `+` |
| Una mano | Índice y corazón | `-` |
| Una mano | Índice, corazón y anular | `×` |
| Una mano | Cuatro dedos (sin pulgar) | `÷` |
| Una mano | Palma abierta (5 dedos) | `=` |
| Una mano | Solo pulgar | Borrar el último elemento |
| Una mano | Solo meñique | Reset |

Ejemplo, `12 + 7 =`: dígito 1, dígito 2, índice, dígito 7, palma abierta.

## Estructura

    src/gest-calc/
        calculator.py    Lógica de la calculadora (sin cámara ni interfaz)
        gestures.py      Detección de dedos, clasificación de gestos y estabilización
        main.py          Captura de vídeo, interfaz y bucle principal
        webcam_test.py   Prueba de cámara (proporcionado)
        sample_main.py   Ejemplo base (proporcionado)

## Decisiones de diseño

- **Detección de dedos:** MediaPipe Hands da 21 landmarks por mano. Un dedo se considera extendido si su punta está más lejos de la muñeca que su articulación intermedia. Se comparan distancias y no coordenadas `y`, para que funcione con la mano inclinada. El pulgar se compara respecto a la base del meñique.
- **Evitar gestos accidentales:**
  1. Suavizado por votación sobre los últimos 7 fotogramas (al menos 5 coincidentes).
  2. Tiempo de permanencia de 0,8 s antes de confirmar un gesto (1,5 s para el reset, por ser destructivo).
  3. Disparo único: un gesto no se repite hasta cambiar de gesto o bajar las manos.
- **Feedback visual:** la interfaz muestra el gesto detectado y una barra de progreso de la confirmación.
- **Interfaz:** pantalla completa y efecto espejo, para legibilidad a distancia y para que el movimiento resulte natural.
- **Separación en módulos:** lógica, visión e interfaz están desacopladas, lo que facilita probar y mantener cada parte.
- **División por cero:** se muestra un mensaje de error y se reinicia al siguiente dígito.

## Obstáculos encontrados

- MediaPipe en Windows no encontraba su modelo (`hand_landmark_tracking_cpu.binarypb`) cuando el proyecto estaba en una ruta con caracteres no ASCII (la «ñ» de `4_Año`) y dentro de OneDrive. Solución: trabajar en una ruta sin ñ ni OneDrive (`C:\dev`).
- El pulgar es el dedo más difícil de detectar de forma fiable. Se mitiga con el suavizado y el tiempo de permanencia.

## Limitaciones

- Sensible a la iluminación y al ángulo de la mano.
- No hay punto decimal.
- Fatiga en uso prolongado (brazos en alto).
'@ | Set-Content -Encoding utf8 README.md
