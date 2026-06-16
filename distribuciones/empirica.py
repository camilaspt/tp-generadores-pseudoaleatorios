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