"""
cada prueba evalua si una muestra se comporta como una distribucion uniforme U(0,1)
"""

from pathlib import Path

import numpy as np
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# valores teoricos de una distribucion uniforme U(0,1)
MEDIA_TEORICA = 0.5
VARIANZA_TEORICA = 1 / 12


def _validar_muestra(muestra):
    arreglo = np.asarray(muestra, dtype=float)
    if arreglo.size == 0:
        raise ValueError("La muestra no puede estar vacia")
    return arreglo


def prueba_media(muestra):
    datos = _validar_muestra(muestra)
    media = float(np.mean(datos))
    return {
        "media": media,
        "media_teorica": MEDIA_TEORICA,
        "diferencia": abs(media - MEDIA_TEORICA),
    }


def prueba_varianza(muestra):
    datos = _validar_muestra(muestra)
    varianza = float(np.var(datos))
    return {
        "varianza": varianza,
        "varianza_teorica": VARIANZA_TEORICA,
        "diferencia": abs(varianza - VARIANZA_TEORICA),
    }


def test_chi_cuadrado(muestra, intervalos=10, alfa=0.05):
    datos = _validar_muestra(muestra)
    n = datos.size

    bordes = np.linspace(0.0, 1.0, intervalos + 1)
    observadas, _ = np.histogram(datos, bins=bordes)
    esperadas = np.full(intervalos, n / intervalos)

    chi2 = float(np.sum((observadas - esperadas) ** 2 / esperadas))
    grados_libertad = intervalos - 1
    p_value = float(stats.chi2.sf(chi2, grados_libertad))
    acepta = p_value > alfa

    return {
        "chi2": chi2,
        "grados_libertad": grados_libertad,
        "p_value": p_value,
        "alfa": alfa,
        "resultado": "ACEPTA H0" if acepta else "RECHAZA H0",
        "observadas": observadas,
        "esperadas": esperadas,
    }


def test_corridas(muestra, alfa=0.05):
    datos = _validar_muestra(muestra)
    media = np.mean(datos)

    # 1 si el valor esta por encima de la media, 0 si esta por debajo.
    # Se descartan los valores exactamente iguales a la media.
    signos = datos[datos != media] >= media
    if signos.size < 2:
        raise ValueError("Muestra insuficiente para el test de corridas")

    n1 = int(np.sum(signos))       # valores arriba de la media
    n2 = int(signos.size - n1)     # valores abajo de la media
    if n1 == 0 or n2 == 0:
        raise ValueError("Todos los valores estan del mismo lado de la media")

    # Una corrida termina cada vez que cambia el signo.
    corridas = int(1 + np.sum(signos[1:] != signos[:-1]))

    n = n1 + n2
    media_corridas = (2 * n1 * n2) / n + 1
    var_corridas = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n**2 * (n - 1))

    z = (corridas - media_corridas) / np.sqrt(var_corridas)
    p_value = float(2 * stats.norm.sf(abs(z)))  # prueba de dos colas
    acepta = p_value > alfa

    return {
        "corridas": corridas,
        "corridas_esperadas": float(media_corridas),
        "z": float(z),
        "p_value": p_value,
        "alfa": alfa,
        "resultado": "ACEPTA H0" if acepta else "RECHAZA H0",
    }


def evaluar_generador(nombre, muestra, alfa=0.05):
    return {
        "nombre": nombre,
        "n": len(muestra),
        "media": prueba_media(muestra),
        "varianza": prueba_varianza(muestra),
        "chi_cuadrado": test_chi_cuadrado(muestra, alfa=alfa),
        "corridas": test_corridas(muestra, alfa=alfa),
    }


def guardar_histograma(nombre, muestra, carpeta, intervalos=10):
    datos = _validar_muestra(muestra)
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4))
    plt.hist(datos, bins=intervalos, range=(0, 1), color="steelblue",
             edgecolor="black", alpha=0.75)
    # Linea de frecuencia esperada para una distribucion uniforme.
    esperada = datos.size / intervalos
    plt.axhline(esperada, color="red", linestyle="--",
                label=f"Esperado ({esperada:.0f})")
    plt.title(f"Histograma - {nombre}")
    plt.xlabel("Valor")
    plt.ylabel("Frecuencia")
    plt.legend()
    plt.tight_layout()

    ruta = carpeta / (nombre.lower().replace(" ", "_") + "_histograma.png")
    plt.savefig(ruta, dpi=150)
    plt.close()
    return ruta


def guardar_dispersion(nombre, muestra, carpeta):
    """Crea y guarda un grafico de dispersion (valor vs indice)."""
    datos = _validar_muestra(muestra)
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 4))
    plt.scatter(range(datos.size), datos, s=1, alpha=0.5, color="steelblue")
    plt.title(f"Dispersion - {nombre}")
    plt.xlabel("Indice")
    plt.ylabel("Valor")
    plt.tight_layout()

    ruta = carpeta / (nombre.lower().replace(" ", "_") + ".png")
    plt.savefig(ruta, dpi=150)
    plt.close()
    return ruta


def imprimir_tabla(resultados, alfa=0.05):
    titulo = "TABLA COMPARATIVA - PRUEBAS ESTADISTICAS (U(0,1))"
    subtitulo = (
        f"Referencia teorica: media = 0.5 | varianza = 1/12 = 0.0833 | "
        f"alpha = {alfa} (p > {alfa} => ACEPTA H0)"
    )

    encabezados = [
        "Generador",
        "Media muestral",
        "Varianza muestral",
        "Chi-cuadrado",
        "p-valor Chi2",
        "Uniformidad",
        "Z corridas",
        "p-valor corridas",
        "Independencia",
    ]
    filas = []
    for r in resultados:
        filas.append([
            r["nombre"],
            f"{r['media']['media']:.4f}",
            f"{r['varianza']['varianza']:.4f}",
            f"{r['chi_cuadrado']['chi2']:.4f}",
            f"{r['chi_cuadrado']['p_value']:.4f}",
            r["chi_cuadrado"]["resultado"],
            f"{r['corridas']['z']:.4f}",
            f"{r['corridas']['p_value']:.4f}",
            r["corridas"]["resultado"],
        ])

    anchos = [max(len(encabezados[i]), *(len(f[i]) for f in filas))
              for i in range(len(encabezados))]
    separador = "-+-".join("-" * a for a in anchos)
    ancho_tabla = len(separador)

    def formatear(fila):
        return " | ".join(c.ljust(anchos[i]) for i, c in enumerate(fila))

    print()
    print(titulo.center(ancho_tabla))
    print(subtitulo)
    print()
    print(formatear(encabezados))
    print(separador)
    for fila in filas:
        print(formatear(fila))
    print()
    print("Columnas 'Uniformidad' y 'Independencia': ACEPTA H0 = compatible con U(0,1); "
          "RECHAZA H0 = evidencia de desvio.")
