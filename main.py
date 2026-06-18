from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from distribuciones.binomial import Binomial
from distribuciones.empirica import EmpiricaDiscreta
from distribuciones.exponencial import Exponencial
from distribuciones.gamma import Gamma
from distribuciones.hipergeometrica import Hipergeometrica
from distribuciones.normal import Normal
from distribuciones.pascal import Pascal
from distribuciones.poisson import Poisson
from distribuciones.uniforme import UniformeContinua
from generadores.python_random import GeneradorMersenneTwister


CANTIDAD = 10_000
ALFA = 0.05
SEMILLA_BASE = 42
CARPETA_FIGURAS = Path("salida") / "figuras" / "distribuciones"
NORMAL_ESTANDAR = NormalDist()


@dataclass(frozen=True)
class Distribucion:
    nombre: str
    generador: object
    media_teorica: float
    varianza_teorica: float
    tipo: str
    archivo: str
    parametros: str
    pmf: callable | None = None
    pdf: callable | None = None
    cdf: callable | None = None
    ppf: callable | None = None
    soporte: tuple[int, int] | None = None
    bins: int = 30


def nuevo_generador(offset: int) -> GeneradorMersenneTwister:
    return GeneradorMersenneTwister(SEMILLA_BASE + offset)


def comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def gamma_erlang_cdf(x: float, k: int, lam: float) -> float:
    if x <= 0:
        return 0.0
    suma = sum((lam * x) ** i / math.factorial(i) for i in range(k))
    return 1.0 - math.exp(-lam * x) * suma


def buscar_cuantil(cdf, prob: float, minimo: float, maximo: float) -> float:
    while cdf(maximo) < prob:
        maximo *= 2
    bajo, alto = minimo, maximo
    for _ in range(80):
        medio = (bajo + alto) / 2
        if cdf(medio) < prob:
            bajo = medio
        else:
            alto = medio
    return (bajo + alto) / 2


def gammaincc_regularizado(a: float, x: float) -> float:
    """Q(a, x), usado para el p-value de Chi-cuadrado sin depender de scipy."""
    if x < 0 or a <= 0:
        raise ValueError("Parametros invalidos para gammaincc")
    if x == 0:
        return 1.0

    eps = 1e-14
    gln = math.lgamma(a)
    if x < a + 1:
        ap = a
        termino = 1 / a
        suma = termino
        for _ in range(1000):
            ap += 1
            termino *= x / ap
            suma += termino
            if abs(termino) < abs(suma) * eps:
                p = suma * math.exp(-x + a * math.log(x) - gln)
                return max(0.0, min(1.0, 1.0 - p))
        p = suma * math.exp(-x + a * math.log(x) - gln)
        return max(0.0, min(1.0, 1.0 - p))

    b = x + 1 - a
    c = 1 / 1e-300
    d = 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            q = math.exp(-x + a * math.log(x) - gln) * h
            return max(0.0, min(1.0, q))
    q = math.exp(-x + a * math.log(x) - gln) * h
    return max(0.0, min(1.0, q))


def crear_distribuciones() -> list[Distribucion]:
    uniforme_a, uniforme_b = 2.0, 8.0
    exp_media = 2.0
    gamma_k, gamma_lam = 3, 0.5
    normal_mu, normal_sigma = 10.0, 2.0
    pascal_k, pascal_q = 3, 0.4
    binomial_n, binomial_p = 20, 0.3
    hiper_n, hiper_muestra, hiper_p = 100, 10, 0.3
    hiper_k = int(hiper_n * hiper_p)
    poisson_lam = 4.0
    emp_valores = [2, 5, 7]
    emp_freq = [10, 30, 60]
    emp_probs = [f / sum(emp_freq) for f in emp_freq]

    return [
        Distribucion(
            "Uniforme",
            UniformeContinua(nuevo_generador(1), uniforme_a, uniforme_b),
            5.0,
            3.0,
            "continua",
            "uniforme_histograma.png",
            "$a=2$, $b=8$",
            pdf=lambda x: 1 / (uniforme_b - uniforme_a)
            if uniforme_a <= x <= uniforme_b else 0.0,
            cdf=lambda x: 0.0 if x < uniforme_a else 1.0
            if x > uniforme_b else (x - uniforme_a) / (uniforme_b - uniforme_a),
            ppf=lambda p: uniforme_a + (uniforme_b - uniforme_a) * p,
            bins=30,
        ),
        Distribucion(
            "Exponencial",
            Exponencial(nuevo_generador(2), exp_media),
            exp_media,
            exp_media**2,
            "continua",
            "exponencial_histograma.png",
            "$\\mu=2$",
            pdf=lambda x: (1 / exp_media) * math.exp(-x / exp_media)
            if x >= 0 else 0.0,
            cdf=lambda x: 0.0 if x < 0 else 1 - math.exp(-x / exp_media),
            ppf=lambda p: -exp_media * math.log(1 - p),
            bins=35,
        ),
        Distribucion(
            "Gamma",
            Gamma(nuevo_generador(3), gamma_k, gamma_lam),
            gamma_k / gamma_lam,
            gamma_k / gamma_lam**2,
            "continua",
            "gamma_histograma.png",
            "$k=3$, $\\lambda=0.5$",
            pdf=lambda x: (gamma_lam**gamma_k * x ** (gamma_k - 1)
                           * math.exp(-gamma_lam * x) / math.factorial(gamma_k - 1))
            if x >= 0 else 0.0,
            cdf=lambda x: gamma_erlang_cdf(x, gamma_k, gamma_lam),
            ppf=lambda p: buscar_cuantil(lambda y: gamma_erlang_cdf(y, gamma_k, gamma_lam),
                                         p, 0.0, 20.0),
            bins=35,
        ),
        Distribucion(
            "Normal",
            Normal(nuevo_generador(4), normal_mu, normal_sigma),
            normal_mu,
            normal_sigma**2,
            "continua",
            "normal_histograma.png",
            "$\\mu=10$, $\\sigma=2$",
            pdf=lambda x: NORMAL_ESTANDAR.pdf((x - normal_mu) / normal_sigma) / normal_sigma,
            cdf=lambda x: NORMAL_ESTANDAR.cdf((x - normal_mu) / normal_sigma),
            ppf=lambda p: normal_mu + normal_sigma * NORMAL_ESTANDAR.inv_cdf(p),
            bins=35,
        ),
        Distribucion(
            "Pascal",
            Pascal(nuevo_generador(5), pascal_k, pascal_q),
            pascal_k * pascal_q / (1 - pascal_q),
            pascal_k * pascal_q / (1 - pascal_q) ** 2,
            "discreta",
            "pascal_barras.png",
            "$k=3$, $Q=0.4$",
            pmf=lambda x: comb(x + pascal_k - 1, x) * (1 - pascal_q) ** pascal_k
            * pascal_q**x,
            soporte=(0, 18),
        ),
        Distribucion(
            "Binomial",
            Binomial(nuevo_generador(6), binomial_n, binomial_p),
            binomial_n * binomial_p,
            binomial_n * binomial_p * (1 - binomial_p),
            "discreta",
            "binomial_barras.png",
            "$n=20$, $p=0.3$",
            pmf=lambda x: comb(binomial_n, x) * binomial_p**x * (1 - binomial_p) ** (binomial_n - x),
            soporte=(0, binomial_n),
        ),
        Distribucion(
            "Hipergeometrica",
            Hipergeometrica(nuevo_generador(7), hiper_n, hiper_muestra, hiper_p),
            hiper_muestra * hiper_k / hiper_n,
            hiper_muestra * hiper_k / hiper_n * (1 - hiper_k / hiper_n)
            * (hiper_n - hiper_muestra) / (hiper_n - 1),
            "discreta",
            "hipergeometrica_barras.png",
            "$N=100$, $n=10$, $K=30$",
            pmf=lambda x: comb(hiper_k, x) * comb(hiper_n - hiper_k, hiper_muestra - x)
            / comb(hiper_n, hiper_muestra),
            soporte=(0, hiper_muestra),
        ),
        Distribucion(
            "Poisson",
            Poisson(nuevo_generador(8), poisson_lam),
            poisson_lam,
            poisson_lam,
            "discreta",
            "poisson_barras.png",
            "$\\lambda=4$",
            pmf=lambda x: math.exp(-poisson_lam) * poisson_lam**x / math.factorial(x),
            soporte=(0, 18),
        ),
        Distribucion(
            "Empirica",
            EmpiricaDiscreta(nuevo_generador(9), emp_valores, emp_freq),
            sum(v * p for v, p in zip(emp_valores, emp_probs)),
            sum((v**2) * p for v, p in zip(emp_valores, emp_probs))
            - sum(v * p for v, p in zip(emp_valores, emp_probs)) ** 2,
            "discreta",
            "empirica_barras.png",
            "valores $\\{2,5,7\\}$, frecuencias $\\{10,30,60\\}$",
            pmf=lambda x: dict(zip(emp_valores, emp_probs)).get(x, 0.0),
            soporte=(min(emp_valores), max(emp_valores)),
        ),
    ]


def chi_cuadrado_continuo(datos: np.ndarray, dist: Distribucion, grupos: int = 10) -> dict:
    probs = np.linspace(0.0, 1.0, grupos + 1)
    bordes = [-np.inf]
    bordes.extend(dist.ppf(float(p)) for p in probs[1:-1])
    bordes.append(np.inf)
    observadas, _ = np.histogram(datos, bins=bordes)
    esperadas = np.full(grupos, datos.size / grupos)
    chi2 = float(np.sum((observadas - esperadas) ** 2 / esperadas))
    gl = grupos - 1
    p_value = gammaincc_regularizado(gl / 2, chi2 / 2)
    return {"chi2": chi2, "gl": gl, "p_value": p_value}


def chi_cuadrado_discreto(datos: np.ndarray, dist: Distribucion) -> dict:
    minimo, maximo = dist.soporte
    valores = list(range(minimo, maximo + 1))
    observadas = np.array([np.sum(datos == x) for x in valores], dtype=float)
    esperadas = np.array([datos.size * dist.pmf(x) for x in valores], dtype=float)

    cola_alta_obs = np.sum(datos > maximo)
    cola_alta_esp = datos.size * max(0.0, 1.0 - sum(dist.pmf(x) for x in valores))
    if cola_alta_obs or cola_alta_esp >= 1e-9:
        observadas = np.append(observadas, cola_alta_obs)
        esperadas = np.append(esperadas, cola_alta_esp)

    obs_agrupadas = []
    esp_agrupadas = []
    obs_acum = esp_acum = 0.0
    for obs, esp in zip(observadas, esperadas):
        obs_acum += obs
        esp_acum += esp
        if esp_acum >= 5:
            obs_agrupadas.append(obs_acum)
            esp_agrupadas.append(esp_acum)
            obs_acum = esp_acum = 0.0
    if esp_acum > 0:
        if esp_agrupadas:
            obs_agrupadas[-1] += obs_acum
            esp_agrupadas[-1] += esp_acum
        else:
            obs_agrupadas.append(obs_acum)
            esp_agrupadas.append(esp_acum)

    obs = np.array(obs_agrupadas)
    esp = np.array(esp_agrupadas)
    chi2 = float(np.sum((obs - esp) ** 2 / esp))
    gl = max(1, len(esp) - 1)
    p_value = gammaincc_regularizado(gl / 2, chi2 / 2)
    return {"chi2": chi2, "gl": gl, "p_value": p_value}


def evaluar(datos: np.ndarray, dist: Distribucion) -> dict:
    prueba = (chi_cuadrado_continuo(datos, dist)
              if dist.tipo == "continua" else chi_cuadrado_discreto(datos, dist))
    return {
        "nombre": dist.nombre,
        "media": float(np.mean(datos)),
        "media_teorica": dist.media_teorica,
        "varianza": float(np.var(datos)),
        "varianza_teorica": dist.varianza_teorica,
        "chi2": prueba["chi2"],
        "gl": prueba["gl"],
        "p_value": prueba["p_value"],
        "resultado": "ACEPTA H0" if prueba["p_value"] > ALFA else "RECHAZA H0",
        "archivo": dist.archivo,
    }


def guardar_grafico(datos: np.ndarray, dist: Distribucion) -> Path:
    CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_FIGURAS / dist.archivo

    plt.figure(figsize=(8, 4.5))
    if dist.tipo == "continua":
        plt.hist(datos, bins=dist.bins, density=True, color="#4c78a8",
                 edgecolor="white", alpha=0.75, label="Muestra")
        xs = np.linspace(float(np.min(datos)), float(np.max(datos)), 400)
        ys = [dist.pdf(float(x)) for x in xs]
        plt.plot(xs, ys, color="#d62728", linewidth=2, label="Densidad teorica")
        plt.ylabel("Densidad")
    else:
        valores, frecuencias = np.unique(datos.astype(int), return_counts=True)
        plt.bar(valores - 0.18, frecuencias / datos.size, width=0.36,
                color="#4c78a8", alpha=0.8, label="Frecuencia relativa")
        minimo, maximo = dist.soporte
        xs = np.arange(minimo, maximo + 1)
        ps = np.array([dist.pmf(int(x)) for x in xs])
        plt.bar(xs + 0.18, ps, width=0.36, color="#f58518", alpha=0.8,
                label="Probabilidad teorica")
        plt.ylabel("Probabilidad")
        plt.xticks(xs)

    plt.title(f"Distribucion {dist.nombre} - {dist.parametros}")
    plt.xlabel("Valor")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ruta, dpi=150)
    plt.close()
    return ruta


def imprimir_resultados(resultados: list[dict]) -> None:
    print("\nRESULTADOS TP 2.2")
    print(f"N = {CANTIDAD} | alpha = {ALFA} | semilla base = {SEMILLA_BASE}")
    print()
    encabezado = (
        "Distribucion        Media obs.  Media teo.  Var obs.  Var teo.  "
        "Chi2      gl  p-value  Resultado     Figura"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for r in resultados:
        print(
            f"{r['nombre']:<18} {r['media']:>10.4f} {r['media_teorica']:>10.4f} "
            f"{r['varianza']:>9.4f} {r['varianza_teorica']:>9.4f} "
            f"{r['chi2']:>8.4f} {r['gl']:>3} {r['p_value']:>8.4f} "
            f"{r['resultado']:<13} {CARPETA_FIGURAS / r['archivo']}"
        )


def main() -> None:
    resultados = []
    for dist in crear_distribuciones():
        datos = np.asarray(dist.generador.generar(CANTIDAD), dtype=float)
        resultado = evaluar(datos, dist)
        ruta = guardar_grafico(datos, dist)
        resultados.append(resultado)
        print(f"Grafico guardado: {ruta}")

    imprimir_resultados(resultados)


if __name__ == "__main__":
    main()
