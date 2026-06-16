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