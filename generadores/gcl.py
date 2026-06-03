class GCL:
    # algoritmo que permite obtener una secuencia de números pseudoaleatorios calculados con una función lineal definida a trozos discontinua
    def __init__(self, semilla: int, multiplicador: int = 12345, incremento: int = 0, modulo: int = 2**31-1):
        if not (0<= semilla < modulo):
            raise ValueError("La semilla debe estar en el rango entre 0 y el modulo")
        self.estado = semilla
        self.multiplicador = multiplicador
        self.incremento = incremento
        self.modulo = modulo

    def sig_entero(self) -> int:
        self.estado = (self.multiplicador * self.estado + self.incremento) % self.modulo
        return self.estado
    
    def siguiente(self) -> float: 
        return self.sig_entero() / self.modulo

    def generar(self, cant: int) -> list[float]:
        if cantidad <= 0:
            raise ValueError("La cant debe ser mayor que cero")
        return [self.siguiente() for _ in range(cantidad)]