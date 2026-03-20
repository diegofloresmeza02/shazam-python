"""
Análisis de métodos matemáticos para la física / F1009.4

Equipo:
    - Alejandro Medrano Torres     A00831829
    - Emilio Tehuintle Ramírez
    - Mauricio Antonio Castillón Tello
    - Diego Alejandro Flores Meza
    - Pablo Gabriel Galeana Benítez

Descripción:
    Funciones principales del sistema. Aquí está todo el procesamiento:
    secuenciamos el audio con FFT, extraemos los key points, generamos
    el hash y comparamos contra la base de datos para identificar la canción.
"""

import os
import glob
import numpy as np
from scipy.fft import fft
from scipy.io import wavfile
from scipy import stats


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _secuenciar_y_hashear(nombre_wav: str, prefijo_salida: str) -> None:
    """
    Toma un archivo .wav, genera su espectrograma con FFT, extrae los
    key points y guarda la tabla de hashes en disco.
    Esta función la reutilizamos tanto para la muestra como para las canciones.
    """

    # ── Secuenciación ─────────────────────────────────────────────────────

    Fs, S = wavfile.read(nombre_wav)

    # Convertimos estéreo a mono promediando ambos canales
    if S.ndim == 2:
        S_mono = (S[:, 0].astype(float) + S[:, 1].astype(float)) / 2
    else:
        S_mono = S.astype(float)  # ya es mono, no hay problema

    intervalo = 2205  # tamaño de cada ventana de tiempo para la FFT

    # Rellenamos con ceros para que la señal sea divisible exactamente
    espacio = len(S_mono) % intervalo
    if espacio != 0:
        S_mono = np.concatenate([S_mono, np.zeros(intervalo - espacio)])

    espectro = []

    # Corremos la FFT en cada ventana y guardamos la magnitud
    num_intervalos = len(S_mono) // intervalo
    for i in range(num_intervalos):
        S_temp = S_mono[i * intervalo : (i + 1) * intervalo]
        T      = fft(S_temp, intervalo)
        magT   = np.abs(T)
        magT   = magT[:int(np.ceil(intervalo / 2))]  # la FFT es simétrica, solo la mitad
        espectro.append(magT)

    espectro = np.array(espectro)
    np.savetxt(f"Sequenced{prefijo_salida}.txt", espectro, delimiter=",")

    # ── Hashing ───────────────────────────────────────────────────────────
    #
    # Extraemos el pico de frecuencia en 4 rangos de 40 Hz cada uno:
    #   40–80 Hz,  80–120 Hz,  120–160 Hz,  160–200 Hz
    #
    # Estos picos son los "key points": la huella digital del audio.
    # Los rangos se escogieron porque ahí hay mucha actividad en música.

    espectro      = np.loadtxt(f"Sequenced{prefijo_salida}.txt", delimiter=",")
    plot_espectro = espectro[:, 39:200]  # columnas 40–200, base 0 en Python

    key_points = []

    for i in range(plot_espectro.shape[0]):
        fila_keys = []
        for j in range(4):
            sub_inicio = j * 40
            sub_fin    = sub_inicio + 40
            a = np.argmax(plot_espectro[i, sub_inicio:sub_fin])
            fila_keys.append(a + 40 * j)  # índice global dentro de las 160 columnas
        key_points.append(fila_keys)

    key_points = np.array(key_points)

    # Calculamos el hash de cada intervalo de tiempo.
    # Algoritmo recursivo: hash = 17 * hash + key_point
    # Empezamos en 4 para que nunca sea cero
    hash_table = []

    for i in range(key_points.shape[0]):
        h = 4
        for j in range(4):
            h = 17 * h + int(key_points[i, j])
        hash_table.append(h)

    hash_table = np.array(hash_table).reshape(-1, 1)
    np.savetxt(f"Data{prefijo_salida}.txt", hash_table, delimiter=",")


def _detectar_canciones(archivo_muestra: str) -> list[str]:
    """
    Busca automáticamente todos los .wav en la carpeta actual,
    excluyendo el archivo de la muestra grabada.
    Así no importa cómo se llamen las canciones ni cuántas sean.
    """
    todos_los_wav = glob.glob("*.wav")
    canciones = [
        f for f in todos_los_wav
        if f.lower() != f"{archivo_muestra.lower()}.wav"
    ]

    if not canciones:
        raise FileNotFoundError(
            "No se encontraron archivos .wav en la carpeta para usar como base de datos.\n"
            "Agrega al menos un archivo de canción en formato .wav y vuelve a intentarlo."
        )

    canciones.sort()  # orden consistente entre ejecuciones
    print(f"\nSe encontraron {len(canciones)} canción(es) en la base de datos:")
    for c in canciones:
        print(f"  · {c}")

    return canciones


# ─────────────────────────────────────────────────────────────────────────────
#  SHAZAM SAMPLE
#  Procesa el audio grabado y genera su huella digital
# ─────────────────────────────────────────────────────────────────────────────

def shazam_sample(nombre_archivo: str) -> None:
    """
    Toma el .wav grabado, lo convierte a su espectrograma usando FFT,
    extrae los key points y genera la tabla de hashes que después
    vamos a comparar con las canciones de la base de datos.
    """
    print("\nProcesando la muestra grabada...")
    _secuenciar_y_hashear(f"{nombre_archivo}.wav", "Sample")
    print("Muestra procesada correctamente.")


# ─────────────────────────────────────────────────────────────────────────────
#  SHAZAM SONG
#  Genera la base de datos si no existe, y luego identifica la canción
# ─────────────────────────────────────────────────────────────────────────────

def shazam_song(tiene_base_de_datos: int, archivo_muestra: str = "Sample") -> None:
    """
    Detecta automáticamente los .wav de la carpeta para usarlos como base
    de datos. Si tiene_base_de_datos == 0 genera los hashes de cada canción;
    si ya los tiene, los carga directo. Al final compara contra la muestra
    e imprime cuál canción identificó.
    """

    # Detectamos las canciones disponibles en la carpeta
    canciones = _detectar_canciones(archivo_muestra)

    # ── Generamos la base de datos solo si el usuario no la tiene ─────────
    if tiene_base_de_datos == 0:
        print("\nGenerando base de datos, esto puede tardar un momento...")

        for i, cancion_wav in enumerate(canciones):
            prefijo = f"Song{i + 1}"
            print(f"  Procesando '{cancion_wav}'...")
            _secuenciar_y_hashear(cancion_wav, prefijo)

        print("Base de datos generada correctamente.")

    # ── Identificando la canción ──────────────────────────────────────────
    #
    # Normalizamos los vectores Hash-Time dividiéndolos entre 1000 y redondeando.
    # Esto los reduce a 3 cifras significativas y compensa pequeñas diferencias
    # en la lectura de frecuencias, lo que hace el sistema más robusto.
    #
    # Después buscamos cuántos hashes de la muestra coinciden con los de
    # cada canción. La que tenga mayor proporción de coincidencias es la ganadora.

    print("\nBuscando coincidencias...")

    # Cargamos y normalizamos los hashes de la muestra grabada
    muestra_hash = np.loadtxt("DataSample.txt", delimiter=",")
    muestra_hash = np.round(muestra_hash / 1000).astype(int)

    proporciones = []  # proporción de matches por canción

    for i in range(len(canciones)):
        # Cargamos y normalizamos los hashes de la canción actual
        song = np.loadtxt(f"DataSong{i + 1}.txt", delimiter=",")
        song = np.round(song / 1000).astype(int)

        matches = []  # guardamos todos los matches encontrados

        # Buscamos cada hash de la muestra dentro del vector de la canción.
        # find() de MATLAB es equivalente a np.where() en Python
        for idx, h in enumerate(muestra_hash):
            indices = np.where(song == h)[0]
            # restamos el offset de tiempo para alinear los vectores
            matches.extend(indices - idx)

        if len(matches) == 0:
            proporciones.append(0.0)
            continue

        matches = np.array(matches)

        # La moda es el offset más repetido: indica en qué punto
        # los dos vectores se alinean mejor
        moda     = int(stats.mode(matches, keepdims=True).mode[0])
        num_moda = int(np.sum(matches == moda))

        # La proporción nos dice qué tan bien encaja esta canción con la muestra
        p = num_moda / len(muestra_hash)
        proporciones.append(p)

    # La canción con la mayor proporción de matches es la identificada
    idx_ganador = int(np.argmax(proporciones))
    cancion_identificada = canciones[idx_ganador]

    print(f"\nLa canción identificada es: {cancion_identificada}")
