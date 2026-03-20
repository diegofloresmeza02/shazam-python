# 🎵 Shazam – Reconocimiento de Audio en Python

**Análisis de métodos matemáticos para la física**
Diego Alejandro Flores Meza


---

## ¿Qué hace este proyecto?

Sistema de reconocimiento de audio inspirado en **Shazam**, desarrollado como parte del curso de *Análisis de métodos matemáticos para la física*. El programa graba unos segundos de audio desde el micrófono, genera su "huella digital" mediante FFT y hashing, y la compara contra una base de datos de canciones para identificar cuál es.

El algoritmo funciona así:

1. **Secuenciación** – Se divide el audio en ventanas de tiempo y se aplica FFT a cada una para obtener el espectrograma.
2. **Key points** – En cada ventana se extraen los picos de frecuencia en 4 rangos: 40–80 Hz, 80–120 Hz, 120–160 Hz y 160–200 Hz.
3. **Hashing** – Los key points se combinan en un único valor hash por ventana usando `hash = 17 * hash + key_point`.
4. **Matching** – Los hashes de la muestra se comparan contra los de cada canción. La que tenga mayor proporción de coincidencias es la identificada.

---

## Estructura del proyecto

```
.
├── main.py                # Script principal: graba y lanza el análisis
├── shazam_functions.py    # Toda la lógica: FFT, hashing e identificación
├── requirements.txt       # Dependencias
└── README.md
```

### Archivos que se generan al correr el programa

| Archivo | Descripción |
|---|---|
| `Sample.wav` | Audio grabado desde el micrófono |
| `SequencedSample.txt` | Espectrograma de la muestra |
| `DataSample.txt` | Tabla de hashes de la muestra |
| `SequencedSong{N}.txt` | Espectrograma de la canción N |
| `DataSong{N}.txt` | Tabla de hashes de la canción N |

---

## Requisitos

- Python **3.9+**
- Un micrófono conectado y funcional
- Archivos `Song1.wav` y `Song2.wav` en la misma carpeta (la base de datos)

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

> **Linux:** puede que necesites instalar `libportaudio2` primero:
> ```bash
> sudo apt-get install libportaudio2
> ```

---

## Cómo usarlo

```bash
python main.py
```

1. Presiona **Enter** cuando el programa lo indique.
2. El audio se graba durante **5 segundos** y se guarda como `Sample.wav`.
3. Indica si ya tienes la base de datos descargada (`1 = sí`, `0 = no`).
   - Si dices `0`, el programa genera los hashes de `Song1.wav` y `Song2.wav`.
4. El programa imprime el número de la canción identificada.

---

## Parámetros configurables

Todos están al inicio de `main.py`:

| Parámetro | Valor por defecto | Descripción |
|---|---|---|
| `TIEMPO` | `5` | Duración de la grabación (segundos) |
| `FREC` | `44100` | Frecuencia de muestreo (Hz) |
| `CANALES` | `2` | Canales de audio (estéreo) |
| `ARCHIVO` | `"Sample"` | Nombre base del archivo de salida |
