import pygame, sys, os
from pygame.locals import *
from math import sqrt, pi, sin, cos
from random import random

#params
win_width = 1000.0
win_height = 500.0
border = 0.1 
border_width = border*win_width
border_height = border*win_height
updatesPerFrame = 20

#globals
restartSimulation = True

########### Simulation ##############

class Vector():
  def __init__(self, x=0.0, y=0.0):
    self.x = x
    self.y = y

  def getTuple(self):
    return self.x, self.y

  def distanceTo(self, v):
    return sqrt((self.x - v.x)**2 + (self.y - v.y)**2)

  def magnitude(self):
    return sqrt(self.x**2 + self.y**2)

  def getNormal(self):
    return Vector(self.x/self.magnitude(), self.y/self.magnitude())

  def __add__(self, addend):
    return Vector(self.x + addend.x, self.y + addend.y)

  def __str__(self):
    return "x: " + str(self.x) + ", y: " + str(self.y)


class PoolTable():
  def __init__(self, ball):
    self.width = 900.0
    self.length = 1800.0
    self.ballDiameter = ball.diameter
    self.pocketWidth = self.ballDiameter*1.6

class Ball():
  def __init__(self, position=Vector(900.0,450.0), velocity=Vector(-0.97,-0.5)):
    self.diameter = 51.0
    self.position = position
    self.velocity = velocity

  def nextPosition(self):
    return self.position + self.velocity

class Simulation():
  def __init__(self):
    self.angle = 2*pi*random()
    direction = Vector(cos(self.angle), sin(self.angle))
    self.ball = Ball(velocity=direction.getNormal())
    self.table = PoolTable(self.ball)
    self.cushions = 0

  def ballInPocket(self):
    missingCushion = self.table.pocketWidth/sqrt(2)

    if Vector(0,0).distanceTo(self.ball.position) < missingCushion:
      return True
    if Vector(self.table.length,0).distanceTo(self.ball.position) < missingCushion:
      return True
    if Vector(self.table.length,self.table.width).distanceTo(self.ball.position) < missingCushion:
      return True
    if Vector(0,self.table.width).distanceTo(self.ball.position) < missingCushion:
      return True

    if Vector(self.table.length/2, 0).distanceTo(self.ball.position) < self.table.pocketWidth/2:
      return True
    if Vector(self.table.length/2, self.table.width).distanceTo(self.ball.position) < self.table.pocketWidth/2:
      return True


  def updateBall(self):
    ballRadius = self.table.ballDiameter/2
    nextx, nexty = self.ball.nextPosition().getTuple()
    if (nextx - ballRadius) < 0 or (nextx + ballRadius) > self.table.length:
      self.ball.velocity.x *= -1
      self.cushions += 1
    elif (nexty - ballRadius) < 0 or (nexty + ballRadius) > self.table.width:
      self.ball.velocity.y *= -1
      self.cushions += 1
    self.ball.position = self.ball.nextPosition()

############# Drawing Routines ###################

def y_flip(y): return win_height - y

def toint(i): return int(round(i))

def tableToWindow((x, y), scaling):
  return (toint(border_width + scaling*x), toint(y_flip(border_height + scaling*y)))

def drawCushion(screen, scaling, color, start, finish):
  pygame.draw.line(screen, color, tableToWindow(start, scaling), tableToWindow(finish, scaling))

#pocket type clockwise starting from 0 bottom left, finishing 5 bottom middle
def drawPocket(screen, scaling, color, coords, radius, pocketType):
  x, y = tableToWindow(coords, scaling)
  pygame.draw.circle(screen, color, (x, y), toint(scaling*radius))
  if pocketType in [0, 1]:
    pygame.draw.rect(screen, (0,0,0), [x - toint(scaling*radius), y - toint(scaling*radius), toint(scaling*radius), 2*toint(scaling*radius)])
  if pocketType in [0, 4, 5]:
    pygame.draw.rect(screen, (0,0,0), [x - toint(scaling*radius), y, 2*toint(scaling*radius), toint(scaling*radius)])
  if pocketType in [1, 2, 3]: 
    pygame.draw.rect(screen, (0,0,0), [x - toint(scaling*radius), y - toint(scaling*radius), 2*toint(scaling*radius), toint(scaling*radius)])
  if pocketType in [3, 4]: 
    pygame.draw.rect(screen, (0,0,0), [x, y - toint(scaling*radius), toint(scaling*radius), 2*toint(scaling*radius)])
  

def drawTable(screen, simulation, scaling, color):
  left_cushion = drawCushion(screen, scaling, color, (0, 0), (0, simulation.table.width))
  right_cushion = drawCushion(screen, scaling, color, (simulation.table.length, 0), (simulation.table.length, simulation.table.width))
  top_cushion = drawCushion(screen, scaling, color, (0, simulation.table.width), (simulation.table.length, simulation.table.width))
  bottom_cushion = drawCushion(screen, scaling, color, (0, 0), (simulation.table.length, 0))

  missingCushion = (simulation.table.pocketWidth)/(sqrt(2))
  middlePocket = simulation.table.pocketWidth/2
  drawPocket(screen, scaling, (245, 245, 220), (0,0), missingCushion, 0)
  drawPocket(screen, scaling, (245, 245, 220), (0,simulation.table.width), missingCushion, 1)
  drawPocket(screen, scaling, (245, 245, 220), (simulation.table.length/2,simulation.table.width), middlePocket, 2)
  drawPocket(screen, scaling, (245, 245, 220), (simulation.table.length,simulation.table.width), missingCushion, 3)
  drawPocket(screen, scaling, (245, 245, 220), (simulation.table.length,0), missingCushion, 4)
  drawPocket(screen, scaling, (245, 245, 220), (simulation.table.length/2,0), middlePocket, 5)
  
 
def drawBall(screen, simulation, scaling, color):
  ball = pygame.draw.circle(screen, color, 
    tableToWindow((simulation.ball.position.x, simulation.ball.position.y), scaling), 
    toint(scaling*simulation.table.ballDiameter*0.5))
  
def input(events): 
  global restartSimulation
  for event in events: 
    if event.type == QUIT: 
      sys.exit(0) 
    if event.type == KEYDOWN:
      if restartSimulation == False:
        print 'restarting'
        restartSimulation = True

def cumulativeAverage(prevAvg, newData, n):
  return (newData + (n-1)*prevAvg)/n


# Run simulation without display
def headlessSimulation():
  repetitions = 1000
  failures = 0
  maxCushions = 1000
  cumAvg = 0.0
  data_points = []
  for i in range(repetitions):
    if(i%100 == 0): print i
    s = Simulation()
    failure = False
    while not s.ballInPocket() and not failure:
      s.updateBall()
      if(s.cushions > maxCushions):
        failure = True
    if failure:
      failures += 1
    else:
      #cumAvg = cumulativeAverage(cumAvg, float(s.cushions), float(i + 1 - failures))
      data_points.append(s.cushions)
  f = open('sim.log', 'w')
  [f.write(str(i) + '\n') for i in data_points]
  f.close()
  print 'failures:', failures
  print 'successes:', repetitions - failures
  print 'average:', sum(data_points)/(repetitions - failures)
  data_points.sort()
  print 'median:', data_points[repetitions/2]
      

################# main ################

#headlessSimulation()
#sys.exit(0)

pygame.init()
window = pygame.display.set_mode((toint(win_width), toint(win_height)))
pygame.display.set_caption('Frictionless pool table')
screen = pygame.display.get_surface() 
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

simulation = Simulation()
simulationRunning = True
scaling = (win_width - 2*border_width)/simulation.table.length

while True: 
  screen.fill((0,0,0))
  if simulationRunning:
    for i in range(updatesPerFrame):
      simulation.updateBall()
      if simulation.ballInPocket():
        simulationRunning = False
  message = str(simulation.cushions) + " cushions, angle: %.2f" % simulation.angle + "rad"
  if simulationRunning == False:
    message += "              (press enter to play again)"
  text = font.render(message, 1, (0, 150, 0))
  screen.blit(text, (0, 0))
  drawTable(screen, simulation, scaling, (0,150,0))
  drawBall(screen, simulation, scaling, (150, 0,0))
  pygame.display.flip()
  input(pygame.event.get())
  clock.tick(60)

  if restartSimulation:
    'got here'
    simulationRunning = True
    restartSimulation = False
    simulation = Simulation()
