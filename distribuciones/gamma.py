import math

class Gamma:
    def __init__(self, generador_base, k: int, a: float): # k: numero de ensayos, a: parametro de forma
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