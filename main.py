import csv
from pathlib import Path
import matplotlib.pyplot as plt

from generadores.gcl import GCL
from generadores.metodo_cuadrados import GeneradorMetodoCuadrados
from generadores.python_random import GeneradorMersenneTwister

CANTIDAD = 10_000
SEMILLA_GCL = 12345
SEMILLA_CUADRADOS = 9731
SEMILLA_PYTHON = 42

def crear_generadores() -> dict:
    return {
        "GCL": GCL(semilla=SEMILLA_GCL),
        "Metodo cuadrados": GeneradorMetodoCuadrados(semilla=SEMILLA_CUADRADOS),
        "Python random": GeneradorMersenneTwister(semilla=SEMILLA_PYTHON),
    }

def generar_muestras(generadores: dict, cant: int) -> dict[str, list[float]]:
    muestras = {}
    for nombre, generador in generadores.items():
        try:
            muestras[nombre] = generador.generar(cant)
        except ValueError as error:
            print(f"Error en {nombre}: {error}")
    return muestras

def guardar_graficos(muestras: dict[str, list[float]], carpeta: Path) -> None:
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, valores in muestras.items():
        if not valores:
            continue
        plt.figure(figsize=(8, 4))
        plt.scatter(range(len(valores)), valores, s=1, alpha=0.5)
        plt.title(f"Generador: {nombre}")
        plt.xlabel("Indice")
        plt.ylabel("Valor")
        plt.tight_layout()
        nombre_archivo = nombre.lower().replace(" ", "_") + ".png"
        plt.savefig(carpeta / nombre_archivo, dpi=150)
        plt.close()
        print(f"Grafico guardado: {carpeta / nombre_archivo}")


if __name__ == "__main__":
    generadores = crear_generadores()
    muestras = generar_muestras(generadores, CANTIDAD)
    guardar_graficos(muestras, Path("salida") / "figuras")
    for nombre, valores in muestras.items():
        print(f"{nombre}: {len(valores)} valores, primeros 5 = {valores[:5]}")