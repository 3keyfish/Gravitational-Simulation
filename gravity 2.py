import pygame
import time
import math

#gravConst = 6.673 * 10 ** -1
gravConst = 100

pygame.init()
screenWidth = 1000  # 1m = 100 pixels
screenHeight = 1000
window = pygame.display.set_mode((screenWidth, screenHeight))
trailSurface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)
pygame.display.set_caption("Simulation")

red = [242, 53, 19]
blue = [52, 82, 235]
orange = [232, 144, 28]
pink = [223, 107, 227]


class Ball:
    def __init__(self, pos: list, vel: list, acc: list, radius: int, colour: tuple, locked: bool):
        self.pos = pos
        self.vel = vel  # m/s
        self.acc = acc
        self.radius = radius
        self.mass = math.pi * (self.radius**2) *10  # area = mass x 10
        self.colour = colour
        self.prevPos = [0, 0]
        self.locked = locked


    def update(self, dt):
        # to be called every frame

        self.prevPos[0] = self.pos[0]
        self.prevPos[1] = self.pos[1]

        if not self.locked:
            # s = ut + 0.5at^2 (suvat)
            self.pos[0] += self.vel[0] * dt + 0.5 * self.acc[0] * dt**2
            self.pos[1] += self.vel[1] * dt + 0.5 * self.acc[1] * dt**2


            self.vel[0] += self.acc[0] * dt
            self.vel[1] += self.acc[1] * dt

        self.acc = [0, 0]

        

        # collision logic - walls
        if self.pos[0] + self.radius >= screenWidth:
            self.pos[0] = screenWidth - self.radius
            self.vel[0] = abs(self.vel[0])*-1
        elif self.pos[0] - self.radius <= 0:
            self.pos[0] = self.radius
            self.vel[0] = abs(self.vel[0])
            
        if self.pos[1] + self.radius >= screenHeight:
            self.pos[1] = screenHeight - self.radius
            self.vel[1] = abs(self.vel[1])*-1
        elif self.pos[1] - self.radius <= 0:
            self.pos[1] = self.radius
            self.vel[1] = abs(self.vel[1])



          

        pygame.draw.circle(window, self.colour, (int(self.pos[0]), int(self.pos[1])), self.radius, 0)
        pygame.draw.line(trailSurface, self.colour, self.prevPos, self.pos)


##        # colour changing
##        self.colour[2] += 0.1
##        if self.colour[2] > 255:
##            self.colour[2] = 0


    def revert(self, dt):
        #if self.prevPos != None:
            #self.pos = self.prevPos
        self.pos[0] += (self.prevPos[0] - self.pos[0]) * dt * 1000
        self.pos[1] += (self.prevPos[1] - self.pos[1]) * dt * 1000


balls = []
balls.append(Ball([500, 500], [10, 0], [0, 0], 70, red, False))
balls.append(Ball([400, 200], [150, -60], [0, 0], 30, blue, False))
balls.append(Ball([500, 250], [300, 0], [0, 0], 5, orange, False))
balls.append(Ball([800, 800], [5, 0], [0, 0], 50, pink, False))


pairs = []
for b1 in range(len(balls)):
    for b2 in range(b1+1, len(balls)):
        pairs.append([balls[b1], balls[b2]])


clock = pygame.time.Clock()
fps = 0
#dtArray = []

mainLoop = True
while mainLoop:
    dt = clock.tick_busy_loop(fps) * 0.001
    #dt = 0.001
    #print(dt)
    #dtArray.append(dt)
    for event in pygame.event.get():        
        if event.type == pygame.QUIT:
            mainLoop = False
            #print(dtArray)
    window.fill((200,200,200))

    
    for j in pairs:
        distx = j[1].pos[0] - j[0].pos[0]  # AB = B - A
        disty = j[1].pos[1] - j[0].pos[1]
        dist = math.sqrt(distx**2 + disty**2)
        radii = j[0].radius + j[1].radius

        
        if dist > radii:
            force = gravConst * ((j[0].mass * j[1].mass) / (dist ** 2))  # magnitude of force
            if distx != 0:
                forcex = force * (distx / dist)
                j[0].acc[0] += forcex / j[0].mass
                j[1].acc[0] += (forcex * -1) / j[1].mass
            if disty != 0:
                forcey = force * (disty / dist)
                j[0].acc[1] += forcey / j[0].mass
                j[1].acc[1] += (forcey * -1) / j[1].mass
        


        ############
        # code below is adapted from https://gist.github.com/no4touchy/4150621
        else:       
            #print("Collision")
            theta = math.asin(disty / dist)
            M = 1 / (j[0].mass + j[1].mass)
            e = 1 #0 = Innelastic, 1 = Elastic
            #print(theta / math.pi  * 180)
            vp = [[j[0].vel[0] * math.cos(theta) + j[0].vel[1] * math.sin(theta),
                   j[1].vel[0] * math.cos(theta) + j[1].vel[1] * math.sin(theta)],
                  [0, 0]]
            vn = [j[0].vel[0] * -math.sin(theta) + j[0].vel[1] * math.cos(theta),
                  j[1].vel[0] * -math.sin(theta) + j[1].vel[1] * math.cos(theta)]
            
            vp[1][0] = M * (vp[0][0] * (j[0].mass - e * j[1].mass) + vp[0][1] * (1 + e) * j[1].mass)
            vp[1][1] = M * (vp[0][0] * (1 + e) * j[0].mass + vp[0][1] * (j[1].mass - e * j[0].mass))
            
            j[0].vel = [vp[1][0] * math.cos(theta) - vn[0] * math.sin(theta),
                           vp[1][0] * math.sin(theta) + vn[0] * math.cos(theta)]
            j[1].vel = [vp[1][1] * math.cos(theta) - vn[1] * math.sin(theta),
                           vp[1][1] * math.sin(theta) + vn[1] * math.cos(theta)]




            distVector = [distx, disty]
            while dist <= radii:
##                j[0].revert(dt)
##                j[1].revert(dt)

                j[0].pos[0] -= distVector[0] / (dist * j[0].mass)
                j[0].pos[1] -= distVector[1] / (dist * j[0].mass)
                j[1].pos[0] += distVector[0] / (dist * j[1].mass)
                j[1].pos[1] += distVector[1] / (dist * j[1].mass)
                
                distx = j[1].pos[0] - j[0].pos[0]
                disty = j[1].pos[1] - j[0].pos[1]
                dist = math.sqrt(distx**2 + disty**2)

                
            #print("while finished")

        ############





      
##    print(balls[0].acc)
##    print(balls[0].vel)
##    print(balls[0].pos)
##    print()

    
    for i in balls:
        i.update(dt)
    #balls[1].update(dt)

        
    window.blit(trailSurface, (0, 0))    
    pygame.display.update()
    

    




pygame.quit()



