import pygame
import sys
import os
import math
import neat 

screenWidth = 1244
screenHeight = 10166

screen = pygame.display.set_mode((screenWidth, screenHeight))

track = pygame.image.load("Assets/track.png")


class Car(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join('Assets', 'car.png'))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(490,820))
        self.vel_vector = pygame.math.Vector2(0.8, 0)
        self.angle = 0
        self.rotational_vel = 5 # rotational velocity
        self.direction = 0 # -1 left, 0 netural, 1 right
        self.alive = True
        self.radars = []
        
    def update(self):
        self.radars.clear() 
        self.drive()
        self.rotate()
        for radar_angle in (-60,-30, 0, 30, 60):
            self.radar(radar_angle)
        self.collision()
        self.data()
        
    def drive(self):
        self.rect.center += self.vel_vector * 6
    
    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotational_vel
            self.vel_vector.rotate_ip(self.rotational_vel)
        if self.direction == -1:
            self.angle += self.rotational_vel
            self.vel_vector.rotate_ip(-self.rotational_vel)
            
        
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center =self.rect.center)
    
    def collision(self):
        length = 40
        collision_point_right = [int(self.rect.center [0]+ math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center [1]-math.sin(math.radians (self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center [0]+ math.cos(math.radians(self.angle - 18)) * length),
                                 int(self.rect.center [1]-math.sin(math.radians (self.angle - 18)) * length)]
        if screen.get_at(collision_point_right) == pygame.Color(2,105, 31, 255) or screen.get_at(collision_point_left) == pygame.Color(2,105, 31, 255):
            self.alive = False
            print('Car is dead')
    def radar(self, radar_angle):
        length = 0 #length of radar
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])
        
        while not screen.get_at((x,y)) == pygame.Color(2,105,31,255) and length < 200:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle +radar_angle))*length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle))*length)

        #draw radar
        pygame.draw.line(screen, (255,255,255,255), self.rect.center, (x,y), 1)
        pygame.draw.circle(screen, (0,255,0,0), (x,y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] -x,2) + math.pow(self.rect.center[1] -y,2 )))

        self.radars.append([radar_angle,dist])

    def data(self):
        input = [0,0,0,0,0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input




def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)



currge = 1

def eval_genomes(genomes, config):
    global cars, ge, nets, currge
    
    cars  = []
    ge = []
    nets = []
    
    for genomeid, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
         
    
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit
                
        screen.blit(track, (0,0))
        if len(cars) == 0:
            currge += 1
            print(f'Current generation is {currge}')
            break
        
        
        for i, car in enumerate(cars):
            ge[i].fitness += 1
            if not car.sprite.alive:
                remove(i)
        
        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] >0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0
    

        #update
        for car in cars:
            car.draw(screen)
            car.update()
            
        pygame.display.update()


# Neat NN
# config_path = '/Users/omart/Desktop/PythonLearning/config.txt'
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    pop.run(eval_genomes, 150)
    
    
    
if __name__ == '__main__':
    localDir = os.path.dirname(__file__)
    config_path = os.path.join(localDir, 'config.txt')
    run(config_path)
    
    
    