from tkinter import *
from tkinter import ttk
import numpy as np
import random
import math
import matplotlib.pyplot as plt

#---------------------------------------------------------------------

# Parámetros
rows, cols = 20, 20
diffusion_rate = 0.1
cell_size = 20  # Tamaño de cada celda en píxeles

# Inicialización de la cuadrícula
expectativa_inicial_uniforme = 0.1
grid = np.full((rows, cols), expectativa_inicial_uniforme)
#grid[rows // 2, cols // 2] = 0.1  # Comida en el centro

# Lista para rastrear las celdas pintadas manualmente
comida_celdas = [[5,8], [12,7]] #posiciones de comidas

probabilidad_max_hc = 1
tolerancia_hc = 0

keep_espectativa_1 = []
target = [[5,10], [0,0], [12,7], [0,0]]

#---------------------------------------------------------------------

class Animal(): #posicion inicial por defecto 0,0
    def __init__(self, inicial = (0,0)):
        self.posx = inicial[0]
        self.posy = inicial[1]
        self.opciones = ["derecha", "izquierda", "arriba", "abajo"]
        self.estoy_presente = True

        self.tipo = "hill_climbing"
        self.tipos_list = ["random", "hill_climbing", "dead_reckoning"]
        self.target_position = []
         # Atributos para el movimiento en espiral
        self.spiral_steps = 1
        self.spiral_direction = 0
        self.spiral_count = 0
        self.spiral_dx = [1, 0, -1, 0]  # derecha, abajo, izquierda, arriba
        self.spiral_dy = [0, 1, 0, -1]
        self.spiral_x = self.posx
        self.spiral_y = self.posy

    
    def mover_random(self): #calcula el movimiento de forma aleatoria
        step = random.choice(self.opciones)
        
        # Move the object according to the direction
        if step == "derecha" and self.posx<cols-1:
            self.posx += 1
        elif step == "izquierda" and self.posx>0:
            self.posx -= 1
        elif step == "abajo" and self.posy<cols-1:
            self.posy += 1
        elif step == "arriba" and self.posy>0:
            self.posy -= 1
        
        #print(self.posx," ", self.posy," ", step)
        
        return [self.posx, self.posy, step]

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
            valores["derecha"] = grid[self.posx + 1, self.posy]  # derecha

        if self.posx > 0:
            valores["izquierda"] = grid[self.posx - 1, self.posy]  # izquierda

        if self.posy < cols - 1:
            valores["abajo"] = grid[self.posx, self.posy + 1]  # abajo

            if self.posx < cols - 1:
                valores["abajo-derecha"] = grid[self.posx + 1, self.posy + 1]  # abajo-derecha

            if self.posx > 0:
                valores["abajo-izquierda"] = grid[self.posx - 1, self.posy + 1]  # abajo-izquierda

        if self.posy > 0:
            valores["arriba"] = grid[self.posx, self.posy - 1]  # arriba

            if self.posx < cols - 1:
                valores["arriba-derecha"] = grid[self.posx + 1, self.posy - 1]  # arriba-derecha

            if self.posx > 0:
                valores["arriba-izquierda"] = grid[self.posx - 1, self.posy - 1]  # arriba-izquierda

        # Encuentra el valor máximo de las posibles direcciones
        valor_mayor = max(valores.values())
        #print("Valores completos:", valores)
        #print("Valor mayor:", valor_mayor)

        # Filtra las direcciones dentro del rango de tolerancia
        opciones_cercanas = [
            key for key, valor in valores.items()
            if valor_mayor - tolerancia <= valor <= valor_mayor + tolerancia
        ]
        #print("Opciones cercanas al máximo:", opciones_cercanas)

        # Decide si elegir la opción máxima o explorar
        if random.random() < probabilidad_max:
            # Elige entre las mejores opciones (dentro del rango)
            key_mayor = random.choice(opciones_cercanas)
            #print("Decisión: Tomar una opción cercana al máximo.")
        else:
            # Elige entre todas las opciones válidas aleatoriamente
            opciones_validas = [key for key, valor in valores.items() if valor != -1]
            key_mayor = random.choice(opciones_validas)
            #print("Decisión: Explorar otra opción válida.")
        
        #print("Dirección elegida:", key_mayor)

        # Mueve en la dirección seleccionada
        self.mover_a(key_mayor)

    def mover_dead_reckoning(self):
        """
        Movimiento basado en dead reckoning hacia la posición objetivo.
        """
        #print("dr")
        if self.target_position is None:
            return  # No hay posición objetivo para moverse

        dx = self.target_position[0][0] - self.posx
        dy = self.target_position[0][1] - self.posy

        if dx != 0:
            step_x = int(dx / abs(dx))  # -1 o 1
        else:
            step_x = 0
        if dy != 0:
            step_y = int(dy / abs(dy))  # -1 o 1
        else:
            step_y = 0

        # Mueve diagonalmente hacia la posición objetivo
        new_x = self.posx + step_x
        new_y = self.posy + step_y

        # Asegura que las nuevas posiciones estén dentro de los límites
        if 0 <= new_x < cols:
            self.posx = new_x
        if 0 <= new_y < rows:
            self.posy = new_y

        if [new_x, new_y] == self.target_position[0]:
            self.target_position.pop(0)

    def generar_circulo(self, centro, radio):
        x0, y0 = centro
        posiciones = []

        # Generar posiciones en los bordes del cuadrado
        for x in range(x0 - radio, x0 + radio + 1):
            y = y0 - radio
            if 0 <= x < cols and 0 <= y < rows:
                posiciones.append((x, y))
            y = y0 + radio
            if 0 <= x < cols and 0 <= y < rows:
                posiciones.append((x, y))
        for y in range(y0 - radio + 1, y0 + radio):
            x = x0 - radio
            if 0 <= x < cols and 0 <= y < rows:
                posiciones.append((x, y))
            x = x0 + radio
            if 0 <= x < cols and 0 <= y < rows:
                posiciones.append((x, y))

        return posiciones

    def mover_en_espiral(self, centro):
        # Mover en la dirección actual
        self.posx += self.spiral_dx[self.spiral_direction]
        self.posy += self.spiral_dy[self.spiral_direction]
        self.spiral_count += 1

        # Verificar límites
        self.posx = max(0, min(self.posx, cols - 1))
        self.posy = max(0, min(self.posy, rows - 1))

        # Cambiar de dirección
        if self.spiral_count == self.spiral_steps:
            self.spiral_count = 0
            self.spiral_direction = (self.spiral_direction + 1) % 4
            if self.spiral_direction == 0 or self.spiral_direction == 2:
                self.spiral_steps += 1  # Incrementar pasos después de dos direcciones


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
        elif self.tipo == "dead_reckoning":
            self.mover_dead_reckoning()
        elif self.tipo == "espiral":
            self.mover_en_espiral(self.centro_busqueda)


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
        ##print(x0,"",y0,"",x1,"",y1)
        canvas.create_rectangle(x0, y0, x1, y1, fill="green", outline="")

    #ANIMAL
    # Dibujar celdas pintadas manualmente en una capa separada
    if conejo.estoy_presente:
        for j,i in conejo.actual():
            x0, y0 = j * cell_size, i * cell_size #calcula las posiciones físicas segun el tamano de la malla
            x1, y1 = x0 + cell_size, y0 + cell_size
            ##print(x0,"",y0,"",x1,"",y1)
            canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="")
    else:
        pass
        #print("No hay animel para dibujar")

# Función para ejecutar la simulación paso a paso
def run_simulation(hay_animal, movimiento, pos_inicial, iteraciones, mantener_expectativa_1):
    global grid
    global keep_espectativa_1
    comido = False
    com = []
    distances = []  # Para almacenar las distancias durante la fase 3

    #print(f"Hay_animal: {hay_animal}")
    if hay_animal:
        conejo.estoy_presente = True
        conejo.tipo = movimiento
        conejo.posx = pos_inicial[0]
        conejo.posy = pos_inicial[1]

        # Solo inicializamos variables relacionadas con 'dead_reckoning' si ese es el tipo de movimiento
        if conejo.tipo == "dead_reckoning":
            if comida_celdas:
                conejo.target_position = target
            else:
                conejo.target_position = [10, 10]  # Posición objetivo por defecto

            # Inicializar variables para el movimiento en espiral
            conejo.centro_busqueda = conejo.target_position[0]
            conejo.spiral_steps = 1
            conejo.spiral_direction = 0
            conejo.spiral_count = 0

        #print(f"posx: {conejo.posx}, - posy: {conejo.posy}")
    else:
        conejo.estoy_presente = False

    phase = 1  # Fase de la simulación
    time_steps = 0  # Contador de pasos de tiempo

    while time_steps < iteraciones:
        #print("Máximo: ", grid.max(), " - Mínimo: ", grid.min())

        if hay_animal:
            conejo.mover()  # El método mover maneja el movimiento según conejo.tipo

            if [conejo.posx, conejo.posy] in comida_celdas:
                # Encontró comida
                x, y = conejo.posx, conejo.posy
                com = [x, y]
                grid[x, y] = 1  # Establece el valor de expectativa en 1
                if conejo.tipo != "dead_reckoning":
                    comida_celdas.remove([x, y])  # Consume la comida
                    comido = True

                # Mantiene la memoria del sector donde encontró la comida
                grid[com[0], com[1]] = 1  # Establece el valor de expectativa en 1
                keep_espectativa_1.append([com[0], com[1]])


                #print(f"El animal encontró la comida en la posición: {com}")


            else:
                # No hay comida aquí
                x, y = conejo.posx, conejo.posy  # Obtiene la posición actual del animal
                grid[x, y] = 0  # Establece ese lugar en 0 de expectativa

        # Mantiene la expectativa de la comida encontrada en 1
        if keep_espectativa_1 != [] and mantener_expectativa_1:
            for x,y in keep_espectativa_1:
                grid[x, y] = 1  # Mantiene el valor de expectativa en 1

        update_canvas(grid, canvas)
        root.update()  # Actualizar la ventana
        root.after(10)  # Pausar por 100 ms para visualizar los cambios

        if phase == 2:
            time_counter += 1
            if time_counter >= diffusion_time:
                # Iniciar fase 3
                phase = 3
                hay_animal = True
                conejo.estoy_presente = True
                conejo.posx = pos_inicial[0]
                conejo.posy = pos_inicial[1]
                conejo.tipo = movimiento  # Volver al tipo de movimiento inicial

                # Solo inicializamos variables de 'dead_reckoning' si ese es el tipo de movimiento
                if conejo.tipo == "dead_reckoning":
                    if comida_celdas:
                        conejo.target_position = comida_celdas[0]
                    else:
                        conejo.target_position = [10, 10]
                    # Reiniciar variables para el movimiento en espiral
                    conejo.spiral_steps = 1
                    conejo.spiral_direction = 0
                    conejo.spiral_count = 0
                    conejo.centro_busqueda = conejo.target_position
                    distances = []  # Reiniciar la lista de distancias
                else:
                    # Si no es 'dead_reckoning', no inicializamos variables de espiral
                    pass

                continue  # Continuar con el siguiente paso

        if phase == 3 and hay_animal:
            # Calcular la distancia desde la posición esperada solo si el tipo es 'dead_reckoning' o 'espiral'
            if conejo.tipo in ['dead_reckoning', 'espiral']:
                x0, y0 = conejo.centro_busqueda
                distance = math.sqrt((conejo.posx - x0) ** 2 + (conejo.posy - y0) ** 2)
                distances.append(distance)
            else:
                # Si no, la distancia puede ser desde una posición fija o no se calcula
                pass

        time_steps += 1
        grid = diffusion_step(grid)

    # Graficar la distancia en función del tiempo durante la fase 3
    if distances:
        plt.figure()
        plt.plot(distances)
        plt.xlabel('Paso de tiempo')
        plt.ylabel('Distancia desde la posición esperada')
        plt.title('Distancia del animal desde la posición esperada durante la fase 3')
        plt.show()



##########################-------------------------
#----INTERFAZ GRAFICA------------------------------
##########################-------------------------

def prueba():
    #print(lista_movimientos.get())
    #print(animal_value.get())
    try:
        pass
        #print(list(map(int, texto_pos_inicial.get().split(','))))
    except:
        pass
    #print("Posición inicial: ", texto_pos_inicial.get())

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