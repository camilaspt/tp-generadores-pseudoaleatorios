from pathlib import Path

from generadores.gcl import GCL
from generadores.metodo_cuadrados import GeneradorMetodoCuadrados
from generadores.python_random import GeneradorMersenneTwister
from tests.pruebas_estadisticas import (
    evaluar_generador,
    guardar_dispersion,
    guardar_histograma,
    imprimir_tabla,
)

CANTIDAD = 10_000
ALFA = 0.05
SEMILLA_GCL = 12345
SEMILLA_CUADRADOS = 9731
SEMILLA_PYTHON = 42
CARPETA_FIGURAS = Path("salida") / "figuras"


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
            print(f"Error al generar con {nombre}: {error}")
    return muestras


def mostrar_detalle(resultado: dict) -> None:
    print(f"\n=== {resultado['nombre']} (n = {resultado['n']}) ===")

    media = resultado["media"]
    print(f"Media     : {media['media']:.5f} (teorica {media['media_teorica']:.5f}, "
          f"dif {media['diferencia']:.5f})")

    var = resultado["varianza"]
    print(f"Varianza  : {var['varianza']:.5f} (teorica {var['varianza_teorica']:.5f}, "
          f"dif {var['diferencia']:.5f})")

    chi = resultado["chi_cuadrado"]
    print(f"Chi2      : {chi['chi2']:.4f} | gl {chi['grados_libertad']} | "
          f"p-value {chi['p_value']:.4f} -> {chi['resultado']}")

    runs = resultado["corridas"]
    print(f"Corridas  : {runs['corridas']} (esperadas {runs['corridas_esperadas']:.1f}) | "
          f"Z {runs['z']:.4f} | p-value {runs['p_value']:.4f} -> {runs['resultado']}")


def main() -> None:
    generadores = crear_generadores()
    muestras = generar_muestras(generadores, CANTIDAD)

    resultados = []
    for nombre, valores in muestras.items():
        if not valores:
            continue
        try:
            resultado = evaluar_generador(nombre, valores, alfa=ALFA)
        except ValueError as error:
            print(f"Error al evaluar {nombre}: {error}")
            continue
        resultados.append(resultado)
        mostrar_detalle(resultado)

        ruta_hist = guardar_histograma(nombre, valores, CARPETA_FIGURAS)
        print(f"Histograma guardado: {ruta_hist}")
        ruta_disp = guardar_dispersion(nombre, valores, CARPETA_FIGURAS)
        print(f"Dispersion guardada: {ruta_disp}")

    imprimir_tabla(resultados, alfa=ALFA)


if __name__ == "__main__":
    main()
