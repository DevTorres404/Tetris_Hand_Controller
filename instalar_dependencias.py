import os
import sys
import subprocess

def instalar(paquete):
    print(f"Instalando {paquete}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

def main():
    print("=== Instalador de Dependencias para Tetris ===\n")

    paquetes = [
        "pygame",
        "opencv-python",
        "mediapipe",
        "numpy",
        "urllib3"
    ]

    for pkg in paquetes:
        try:
            __import__(pkg.split("-")[0])
            print(f"{pkg} ya está instalado.")
        except:
            instalar(pkg)

    print("\n✔ Dependencias instaladas correctamente.")

if __name__ == "__main__":
    main()
