from tkinter import *
from tkinter import ttk
import numpy as np
import random
import math


#---------------------------------------------------------------------

# Parámetros
rows, cols = 20, 20
diffusion_rate = 0.1
cell_size = 20  # Tamaño de cada celda en píxeles

# Inicialización de la cuadrícula
expectativa_inicial_uniforme = 0.1
grid = np.full((rows, cols), expectativa_inicial_uniforme)
#grid[rows // 2, cols // 2] = 0.1  # Comida en el centro

probabilidad_max_hc = 1
tolerancia_hc = 0

# Lista para rastrear las celdas pintadas manualmente
comida_celdas = [[10,10]] #posiciones de comidas

keep_espectativa_1 = []

#---------------------------------------------------------------------

class Animal(): #posicion inicial por defecto 0,0
    def __init__(self, inicial = (0,0)):
        self.posx = inicial[0]
        self.posy = inicial[1]
        self.opciones = ["derecha", "izquierda", "arriba", "abajo"]
        self.estoy_presente = True

        self.tipo = "hill_climbing"
        self.tipos_list = [ "random", "hill_climbing"]# Historial de las últimas 5 posiciones visitadas
        self.historial = []

    def mover_random(self):  # Calcula el movimiento de forma aleatoria
        movimientos_validos = []

        #filtra las opciones para no incluir movimientos que lleven a posiciones del historial
        for step in self.opciones:
            nueva_posx, nueva_posy = self.calcular_nueva_posicion(step)

            #verifica si la nueva posicion esta dentro de los limites y no en el historial
            if (nueva_posx, nueva_posy) not in self.historial and 0 <= nueva_posx < rows and 0 <= nueva_posy < cols:
                movimientos_validos.append(step)

        #si no hay movimientos validos, se puede mover a cualquier lugar
        if not movimientos_validos:
            #pero se asegura que siga dentro de los limites de la cuadricula
            #ademas de no traspasar la barrera
            for step in self.opciones:
                nueva_posx, nueva_posy = self.calcular_nueva_posicion(step)
                if 0 <= nueva_posx < rows and 0 <= nueva_posy < cols:
                    movimientos_validos.append(step)

        #selecciona un movimiento al azar entre los válidos
        step = random.choice(movimientos_validos)
        self.posx, self.posy = self.calcular_nueva_posicion(step)

        #actualiza el historial
        self.actualizar_historial()

        print(self.posx, " ", self.posy, " ", step)
        return [self.posx, self.posy, step]

    def calcular_nueva_posicion(self, step): #calcula la posible posicion en el grid dada una direccion
        """Calcula la nueva posición según el paso dado."""
        nueva_posx, nueva_posy = self.posx, self.posy
        if step == "derecha":
            nueva_posx += 1
        elif step == "izquierda":
            nueva_posx -= 1
        elif step == "abajo":
            nueva_posy += 1
        elif step == "arriba":
            nueva_posy -= 1
        elif step == "arriba-izquierda":
            nueva_posx -= 1
            nueva_posy -= 1
        elif step == "arriba-derecha":
            nueva_posx += 1
            nueva_posy -= 1
        elif step == "abajo-derecha":
            nueva_posx += 1
            nueva_posy += 1
        elif step == "abajo-izquierda":
            nueva_posx -= 1
            nueva_posy += 1
        
        return nueva_posx, nueva_posy

    def actualizar_historial(self):
        """Guarda la posición actual en el historial, eliminando la más antigua si excede 5 posiciones."""
        self.historial.append((self.posx, self.posy))
        if len(self.historial) > 15: #limite maximo del historial de movimientos
            self.historial.pop(0)  #elimina la posicion mas antigua



    #calcula el movimiento basado en Hill Climbing
    def mover_hill_climbing(self, probabilidad_max=probabilidad_max_hc #probabilidad de seguir Hill Climbing
                                , tolerancia=tolerancia_hc #Tolerancia +- para considerar un valor dentro de la proxima escalada maxima
                                ):
        """
        Movimiento Hill Climbing con probabilidad de explorar otras celdas
        y rango de tolerancia para valores cercanos al máximo.
        """

        # Diccionario para almacenar los valores de las posiciones
        valores = {
            "arriba": -1,
            "derecha": -1,
            "abajo": -1,
            "izquierda": -1,
            "arriba-izquierda": -1,
            "arriba-derecha": -1,
            "abajo-izquierda": -1,
            "abajo-derecha": -1,
        }

        # Obtiene los valores de cada posición, considerando los límites del grid
        if self.posx < cols - 1:
            valores["derecha"] = round(grid[self.posx + 1, self.posy], 3)  # derecha

        if self.posx > 0:
            valores["izquierda"] = round(grid[self.posx - 1, self.posy], 3)  # izquierda

        if self.posy < cols - 1:
            valores["abajo"] = round(grid[self.posx, self.posy + 1], 3)  # abajo

            if self.posx < cols - 1:
                valores["abajo-derecha"] = round(grid[self.posx + 1, self.posy + 1], 3)  # abajo-derecha

            if self.posx > 0:
                valores["abajo-izquierda"] = round(grid[self.posx - 1, self.posy + 1], 3)  # abajo-izquierda

        if self.posy > 0:
            valores["arriba"] = round(grid[self.posx, self.posy - 1], 3)  # arriba

            if self.posx < cols - 1:
                valores["arriba-derecha"] = round(grid[self.posx + 1, self.posy - 1], 3)  # arriba-derecha

            if self.posx > 0:
                valores["arriba-izquierda"] = round(grid[self.posx - 1, self.posy - 1], 3)  # arriba-izquierda

        # Encuentra el valor máximo de las posibles direcciones
        valor_mayor = max(valores.values())
        print("Valores completos:", valores)
        print("Valor mayor:", valor_mayor)

        # Filtra las direcciones dentro del rango de tolerancia
        opciones_cercanas = [
            key for key, valor in valores.items()
            if valor_mayor - tolerancia <= valor <= valor_mayor + tolerancia
        ]
        print("Opciones cercanas al máximo:", opciones_cercanas)

        # Decide si elegir la opción máxima o explorar
        if random.random() < probabilidad_max:
            # Elige entre las mejores opciones (dentro del rango)
            key_mayor = random.choice(opciones_cercanas)
            print("Decisión: Tomar una opción cercana al máximo.")
        else:
            # Elige entre todas las opciones válidas aleatoriamente
            opciones_validas = [key for key, valor in valores.items() if valor != -1]
            key_mayor = random.choice(opciones_validas)
            print("Decisión: Explorar otra opción válida.")
        
        print("Dirección elegida:", key_mayor)

        # Mueve en la dirección seleccionada
        self.mover_a(key_mayor)

    def mover_a(self, donde): #actualiza la nueva posicion dado el calculo de movimiento previo
        if donde == "arriba":
            self.posy -= 1
        elif donde == "derecha":
            self.posx += 1
        elif donde == "abajo":
            self.posy += 1
        elif donde == "izquierda":
            self.posx -= 1
        elif donde == "arriba-derecha":
            self.posx += 1
            self.posy -= 1
        elif donde == "arriba-izquierda":
            self.posx -= 1
            self.posy -= 1
        elif donde == "abajo-derecha":
            self.posx += 1
            self.posy += 1
        elif donde == "abajo-izquierda":
            self.posx -= 1
            self.posy += 1
        
    def actual(self): #obtiene la posicion actual del conejo
        if self.estoy_presente:
            return [[self.posx, self.posy]]
        else:
            return []

    def mover(self): #llama la funcion para calcular el movimiento basado en el tipo de movimiento

        if self.tipo == "random":
             self.mover_random()
        elif self.tipo == "hill_climbing":
            self.mover_hill_climbing()

conejo = Animal()


# Función para calcular la difusión
def diffusion_step(grid):
    new_grid = grid.copy()
    for i in range(rows):
        for j in range(cols):
            # Distribuir valores a celdas vecinas
            total_diffusion = 0
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    diffusion = diffusion_rate * grid[i, j]
                    new_grid[ni, nj] += diffusion
                    total_diffusion += diffusion
            new_grid[i, j] -= total_diffusion  # Restar lo que se distribuyó
    return new_grid

# Función para actualizar la visualización
def update_canvas(grid, canvas):
    canvas.delete("all")
    max_value = grid.max()
    for i in range(rows):
        for j in range(cols):
            # Escalar el valor para determinar la intensidad del color
            """
            fixed_max = 1.0  # Valor máximo fijo para la escala
            intensity = int((grid[i, j] / fixed_max) * 255) if fixed_max > 0 else 0
            """

            intensity = int((grid[j,i] / 1) * 255) if 1 > 0 else 0
            color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"  # Color en escala de grises
            x0, y0 = j * cell_size, i * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
    
    #COMIDA
    # Dibujar celdas pintadas manualmente en una capa separada
    for j,i in comida_celdas:
        x0, y0 = j * cell_size, i * cell_size #calcula las posiciones físicas segun el tamano de la malla
        x1, y1 = x0 + cell_size, y0 + cell_size
        #print(x0,"",y0,"",x1,"",y1)
        canvas.create_rectangle(x0, y0, x1, y1, fill="green", outline="")

    #ANIMAL
    # Dibujar celdas pintadas manualmente en una capa separada
    if conejo.estoy_presente:
        for j,i in conejo.actual():
            x0, y0 = j * cell_size, i * cell_size #calcula las posiciones físicas segun el tamano de la malla
            x1, y1 = x0 + cell_size, y0 + cell_size
            #print(x0,"",y0,"",x1,"",y1)
            canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="")
    else:
        print("No hay animel para dibujar")

# Función para ejecutar la simulación paso a paso
def run_simulation(hay_animal, movimiento, pos_inicial, iteraciones, mantener_expectativa_1):
    global grid
    global keep_espectativa_1
    comido = False
    com = []


    print(f"Hay_animal: {hay_animal}")
    if hay_animal:
        conejo.estoy_presente = True
        conejo.tipo = movimiento
        conejo.posx = pos_inicial[0]
        conejo.posy = pos_inicial[1]
        print(f"posx: {conejo.posx}, - posy: {conejo.posy}")
    else:
        conejo.estoy_presente = False
    
    for t in range(iteraciones):
        grid = diffusion_step(grid)
        print("Maximo: ", grid.max(), " - Mínimo: ", grid.min())

        if hay_animal:
            conejo.mover()

            if conejo.actual() == comida_celdas:
                #encontro comida
                x, y = conejo.actual()[0]
                com = [x,y]
                grid[x, y] = 1  #establece el valor de espectativa en 1
                comida_celdas.remove(conejo.actual()[0]) #consume la comida
                comido = True

            else:
                #No hay comida aca
                x, y = conejo.actual()[0] #obitne posicion actual del conejo
                grid[x, y] = 0  #( Comida en el centro) Establece ese lugar en 0 de espectativa

            #ESTO HACE QUE EL CONEJO MANTENGA LA MEMORIA DEL SECTOR DONDE ENCONTRO LA COMIDA
            #Provoca que los valores de expectativa seteado en el sector de la comida se extienda alrededor
                #de lo contrario este se perdería y el conejo perdería total memoria de que cerca de ese lugar hubo comida
            if comido:
                grid[com[0], com[1]] = 1  #establece el valor de espectativa en 1
                keep_espectativa_1 = conejo.actual()[0]

                #Elimina el animal ya que este se va
                conejo.estoy_presente = False
            
        #Mantiene la espectativa de la comida encontrada en 1
        if keep_espectativa_1 != [] and mantener_expectativa_1:
            grid[keep_espectativa_1[0], keep_espectativa_1[1]] = 1  #establece el valor de espectativa en 1
                


        update_canvas(grid, canvas) #actualiza el coloreo
        root.update()  # Actualizar la ventana
        root.after(10)  # Pausar por 100 ms para visualizar los cambios

        #si encuentra la comida y la consume, se rompe el bucle para dar paso a la fase 2
        if comido:
            break



##########################-------------------------
#----INTERFAZ GRAFICA------------------------------
##########################-------------------------

def prueba():
    print(lista_movimientos.get())
    print(animal_value.get())
    try:
        print(list(map(int, texto_pos_inicial.get().split(','))))
    except:
        pass
    print("posicion_incial: ", texto_pos_inicial.get())

# Interfaz gráfica
root = Tk()
root.title("Simulación de Difusión Manual")

# Canvas principal
canvas = Canvas(root, width=cols * cell_size, height=rows * cell_size, bg="white")
canvas.pack()

# Contenedor para los controles y parámetros (debajo del canvas)
bottom_frame = Frame(root, padx=10, pady=10)
bottom_frame.pack(fill=X, expand=True)

# Frame izquierdo (dentro del bottom_frame)
left_frame = Frame(bottom_frame, padx=10, pady=10)
left_frame.pack(side=LEFT, fill=Y)

# Frame derecho (dentro del bottom_frame)
right_frame = Frame(bottom_frame, padx=10, pady=10)
right_frame.pack(side=RIGHT, fill=Y)

# Controles en el frame izquierdo
# Check para activar o desactivar el animal
animal_value = BooleanVar()
animal_value.set(True)
check_animal = ttk.Checkbutton(left_frame, text="animal", variable=animal_value)
check_animal.pack()

# Para seleccionar el tipo de movimiento
Label(left_frame, text="Movimiento:").pack()
lista_movimientos = ttk.Combobox(left_frame, values=conejo.tipos_list)
lista_movimientos.set(conejo.tipos_list[0])  # Por defecto tiene el primero de la lista
lista_movimientos.pack()

# Posición inicial del animal
texto_pos_inicial = StringVar()
Label(left_frame, text="Posición inicial:").pack()
posicion_inicial = ttk.Entry(left_frame, textvariable=texto_pos_inicial)
texto_pos_inicial.set("0,0")  # posición inicial por defecto
posicion_inicial.pack()

# Número de iteraciones
texto_iteraciones = StringVar()
Label(left_frame, text="Iteraciones:").pack()
iteraciones = ttk.Entry(left_frame, textvariable=texto_iteraciones)
texto_iteraciones.set("800")  # iteraciones por defecto
iteraciones.pack()

# Check para mantener expectativa 1
expectativa_value = BooleanVar()
expectativa_value.set(True)
check_expectativa = ttk.Checkbutton(left_frame, text="Mantener expectativa", variable=expectativa_value)
check_expectativa.pack()

# Botón para iniciar la simulación
start_button = Button(left_frame, text="Iniciar Simulación", command=lambda: run_simulation(
    animal_value.get(),
    lista_movimientos.get(),
    list(map(int, posicion_inicial.get().split(','))),
    int(iteraciones.get()),
    expectativa_value.get()))
start_button.pack()

# Botón de prueba
boton_prueba = Button(left_frame, text="prueba", command=prueba)
boton_prueba.pack()

# Labels centrados en el frame derecho
Label(right_frame, text="Parámetros:", font=("Arial", 14, "bold")).pack(pady=10)

Label(right_frame, text=f"expectativa_inicial_uniforme: {expectativa_inicial_uniforme}").pack(pady=5)
Label(right_frame, text=f"difusion_rate: {diffusion_rate}").pack(pady=5)
Label(right_frame, text=f"tamaño de la cuadrícula: {rows}x{cols}").pack(pady=5)
Label(right_frame, text=f"Probabilidad HC: {probabilidad_max_hc}").pack(pady=5)
Label(right_frame, text=f"Tolerancia HC: {tolerancia_hc}").pack(pady=5)

root.mainloop()