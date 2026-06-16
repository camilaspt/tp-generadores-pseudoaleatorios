import math
class Poisson:
    def __init__(self, generador_base, p: float): # p: parametro de la distribucion
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