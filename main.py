"""
Análisis de métodos matemáticos para la física / F1009.4

Equipo:
    - Alejandro Medrano Torres     A00831829
    - Emilio Tehuintle Ramírez
    - Mauricio Antonio Castillón Tello
    - Diego Alejandro Flores Meza
    - Pablo Gabriel Galeana Benítez

Descripción:
    Script principal. Graba unos segundos de audio desde el micrófono,
    lo guarda como .wav y manda llamar las funciones de análisis para
    identificar la canción, parecido a como funciona Shazam.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf

from shazam_functions import shazam_sample, shazam_song


# Parámetros de grabación, los mismos que teníamos en MATLAB
TIEMPO  = 5        # cuántos segundos vamos a grabar
FREC    = 44100    # frecuencia de muestreo estándar en Hz
CANALES = 2        # estéreo
ARCHIVO = "Sample" # nombre del archivo que vamos a guardar


def main() -> None:
    # Le avisamos al usuario que va a empezar la grabación
    input("Vamos a comenzar a grabar, presiona Enter cuando estés listo...")
    print("Iniciando la grabación...")

    # Grabamos el audio directamente como arreglo de numpy
    audio = sd.rec(
        frames=int(TIEMPO * FREC),
        samplerate=FREC,
        channels=CANALES,
        dtype=np.int16,
    )
    sd.wait()  # esperamos a que termine antes de seguir
    print("Terminando la grabación, espera...")

    # Guardamos el audio en un .wav con 16 bits, igual que en MATLAB
    nombre_archivo = f"{ARCHIVO}.wav"
    sf.write(nombre_archivo, audio, FREC, subtype="PCM_16")
    print(f"Audio guardado como '{nombre_archivo}'.")

    # Le preguntamos si ya tiene la base de datos para no generarla de nuevo
    valor = int(input(
        "\n¿Actualmente cuenta con nuestra base de datos descargada?\n"
        "Teclee 1 para sí y 0 para no: "
    ))

    # Mandamos llamar nuestras funciones
    # Si no tiene la base de datos, detectamos automáticamente los .wav de la carpeta
    shazam_sample(ARCHIVO)
    shazam_song(valor, archivo_muestra=ARCHIVO)


if __name__ == "__main__":
    main()
