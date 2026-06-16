import math
class Exponencial:
    def __init__(self, generador_base, media: float): # media: media de la distribucion
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