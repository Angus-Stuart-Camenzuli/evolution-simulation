import pygame
import random
import numpy
import copy

# pygame setup
pygame.init()

#screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
random.seed()

WIDTH = 540
HEIGHT = 960

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Evolution Simulation")

FOOD_SIZE = 5
ORGANISM_SIZE = 10

FOOD_ENERGY = 30
FOOD_SPAWN_INTERVAL = 20

ORGANISM_SPAWN_X = WIDTH / 2
ORGANISM_SPAWN_Y = HEIGHT / 2
ORGANISM_MAX_SPEED = 50

ORGANISM_MOVE_COST = 2
ORGANISM_REPRODUCTION_COST = 150
ORGANISM_ENERGY = 100
ORGANISM_CONST_ENERGY_COST = 0.5
ORGANISM_REPRODUCTION_THRESHOLD = 50 # So organism does not die after reproducing

VISION_RADIUS = 100
SIMULATION_SPEED = 5

INITIAL_NUMBER_OF_ORGANSIMS = 10

TURN_SPEED = 1.5  
FORWARD_SPEED = 50  

INITIAL_AMOUNT_OF_FOOD = 250

# Colours
PALETTE_LIGHT = {
    "BACKGROUND": "#FFFFFF",
    "ORGANISMS": ["#FF4D4D", "#4DA6FF"],
    "FOOD": "#66FF66",
}

PALETTE_NEON = {
    "BACKGROUND": "#0B0F14",
    "ORGANISMS": ["#FF3B3B", "#00C2FF"],
    "FOOD": "#39FF14",
}

PALETTE_CYBERPUNK = {
    "BACKGROUND": "#050508",
    "ORGANISMS": ["#FF0055", "#00F0FF"],
    "FOOD": "#A6FF00",
}

PALETTE_DARK_TECH = {
    "BACKGROUND": "#020617",
    "ORGANISMS": ["#FF3366", "#33CCFF"],
    "FOOD": "#CCFF33",
}

palette = PALETTE_DARK_TECH

BACKGROUND_COLOUR = palette["BACKGROUND"]
ORGANISM_COLOURS = palette["ORGANISMS"]
FOOD_COLOUR = palette["FOOD"]

ORGANISM_TYPES = ["Predator", "Vegetarian"]

class Neural_Network:
    def __init__(self, num_inputs, num_hidden_layers, num_neurons, num_outputs, weights = None, biases = None, first_gen = True):
        self.num_inputs = num_inputs
        self.num_hidden_layers = num_hidden_layers
        self.num_neurons = num_neurons
        self.num_outputs = num_outputs
        self.weights = weights if weights is not None else []
        self.biases = biases if biases is not None else []
        if first_gen:
            # Layer 0: input → hidden1
            layer = []
            for _ in range(num_inputs):
                row = [random.uniform(-1,1) for _ in range(num_neurons)]
                layer.append(row)
            self.weights.append(layer)
            self.biases.append([random.uniform(-1,1) for _ in range(num_neurons)])

            # Hidden layers
            for _ in range(num_hidden_layers-1):
                layer = []
                for _ in range(num_neurons):
                    row = [random.uniform(-1,1) for _ in range(num_neurons)]
                    layer.append(row)
                self.weights.append(layer)
                self.biases.append([random.uniform(-1,1) for _ in range(num_neurons)])

            # Output layer
            layer = []
            for _ in range(num_neurons):
                row = [random.uniform(-1,1) for _ in range(num_outputs)]
                layer.append(row)
            self.weights.append(layer)
            self.biases.append([random.uniform(-1,1) for _ in range(num_outputs)])

    def print_network(self):
        for idx, layer in enumerate(self.weights):
            print(f"Layer {idx} weights:")
            for row in layer:
                print(" ", row)
            print(f"Layer {idx} biases:")
            print(" ", self.biases[idx])
            print()  # empty line between layers

    # Inputs is a list
    def forward(self, inputs):
        neurons_layer_0 = []
        for j in range(self.num_neurons):
            numbers = []
            for i in range(len(self.weights[0])):
                z = self.weights[0][i][j] * inputs[i]
                numbers.append(z)
            x = numpy.tanh(sum(numbers) + self.biases[0][j])
            neurons_layer_0.append(x)
        
        neurons_layer_1 = []
        for j in range(self.num_neurons):
            numbers = []
            for i in range(len(self.weights[1])):
                z = self.weights[1][i][j] * neurons_layer_0[i]
                numbers.append(z)
            x = numpy.tanh(sum(numbers) + self.biases[1][j])
            neurons_layer_1.append(x)


        neurons_layer_2 = []
        for j in range(self.num_outputs):
            numbers = []
            for i in range(len(self.weights[2])):
                z = self.weights[2][i][j] * neurons_layer_1[i]
                numbers.append(z)
            x = numpy.tanh(sum(numbers) + self.biases[2][j])
            neurons_layer_2.append(x)

        
        return neurons_layer_2
    
    def mutation(self):
        new_weights = copy.deepcopy(self.weights)
        new_biases = copy.deepcopy(self.biases)

        chance_of_mutation_weights = 10
        chance_of_mutation_biases = 10
        number_of_mutations = 5

        if (random.randint(0, 100) <= chance_of_mutation_weights): 
            number_of_mutations = random.randint(0,number_of_mutations)
            for _ in range(number_of_mutations):
                for l in range(len(self.weights)):
                    for i in range(len(self.weights[l])):
                        for j in range(len(self.weights[l][i])):
                            if (random.randint(0, 100) <= chance_of_mutation_weights):
                                new_weights[l][i][j] = random.uniform(-1,1)

        if (random.randint(0, 100) <= chance_of_mutation_biases): 
            number_of_mutations = random.randint(0,number_of_mutations)
            for _ in range(number_of_mutations):
                for l in range(len(self.biases)):
                    for i in range(len(self.biases[l])):
                        if (random.randint(0, 100) <= chance_of_mutation_biases):
                            new_biases[l][i] = random.uniform(-1,1)
        
        return new_weights, new_biases
                            
class Food:
    def __init__(self, x, y, added_energy):
        self.x = x
        self.y = y
        self.added_energy = added_energy

    def delete(self):
        pygame.draw.rect(screen, BACKGROUND_COLOUR, (self.x, self.y, FOOD_SIZE, FOOD_SIZE))

    def draw(self):
        pygame.draw.rect(screen, FOOD_COLOUR, (self.x, self.y, FOOD_SIZE, FOOD_SIZE))

class Organism:
    def __init__(self, x, y, current_energy = 100, movement_cost = 1, reproduction_cost = 200, dead = False, const_energy_cost = 1, first_gen = True, weights = None, biases = None, colour="red",organism_type=""):
        self.current_energy = current_energy
        self.movement_cost = movement_cost
        self.reproduction_cost = reproduction_cost
        self.x = x
        self.y = y
        self.dead = dead
        self.prevx = x
        self.prevy = y
        self.closest_food = None
        self.closest_distance = None
        self.const_energy_cost = const_energy_cost
        self.first_gen = first_gen
        self.brain = Neural_Network(4, 2, 5, 2, first_gen=self.first_gen, weights=weights, biases=biases)
        self.id = random.randint(0,100000)
        self.angle = random.uniform(0, 2 * numpy.pi)
        self.colour = colour
        self.organism_type =organism_type
        #print(self.id)

    def update(self, dt, food_list):
        if self.dead:
            return

        # find closest food
        if food_list:
            closest_food = min(food_list, key=lambda f: calc_distance(self, f))
            distance = calc_distance(self, closest_food)
            self.closest_food = closest_food
            self.closest_distance = distance
        else:
            self.closest_food = None
            self.closest_distance = None

        # neural network input
        if self.closest_food:
            dx = self.closest_food.x - self.x
            dy = self.closest_food.y - self.y
            distance = self.closest_distance
            inputs = [dx / VISION_RADIUS, dy / VISION_RADIUS, distance / VISION_RADIUS, self.current_energy / ORGANISM_ENERGY]
        else:
            inputs = [-1, -1, 1, self.current_energy / ORGANISM_ENERGY]

        # forward pass
        movement_outputs = self.brain.forward(inputs)
        turn = movement_outputs[0]
        forward = movement_outputs[1]

        self.movement_controller(turn, forward, dt)
        self.current_energy -= self.const_energy_cost * dt

        # keep inside screen
        self.x = max(0, min(self.x, WIDTH - ORGANISM_SIZE))
        self.y = max(0, min(self.y, HEIGHT - ORGANISM_SIZE))

        if self.x != self.prevx or self.y != self.prevy:
            self.current_energy -= self.movement_cost * dt

        if self.current_energy <= 0:
            self.die()

        self.prevx = self.x
        self.prevy = self.y

    def die(self):
        self.dead = True

    def draw(self):
        pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), ORGANISM_SIZE)

    def vision(self, food, distance):
        if (distance < VISION_RADIUS):
            self.food_info.append([distance, food])
    
    def eat(self, food, distance, obj_list):
        if (distance < ORGANISM_SIZE):
            self.current_energy += food.added_energy
            food.delete()
            if food in obj_list:
                obj_list.remove(food)
    
    def eat_prey(self, prey, distance):
        if (distance < ORGANISM_SIZE):
            self.current_energy += prey.current_energy # I will replace magic number later but its the energy given when consuming live organism
            prey.dead = True

    def movement_controller(self, turn, forward, dt):
        # turn organism
        self.angle += turn * TURN_SPEED * dt

        # move forward in direction it's facing
        self.x += numpy.cos(self.angle) * forward * FORWARD_SPEED * dt
        self.y += numpy.sin(self.angle) * forward * FORWARD_SPEED * dt

    def reproduction(self):
        weight, bias = self.brain.mutation()
        return weight, bias

def calc_distance(obj_one, obj_two):
    distance = (((obj_one.x - obj_two.x) ** 2) + ((obj_one.y - obj_two.y) ** 2)) ** 0.5
    return distance

def spawn_tribes(colours, types):
    organisms = []

    num_tribes = len(types)
    num_per_tribe = INITIAL_NUMBER_OF_ORGANSIMS // num_tribes

    for colour, org_type in zip(colours, types):
        for _ in range(num_per_tribe):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)

            org = Organism(
                x=x,
                y=y,
                current_energy=ORGANISM_ENERGY,
                movement_cost=ORGANISM_MOVE_COST,
                reproduction_cost=ORGANISM_REPRODUCTION_COST,
                const_energy_cost=ORGANISM_CONST_ENERGY_COST,
                colour=colour,
                organism_type=org_type
            )

            organisms.append(org)

    return organisms

def main():
    food_on_screen = []

    food_spawn_timer = 0

    organisms = spawn_tribes(colours=ORGANISM_COLOURS, types=ORGANISM_TYPES)

    for _ in range(INITIAL_AMOUNT_OF_FOOD):
        food_instance = Food(random.randint(0, WIDTH - FOOD_SIZE), random.randint(0, HEIGHT - FOOD_SIZE), FOOD_ENERGY)
        food_on_screen.append(food_instance)

    running = True
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        # fill the screen with a color to wipe away anything from last frame
        screen.fill(BACKGROUND_COLOUR)

        # RENDER YOUR GAME HERE

        organisms = [org for org in organisms if not org.dead]

        dt = (clock.get_time() / 1000) * SIMULATION_SPEED

        vegetarians = [org for org in organisms if org.organism_type == "Vegetarian" and not org.dead]

        for org in organisms:
            org.draw()
            if org.organism_type == "Vegetarian":
                org.update(dt, food_on_screen)
            elif org.organism_type == "Predator":
                org.update(dt, vegetarians) 
                if org.closest_food:
                    org.eat_prey(org.closest_food, org.closest_distance)
            if org.current_energy >= ORGANISM_REPRODUCTION_COST + ORGANISM_REPRODUCTION_THRESHOLD:
                weights, biases = org.reproduction()
                offspring = Organism(
                    org.x,
                    org.y,
                    current_energy=ORGANISM_ENERGY,
                    movement_cost=ORGANISM_MOVE_COST,
                    reproduction_cost=ORGANISM_REPRODUCTION_COST,
                    const_energy_cost=ORGANISM_CONST_ENERGY_COST,
                    first_gen=False,
                    weights= weights,
                    biases= biases,
                    colour=org.colour,
                    organism_type=org.organism_type
                )
                org.current_energy -= ORGANISM_REPRODUCTION_COST
                organisms.append(offspring)

        if (food_spawn_timer % FOOD_SPAWN_INTERVAL) == 0:  
            food_instance = Food(random.randint(0, WIDTH - FOOD_SIZE), random.randint(0, HEIGHT - FOOD_SIZE), FOOD_ENERGY)
            food_on_screen.append(food_instance)
        
        for food_item in food_on_screen[:]:
            food_item.draw()
            for org in organisms:
                if org.closest_food == food_item and org.organism_type == "Vegetarian":
                    distance = org.closest_distance
                    org.eat(food_item, distance, food_on_screen)
                
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
        food_spawn_timer += 1

if __name__ == "__main__":
    main()

pygame.quit()