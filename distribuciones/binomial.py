class Binomial:
    def __init__(self, generador_base, n: int, p: float): # n: numero de ensayos, p: probabilidad de exito
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