class UniformeContinua:
    def __init__(self, generador_base, a: float, b: float):
        if a >= b:
            raise ValueError("a debe ser menor que b")
        self.generador = generador_base
        self.a = a
        self.b = b

    def siguiente(self) -> float:
        r = self.generador.siguiente()
        return self.a + (self.b - self.a) * r

    def generar(self, cant: int) -> list[float]:
        if cant <= 0:
            raise ValueError("cant debe ser mayor que cero")
        return [self.siguiente() for _ in range(cant)]