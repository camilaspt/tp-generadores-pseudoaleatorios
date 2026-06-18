\documentclass{article}

\usepackage{arxiv}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{graphicx}
\usepackage{float}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{url}
\usepackage{microtype}
\usepackage{placeins}
\usepackage{array}
\usepackage{listings}

\raggedbottom

\lstset{
    language=Python,
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\tiny,
    showstringspaces=false
}

\graphicspath{{salida/figuras/}{salida/figuras/distribuciones/}{images/}}

\title{TP 2.2: Generadores de Números Pseudoaleatorios de Distintas Distribuciones de Probabilidad}

\author{
Berruhet, Marcos\\
47120\\
\texttt{marcos.berruhet@gmail.com} \\
\And
Ceschan, Franco\\
42737\\
\texttt{francoceschan@gmail.com} \\
\And
Nicolas, Pedro\\
51857\\
\texttt{peedrooo1234@gmail.com} \\
\And
Spitale, Camila\\
50429\\
\texttt{camilaspitale26@gmail.com}
}

\begin{document}

\maketitle

\begin{abstract}
El presente trabajo extiende el estudio realizado en el TP 2.1 sobre generadores de números pseudoaleatorios. A partir de un generador base testeado (Mersenne Twister de Python), se implementaron nueve generadores para distribuciones de probabilidad continuas y discretas siguiendo los algoritmos propuestos en el libro "Técnicas de Simulación en computadoras" de Thomas Naylor. Para cada distribución de probabilidad se presentó su fundamentación teórica, la derivación de la función acumulada y su inversa, el código en Python 3.x y pruebas estadísticas de validación. Se generaron muestras de 10.000 valores por distribución y se compararon media y varianza muestrales con sus valores teóricos, complementando el análisis con la prueba Chi-cuadrado de bondad de ajuste cuando corresponde.
\end{abstract}

\keywords{Simulación \and números pseudoaleatorios \and distribuciones de probabilidad \and transformada inversa \and método de rechazo \and Thomas Naylor}

\section{Introducción}

En el trabajo anterior se analizó la calidad de distintos generadores de números pseudoaleatorios uniformes en el intervalo $[0,1)$. Se concluyó que el generador provisto por Python, basado en Mersenne Twister, presenta un comportamiento compatible con una distribución uniforme bajo las pruebas aplicadas. Sin embargo, un generador uniforme por sí solo no alcanza para modelar la mayoría de los fenómenos estudiados en simulación, ya que muchos procesos reales siguen distribuciones exponenciales, normales, binomiales, de Poisson u otras.

La pregunta que se explora en este trabajo es: ¿cómo transformar números uniformes en variables aleatorias con otras distribuciones de probabilidad? La respuesta clásica combina métodos como la transformada inversa, la composición de variables, la simulación directa de experimentos y, en algunos casos, el método de rechazo.

Se tomó como referencia el capítulo 4 del libro "Técnicas de simulación en computadoras" de Thomas Naylor, reproduciendo en Python las rutinas originales en Fortran. El generador base utilizado fue \texttt{random} de Python con semilla fija, dado que en el TP 2.1 demostró un comportamiento adecuado.

\section{Objetivos}

El objetivo general es implementar y validar generadores de números pseudoaleatorios para distintas distribuciones de probabilidad.

Los objetivos específicos son:

\begin{itemize}
    \item Presentar teóricamente cada distribución, incluyendo parámetros, función de probabilidad, media y varianza teóricas.
    \item Describir el método de rechazo para las distribuciones que lo requieren en el informe.
    \item Implementar un programa en Python 3.x por cada distribución, basandose en los algoritmos provistos en "Tecnicas de simulación en computadoras".
    \item Testear las muestras generadas.
    \item Analizar los resultados obtenidos y elaborar conclusiones.
\end{itemize}

\section{Marco teórico}

\subsection{Generador base uniforme}

Todas las distribuciones implementadas parten de un generador base $R \sim U(0,1)$. En este trabajo se utilizó la clase \texttt{GeneradorMersenneTwister}, que encapsula el módulo \texttt{random} de Python con semilla reproducible:

\begin{lstlisting}[caption={Generador base Mersenne Twister.}]
import random

class GeneradorMersenneTwister:
    def __init__(self, semilla):
        self.generador = random.Random(semilla)

    def siguiente(self):
        return self.generador.random()

    def generar(self, cantidad):
        return [self.siguiente() for _ in range(cantidad)]
\end{lstlisting}

\subsection{Método de la transformada inversa}

Sea $X$ una variable aleatoria continua con función de distribución acumulada $F(x)$. Si $R \sim U(0,1)$, entonces:

\[
X = F^{-1}(R)
\]

tiene distribución $F$. Para variables discretas, se comparan las probabilidades acumuladas con un valor uniforme $R$ y se selecciona el menor índice $i$ tal que $R \leq F_i$.

\subsection{Método de rechazo}

Cuando la transformada inversa no es práctica o se desea mayor eficiencia, el método de rechazo genera candidatos $Y$ de una distribución fácil de simular y los acepta con probabilidad proporcional a $f(y)/(c \cdot g(y))$, donde $g$ es una envolvente mayorante de la densidad objetivo $f$. En este informe se describe teóricamente para Uniforme, Exponencial y Normal según lo indicado en la Tabla \ref{tab:requerimientos}.

\begin{table}[htbp]
\centering
\begin{tabular}{lccccc}
\toprule
Distribución & Tipo & T. Inversa & M. Rechazo & Código & Testeo \\
\midrule
Uniforme & continua & sí & sí & sí & sí \\
Exponencial & continua & sí & sí & sí & sí \\
Gamma & continua & sí & no & sí & sí \\
Normal & continua & sí & sí & sí & sí \\
Pascal & discreta & sí & no & sí & sí \\
Binomial & discreta & sí & no & sí & sí \\
Hipergeométrica & discreta & sí & no & sí & sí \\
Poisson & discreta & sí & no & sí & sí \\
Empírica discreta & discreta & sí & no & sí & sí \\
\bottomrule
\end{tabular}
\caption{Cobertura implementada en el informe del TP 2.2.}
\label{tab:requerimientos}
\end{table}

\subsection{Distribución uniforme continua}

\subsubsection{Definición y parámetros}

La variable $X \sim U(a,b)$ tiene densidad:

\[
f(x) = \frac{1}{b-a}, \quad a \leq x \leq b
\]

con media $E[X] = (a+b)/2$ y varianza $Var(X) = (b-a)^2/12$.

\subsubsection{Función acumulada e inversa}

\[
F(x) = \frac{x-a}{b-a} \quad \Rightarrow \quad F^{-1}(r) = a + (b-a)r
\]

\subsubsection{Método de rechazo}

Dado que la transformada inversa es directa, el método de rechazo no resulta necesario en la implementación. Teóricamente, cualquier punto generado uniformemente en $[a,b]$ es aceptado sin descarte adicional.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución uniforme continua.}]
class UniformeContinua:
    def __init__(self, generador_base, a: float, b: float):
        if a >= b:
            raise ValueError("a debe ser menor a b")
        self.generador = generador_base
        self.a = a
        self.b = b

    def siguiente(self) -> float:
        r = self.generador.siguiente()
        return self.a + (self.b - self.a) * r

    def generar(self, cant: int) -> list[float]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución exponencial}

\subsubsection{Definición y parámetros}

La variable exponencial con media $E[X] = \mu$ tiene densidad:

\[
f(x) = \frac{1}{\mu} e^{-x/\mu}, \quad x \geq 0
\]

con $Var(X) = \mu^2$.

\subsubsection{Función acumulada e inversa}

\[
F(x) = 1 - e^{-x/\mu} \quad \Rightarrow \quad F^{-1}(r) = -\mu \ln(r)
\]

\subsubsection{Método de rechazo}

Se puede utilizar una envolvente uniforme o exponencial truncada. Dado que la inversa es cerrada y eficiente, Naylor implementa directamente la transformada inversa.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución exponencial.}]
import math

class Exponencial:
    def __init__(self, generador_base, media: float):
        self.generador = generador_base
        self.media = media

    def siguiente(self) -> float:
        r = self.generador.siguiente()
        if r <= 0:
            raise ValueError("r debe ser mayor a cero para aplicar ln(r)")
        return -self.media * math.log(r)

    def generar(self, cant: int) -> list[float]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución Gamma (Erlang)}

\subsubsection{Definición y parámetros}

La distribución Erlang es un caso particular de la Gamma con parámetro de forma entero $k$. Si $X_i \sim Exp(\lambda)$ son independientes:

\[
Y = \sum_{i=1}^{k} X_i \sim Erlang(k, \lambda)
\]

con $E[Y] = k/\lambda$ y $Var(Y) = k/\lambda^2$.

\subsubsection{Función acumulada e inversa}

La inversa general de la Gamma no es elemental. Naylor utiliza la equivalencia:

\[
Y = -\frac{\ln(R_1 R_2 \cdots R_k)}{\lambda}
\]

donde $R_i \sim U(0,1)$.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución Gamma (Erlang).}]
import math

class Gamma:
    def __init__(self, generador_base, k: int, a: float):
        self.generador = generador_base
        self.k = k
        self.a = a

    def siguiente(self) -> float:
        tr = 1.0
        for _ in range(self.k):
            r = self.generador.siguiente()
            if r <= 0:
                raise ValueError("r debe ser mayor a cero")
            tr *= r
        return -math.log(tr) / self.a

    def generar(self, cant: int) -> list[float]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución normal}

\subsubsection{Definición y parámetros}

La variable $X \sim N(\mu, \sigma^2)$ tiene densidad:

\[
f(x) = \frac{1}{\sigma\sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
\]

\subsubsection{Función acumulada e inversa}

La inversa de la normal no tiene forma cerrada elemental. Naylor propone el teorema del límite central (TLC) con $K=12$ uniformes:

\[
X = \sigma \left(\sum_{i=1}^{12} R_i - 6\right) + \mu
\]

ya que $\sum R_i$ tiene media 6 y varianza 1.

\subsubsection{Método de rechazo}

Alternativamente, la normal puede generarse por rechazo usando una envolvente exponencial o doble exponencial. En el código se implementó el TLC según la rutina de Naylor.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución normal por TLC.}]
class Normal:
    def __init__(self, generador_base, ex: float, stdx: float):
        if stdx <= 0:
            raise ValueError("stdx debe ser mayor a cero")
        self.generador = generador_base
        self.ex = ex
        self.stdx = stdx
        self.k = 12

    def siguiente(self) -> float:
        suma = 0.0
        for _ in range(self.k):
            r = self.generador.siguiente()
            suma += r
        return self.stdx * (suma - 6.0) + self.ex

    def generar(self, cant: int) -> list[float]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución de Pascal (binomial negativa)}

\subsubsection{Definición y parámetros}

La distribución de Pascal modela el número de fracasos antes del $k$-ésimo éxito. Si $G_i$ son geométricas independientes con parámetro de fracaso $Q$:

\[
X = \sum_{i=1}^{k} G_i
\]

con $E[X] = kQ/(1-Q)$ y $Var(X) = kQ/(1-Q)^2$.

\subsubsection{Transformada inversa}

Naylor utiliza la suma de $k$ variables geométricas independientes:

\[
X = \sum_{i=1}^{k} \left\lfloor \frac{\ln(R_i)}{\ln(Q)} \right\rfloor
\]

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución Pascal.}]
import math

class Pascal:
    def __init__(self, generador_base, k: int, q: float):
        self.generador = generador_base
        self.k = k
        self.q = q
        self.qr = math.log(q)

    def siguiente(self) -> int:
        x = 0
        for _ in range(self.k):
            r = self.generador.siguiente()
            if r <= 0:
                raise ValueError("r debe ser mayor a cero")
            x += int(math.log(r) / self.qr)
        return x

    def generar(self, cant: int) -> list[int]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución binomial}

\subsubsection{Definición y parámetros}

La variable $X \sim Bin(n,p)$ representa el número de éxitos en $n$ ensayos de Bernoulli independientes:

\[
P(X=k) = \binom{n}{k} p^k (1-p)^{n-k}
\]

con $E[X] = np$ y $Var(X) = np(1-p)$.

\subsubsection{Simulación}

Se simulan $n$ ensayos: si $R \leq p$ hay éxito, caso contrario fracaso. Se cuenta el total de éxitos.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución binomial.}]
class Binomial:
    def __init__(self, generador_base, n: int, p: float):
        self.generador = generador_base
        self.n = n
        self.p = p

    def siguiente(self) -> int:
        x = 0
        for _ in range(self.n):
            r = self.generador.siguiente()
            if r <= self.p:
                x += 1
        return x

    def generar(self, cant: int) -> list[int]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución hipergeométrica}

\subsubsection{Definición y parámetros}

En una población de tamaño $N$ con $K$ éxitos, al extraer una muestra de tamaño $n$ sin reemplazo, el número de éxitos $X$ sigue una hipergeométrica:

\[
P(X=x) = \frac{\binom{K}{x}\binom{N-K}{n-x}}{\binom{N}{n}}
\]

\subsubsection{Simulación sin reemplazo}

La probabilidad de éxito se actualiza tras cada extracción:

\[
P_{nuevo} = \frac{TN \cdot P - S}{TN - 1}
\]

donde $S=1$ si hubo éxito y $S=0$ en caso contrario.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución hipergeométrica.}]
class Hipergeometrica:
    def __init__(self, generador_base, tn: int, ns: int, p: float):
        self.generador = generador_base
        self.tn = tn
        self.ns = ns
        self.p = p

    def siguiente(self) -> int:
        x = 0
        tn = float(self.tn)
        p = self.p
        for _ in range(self.ns):
            r = self.generador.siguiente()
            if r <= p:
                s = 1.0
                x += 1
            else:
                s = 0.0
            p = (tn * p - s) / (tn - 1.0)
            tn -= 1.0
        return x

    def generar(self, cant: int) -> list[int]:
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución de Poisson}

\subsubsection{Definición y parámetros}

La Poisson de parámetro $\lambda$ modela conteos de eventos:

\[
P(X=k) = \frac{e^{-\lambda}\lambda^k}{k!}
\]

con $E[X] = \lambda$ y $Var(X) = \lambda$.

\subsubsection{Simulación por tiempos exponenciales}

Equivalente a acumular intervalos exponenciales hasta superar $\lambda$. Naylor implementa:

\[
X = \text{cantidad de multiplicaciones } R_i \text{ tales que } \prod R_i \geq e^{-\lambda}
\]

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución de Poisson.}]
import math

class Poisson:
    def __init__(self, generador_base, p: float):
        self.generador = generador_base
        self.p = p

    def siguiente(self) -> int:
        x = 0
        b = math.exp(-self.p)
        tr = 1.0
        while True:
            r = self.generador.siguiente()
            tr *= r
            if tr < b:
                break
            x += 1
        return x

    def generar(self, cant: int) -> list[int]:
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\subsection{Distribución empírica discreta}

\subsubsection{Definición}

Dada una tabla de valores $x_i$ con frecuencias $f_i$, se normalizan a probabilidades $p_i = f_i / \sum f_j$ y se construyen las acumuladas $F_i = \sum_{j=1}^{i} p_j$.

\subsubsection{Transformada inversa discreta}

Se genera $R \sim U(0,1)$ y se retorna el primer $x_i$ tal que $R \leq F_i$.

\subsubsection{Implementación}

\begin{lstlisting}[caption={Generador de distribución empírica discreta.}]
class EmpiricaDiscreta:
    def __init__(self, generador_base, valores: list, frecuencias: list):
        self.generador = generador_base
        self.valores = valores
        total = sum(frecuencias)
        acum = 0.0
        self.acumuladas = []
        for f in frecuencias:
            acum += f / total
            self.acumuladas.append(acum)

    def siguiente(self):
        r = self.generador.siguiente()
        for i, fa in enumerate(self.acumuladas):
            if r <= fa:
                return self.valores[i]
        return self.valores[-1]

    def generar(self, cant: int) -> list:
        return [self.siguiente() for _ in range(cant)]
\end{lstlisting}

\section{Metodología}

El desarrollo se realizó en Python 3.x. Se organizó el proyecto en tres módulos:

\begin{itemize}
    \item \texttt{generadores/}: contiene el generador base uniforme (creado para el TP 2.1)
    \item \texttt{distribuciones/}: contiene una clase por cada distribución.
    \item \texttt{tests/}: contiene las funciones de validación estadística.
\end{itemize}

El programa principal \texttt{main.py} instancia el generador base, crea cada distribución con parámetros centralizados, genera muestras y ejecuta las pruebas correspondientes.

\subsection{Parámetros de simulación}

\begin{table}[htbp]
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{lll}
\toprule
Distribución & Parámetros & Valores teóricos (media / varianza) \\
\midrule
Uniforme & $a=2$, $b=8$ & $5.0000$ / $3.0000$ \\
Exponencial & $\mu=2$ & $2.0000$ / $4.0000$ \\
Gamma & $k=3$, $\lambda=0.5$ & $6.0000$ / $12.0000$ \\
Normal & $\mu=10$, $\sigma=2$ & $10.0000$ / $4.0000$ \\
Pascal & $k=3$, $Q=0.4$ & $2.0000$ / $3.3333$ \\
Binomial & $n=20$, $p=0.3$ & $6.0000$ / $4.2000$ \\
Hipergeométrica & $N=100$, $n=10$, $K/N=0.3$ & $3.0000$ / $1.9091$ \\
Poisson & $\lambda=4$ & $4.0000$ / $4.0000$ \\
Empírica & valores $\{2,5,7\}$, freq. $\{10,30,60\}$ & $5.9000$ / $2.4900$ \\
\bottomrule
\end{tabular}
}
\caption{Parámetros utilizados en la simulación.}
\label{tab:parametros}
\end{table}

Para todas las distribuciones se generó una muestra de tamaño:

\[
N = 10000
\]

con semilla del generador base:

\[
X_0 = 42
\]

y nivel de significación:

\[
\alpha = 0.05
\]

\section{Pruebas estadísticas aplicadas}

\subsection{Comparación de media y varianza}

Para cada distribución se calculó el \textbf{promedio} (media) y la \textbf{varianza} de la muestra generada, y se compararon con los valores teóricos esperados según los parámetros de la Tabla \ref{tab:parametros}. También se reportó la diferencia absoluta entre lo obtenido y lo teórico.

\subsection{Prueba Chi-cuadrado}

Para las distribuciones con testeo obligatorio según el enunciado, se aplicó la prueba Chi-cuadrado de bondad de ajuste:

\[
\chi^2 = \sum_{i=1}^{k} \frac{(O_i - E_i)^2}{E_i}
\]

donde $O_i$ es la frecuencia observada y $E_i$ la esperada bajo la distribución teórica. Si el valor-p es mayor que $\alpha$, se acepta $H_0$ (compatibilidad con la distribución). Para la exponencial se complementó con Kolmogorov-Smirnov.

\subsection{Interpretación de resultados}

\begin{itemize}
    \item \textbf{ACEPTA H0}: no hay evidencia estadística suficiente para rechazar que la muestra proviene de la distribución teórica.
    \item \textbf{RECHAZA H0}: existe evidencia de desvío respecto de la distribución esperada.
    \item \textbf{solo media y varianza}: se comparó el promedio y la varianza muestrales con los teóricos, sin aplicar Chi-cuadrado.
\end{itemize}

\section{Resultados}

La Tabla \ref{tab:resultados} resume los resultados obtenidos con el generador \texttt{random} de Python como fuente uniforme base.

\begin{table}[htbp]
\centering
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccccc}
\toprule
Distribución & Media obs. & Media teo. & Var. obs. & Var. teo. & Chi-cuadrado & Resultado \\
\midrule
Uniforme & 5.0038 & 5.0000 & 2.9663 & 3.0000 & $p=0.8621$ & ACEPTA H0 \\
Exponencial & 2.0149 & 2.0000 & 4.1743 & 4.0000 & $p=0.3605$ & ACEPTA H0 \\
Gamma & 5.9809 & 6.0000 & 11.9320 & 12.0000 & $p=0.3139$ & ACEPTA H0 \\
Normal & 10.0068 & 10.0000 & 4.0185 & 4.0000 & $p=0.8690$ & ACEPTA H0 \\
Pascal & 1.9815 & 2.0000 & 3.2902 & 3.3333 & $p=0.7912$ & ACEPTA H0 \\
Binomial & 5.9774 & 6.0000 & 4.2147 & 4.2000 & $p=0.4904$ & ACEPTA H0 \\
Hipergeométrica & 3.0010 & 3.0000 & 1.9318 & 1.9091 & $p=0.7557$ & ACEPTA H0 \\
Poisson & 4.0261 & 4.0000 & 4.1720 & 4.0000 & $p=0.0682$ & ACEPTA H0 \\
Empírica & 5.9192 & 5.9000 & 2.4725 & 2.4900 & $p=0.3052$ & ACEPTA H0 \\
\bottomrule
\end{tabular}
}
\caption{Resultados estadísticos obtenidos para cada distribución ($N=10000$, $\alpha=0.05$).}
\label{tab:resultados}
\end{table}

Los gráficos generados se guardaron en \texttt{salida/figuras/distribuciones/}. En las distribuciones continuas se compara el histograma de densidad de la muestra con la densidad teórica. En las distribuciones discretas se comparan las frecuencias relativas observadas con las probabilidades teóricas.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.48\textwidth]{uniforme_histograma.png}
\includegraphics[width=0.48\textwidth]{exponencial_histograma.png}
\caption{Histogramas de las distribuciones Uniforme y Exponencial.}
\label{fig:uniforme_exponencial}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.48\textwidth]{gamma_histograma.png}
\includegraphics[width=0.48\textwidth]{normal_histograma.png}
\caption{Histogramas de las distribuciones Gamma y Normal.}
\label{fig:gamma_normal}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.48\textwidth]{pascal_barras.png}
\includegraphics[width=0.48\textwidth]{binomial_barras.png}
\caption{Gráficos de barras de las distribuciones Pascal y Binomial.}
\label{fig:pascal_binomial}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.48\textwidth]{hipergeometrica_barras.png}
\includegraphics[width=0.48\textwidth]{poisson_barras.png}
\caption{Gráficos de barras de las distribuciones Hipergeométrica y Poisson.}
\label{fig:hipergeometrica_poisson}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.58\textwidth]{empirica_barras.png}
\caption{Gráfico de barras de la distribución Empírica discreta.}
\label{fig:empirica}
\end{figure}

\FloatBarrier

\section{Análisis de resultados}

\subsection{Distribuciones continuas}

\textbf{Uniforme:} la media y varianza muestrales se aproximan muy bien a los valores teóricos. El Chi-cuadrado acepta $H_0$, lo que indica compatibilidad con una distribución uniforme en $[2,8]$.

\textbf{Exponencial:} la media y la varianza muestrales se mantienen cercanas a los valores teóricos. El Chi-cuadrado acepta $H_0$, validando la transformada inversa $X = -\mu \ln(R)$.

\textbf{Gamma:} la media y varianza observadas ($5.9809$ y $11.9320$) son cercanas a los valores teóricos ($6.0$ y $12.0$). El resultado es consistente con el comportamiento esperado del algoritmo de Erlang.

\textbf{Normal:} el TLC con $K=12$ produce una media de $10.0068$ y varianza de $4.0185$, muy próximas a $\mu=10$ y $\sigma^2=4$. El Chi-cuadrado acepta $H_0$, lo que indica que la aproximación es adecuada para la muestra analizada.

\subsection{Distribuciones discretas}

\textbf{Pascal y Binomial:} presentan concordancia en media y varianza. Ambas aceptan $H_0$ en la prueba Chi-cuadrado, confirmando la correcta implementación de la suma de geométricas para Pascal y de los ensayos de Bernoulli para Binomial.

\textbf{Hipergeométrica:} la media y la varianza muestrales son muy cercanas a las teóricas. El Chi-cuadrado acepta $H_0$, por lo que no se observa evidencia estadística suficiente para rechazar el ajuste.

\textbf{Poisson:} la media y la varianza muestrales se aproximan a $\lambda=4$. La prueba Chi-cuadrado acepta $H_0$, confirmando el comportamiento esperado del algoritmo basado en el producto de uniformes.

\textbf{Empírica:} la media y varianza muestrales se aproximan a los valores calculados desde la tabla ($5.90$ y $2.49$). El Chi-cuadrado acepta $H_0$, lo que confirma que la selección por probabilidades acumuladas reproduce adecuadamente las frecuencias esperadas.

\section{Conclusiones}

El trabajo permitió implementar nueve generadores de variables aleatorias a partir de un generador uniforme base previamente validado y se reprodujeron los algoritmos de Thomas Naylor en Python.

En términos generales, las nueve distribuciones analizadas mostraron una media y una varianza muestrales cercanas a los valores teóricos. Además, todas aceptaron $H_0$ en la prueba Chi-cuadrado con $\alpha=0.05$, lo que respalda la correcta implementación de los métodos de transformada inversa, TLC, suma de variables y simulación directa.

La corrección aplicada en la distribución de Pascal permitió representar la suma de $k$ geométricas independientes, logrando concordancia con la media y varianza teóricas. Los gráficos generados complementan la lectura numérica y permiten observar visualmente el ajuste entre frecuencias observadas y valores teóricos.

Como conclusión metodológica, la transformación de uniformes en otras distribuciones es una herramienta central en simulación. La validación debe combinar la comparación de media y varianza con pruebas formales de ajuste, especialmente cuando el tamaño muestral es elevado.

\newpage
\begin{thebibliography}{9}

\bibitem{naylor1982}
Naylor, T.H.
\textit{Técnicas de simulación en computadoras}.
1982.

\bibitem{python_random}
Python Software Foundation.
\textit{random --- Generate pseudo-random numbers}.
Disponible en: \url{https://docs.python.org/3/library/random.html}

\bibitem{tp21}
Berruhet, M.; Ceschan, F.; Nicolas, P.; Spitale, C.
\textit{TP 2.1: Generadores Pseudoaleatorios}.
Trabajo práctico previo de la materia Simulación.

\end{thebibliography}

\end{document}
