import random

class GeneradorMersenneTwister:
    def __init__(self, semilla):
        self.generador = random.Random(semilla)

    def siguiente(self):
        return self.generador.random()

    def generar(self, cantidad):
        return [self.siguiente() for _ in range(cantidad)]