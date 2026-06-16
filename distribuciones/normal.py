class Normal:
    def __init__(self, generador_base, ex: float, stdx: float): # ex: media, stdx: desviacion estandar
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