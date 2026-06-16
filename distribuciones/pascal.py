import math
class Pascal:
    def __init__(self, generador_base, k: int, q: float): # k: numero de ensayos, q: probabilidad de exito
        self.generador = generador_base
        self.k = k
        self.q = q
        self.qr = math.log(q)

    def siguiente(self) -> int:
        tr = 1.0
        for _ in range(self.k):
            r = self.generador.siguiente()
            if r <= 0:
                raise ValueError("r debe ser mayor a cero")
            tr *= r
        nx = math.log(tr) / self.qr
        return int(nx)

    def generar(self, cant: int) -> list[int]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cant)]