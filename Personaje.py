class Personaje():
    def __init__(self, nombre = "", cabello = "", ojos = "", piel = "", accesorio = "", genero = ""):
        self.CABELLO = 0
        self.OJOS = 1
        self.PIEL = 2
        self.ACCESORIO = 3
        self.GENERO = 4
        self.nombre = nombre
        self.caracteristicas = []
        self.caracteristicas.append(cabello)
        self.caracteristicas.append(ojos)
        self.caracteristicas.append(piel)
        self.caracteristicas.append(accesorio)
        self.caracteristicas.append(genero)
    
    def DescripcionPersonaje(self):
        print( "\t" + self.nombre + " [" + "Cabello: " + self.caracteristicas[self.CABELLO] + ", Ojos: " + self.caracteristicas[self.OJOS] + ", Piel: " + self.caracteristicas[self.PIEL] + ", Accesorio: " + self.caracteristicas[self.ACCESORIO] + ",Genero: " + self.caracteristicas[self.GENERO] + "]\n")
        return
        