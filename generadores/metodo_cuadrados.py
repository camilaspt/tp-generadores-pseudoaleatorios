class GeneradorMetodoCuadrados:
    def __init__(self, semilla: int, digitos: int = 4):
        if semilla < 0 or semilla >= 10**digitos:
            raise ValueError(f"La semilla debe tener {digitos} dígitos")
        self.semilla = semilla
        self.digitos = digitos
        self.maximo = 10**digitos

    def siguiente(self) -> float:
        cuadrado = self.semilla ** 2
        texto = str(cuadrado).zfill(2 * self.digitos)
        inicio = (2 * self.digitos - self.digitos) // 2
        fin = inicio + self.digitos
        self.semilla = int(texto[inicio:fin])
        return self.semilla / self.maximo
    
    def generar(self, cantidad: int) -> list[float]:
        if cantidad <= 0:
            raise ValueError("La cant debe ser mayor a cero")
        return [self.siguiente() for _ in range(cantidad)]
    