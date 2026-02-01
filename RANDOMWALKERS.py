#I am going to create an Agent based model that monitors the random movement of walkers in a random
# walkers in a 2 D grid
# I need a model class for the environment where the agents are moving and operating
# I also need agent classes for slow agents , fast agents and the obstacles that they will find in some parts of the grid when they are randomly moving
# import the libraries that I'll need
import mesa
import matplotlib.pyplot as plt
import seaborn as sns

# Slow Walker agents class
class Slow_Walker(mesa.Agent): #classifies agents in models , moves agents, agents tasks , functionality of the agents
    def __init__(self, unique_id, model): # constractor method  for the agent class
        super().__init__( model) # inheritance
        self.distance = 0
        self.collisions = 0
    # moving the agents
    def move(self):
        possible = self.model.grid.get_neighborhood(self.pos, moore = True , include_center = False )
        new_pos = self.random.choice(possible)
        self.model.grid.move_agent(self, new_pos)
        # after moving the distance moved by the agents increases by one unit
        self.distance += 1
    def collide_with_obstacle(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1: # if there are more than one cellmate in the new cell
            other = self.random.choice(cellmates) # choose one randomly
            if other != self:
                if isinstance(other, Obstacles): # if it meets an obstacle the collisions increase by one
                    self.collisions += 1

    # step method: functionality of the agent class
    def step(self):
        self.move() # first move the agents
        self.collide_with_obstacle()

# Fast Walkers agents class
class Fast_Walker(mesa.Agent):
    def __init__(self, unique_id, model): # constructor method
        super().__init__( model)  # inheritance
        self.distance = 0
        self.collisions = 0

    # move the agents
    def move(self):
        possible = self.model.grid.get_neighborhood(self.pos, moore = True , include_center = False )
        new_pos = self.random.choice(possible)
        self.model.grid.move_agent(self, new_pos)
        self.distance += 2 # since they move faster so they cover double the distance for slow walkers

    # collisions
    def collide_with_obstacle(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            if other != self:
                if isinstance(other, Obstacles):
                    self.collisions += 1

    # step method
    def step(self):
        self.move()
        self.collide_with_obstacle()

# Obstacles agents class
class Obstacles(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__( model)
        self.distance = 0
        self.collisions = 0
    # move the agents
    def move(self):
        possible = self.model.grid.get_neighborhood(self.pos, moore = True , include_center = False )
        new_pos = self.random.choice(possible)
        self.model.grid.move_agent(self, new_pos)
        self.distance += 1
    def collide(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            if other != self:
                if isinstance(other, Slow_Walker) or isinstance(other, Fast_Walker): # check if it meets a slow walker or a fast walker
                    self.collisions += 1
    def step(self):
        if isinstance(self, Wind): # it moves when hit by the wind
            self.move()
        self.collide()

# agent class for the wind
class Wind(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__( model)
        self.power = 50
        self.distance = 0

    def move(self):
        possible = self.model.grid.get_neighborhood(self.pos, moore = True , include_center = False )
        new_pos = self.random.choice(possible)
        self.model.grid.move_agent(self, new_pos)
        self.distance += 1
    def collisions(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            if other != self:
                if isinstance(other, Obstacles):
                    self.collisions += 1
                    self.power -= 5

    def death(self):
        if self.power >= 0:
            self.remove()


    # step method
    def step(self):
        self.move()
        self.collisions()
        if self.power >= 0:
            self.death()

# model class for the environment model
class Environment(mesa.Model): # number of agents , creates grid,  places agents on the grid, creates agents
    def __init__(self, S, F, O,W, width, height): # constructor method for the model class
        super().__init__() # completes the inheritance
        self.S = S
        self.F = F
        self.O = O
        self.W = W
        # creating the grid for movement of the agents
        self.grid = mesa.space.MultiGrid(width, height, torus = True)
        for i in range(S):
            a = Slow_Walker(i,self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))
        for j in range(F):
            a = Fast_Walker(j,self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))

        for k in range(O):
            a = Obstacles(k,self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))

        for g in range(W):
            a = Wind(g,self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x,y))
    def step(self):
        self.agents.shuffle_do("step")


model = Environment(50,50,10,30,30,30)
for i in range(100):
    print(f"step {i}")
    model.step()

# distance moved by slow walkers
distances = []
for slow_walkers in model.agents:
    if isinstance(slow_walkers, Slow_Walker):
        distances.append(slow_walkers.distance)

if distances:
    plt.figure(figsize = (10,10))
    sns.histplot(distances,bins = range(max(distances)+ 2), kde = True, stat = "count", discrete= True, edgecolor = "black")
    plt.title("Distance moved by slow walkers")
    plt.xlabel("Distance moved by slow walkers")
    plt.ylabel("Frequency")
    plt.grid(True, alpha = 0.3)
    plt.show()
else:
    print("No distance found")

distance = []
for fast_walkers in model.agents:
    if isinstance(fast_walkers, Fast_Walker):
        distance.append(fast_walkers.distance)

if distance:
    plt.figure(figsize = (10,10))
    sns.histplot(distance,bins = range(max(distance)+ 2), kde = True, stat = "count", discrete= True, edgecolor = "black")
    plt.title("Distance moved by Fast Walkers")
    plt.xlabel("Distance moved by Fast walkers")
    plt.ylabel("Frequency")
    plt.grid(True, alpha = 0.3)
    plt.show()
else:
    print("No distance found")



