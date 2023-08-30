# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math, sys
import numpy as np
from matplotlib import pyplot as plt
import pygame
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

HEIGHT = 450
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60

FramePerSec = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((100, 100))
        #self.surf.fill((128,255,40))
        self.image = pygame.transform.scale(pygame.image.load('assets/duck.png'), (100,100))
        self.rect = self.surf.get_rect(center = (10, 420))

        self.pos = vec((10, 385))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

PT1 = platform()
P1 = Player()

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)


color_active = pygame.Color('lightskyblue3')

# color_passive store color(chartreuse4) which is
# color of input box.
color_passive = pygame.Color('white')

#pygame.Rect((x, y), (width, height))
class InputBox():

    def __init__(self, pos, size):
        self.rect = pygame.Rect(pos, size)
        self.active = False
        self.color = color_passive
        self.text = ''

inputBox1 = InputBox((200, 200), (140, 32))
inputBox2 = InputBox((200, 300), (140, 32))
inputBox3 = InputBox((200, 400), (140, 32))

inputBoxes = [inputBox1, inputBox2, inputBox3]
activeBox = None

base_font = pygame.font.Font(None, 32)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for inputBox in inputBoxes:
                if inputBox.rect.collidepoint(event.pos):
                    activeBox = inputBox
                    activeBox.color = color_active
                else:
                    activeBox.color = color_passive
                    activeBox = None

        if event.type == pygame.KEYDOWN:
            if activeBox is None:
                continue

            # Check for backspace
            if event.key == pygame.K_BACKSPACE:

                # get text input from 0 to -1 i.e. end.
                activeBox.text = activeBox.text[:-1]

            elif event.key == pygame.K_RETURN:
                # TODO: submit the entered number to the physics calculation
                activeBox.color = color_passive
                activeBox = None
                continue

            # Unicode standard is used for string
            # formation
            else:
                character = event.unicode
                if character.isnumeric() or character == '.':
                    activeBox.text += event.unicode

    screen.fill(pygame.Color('lightgray'))

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    screen.blit(P1.image, P1.rect)

    for inputBox in inputBoxes:
        pygame.draw.rect(screen, inputBox.color, inputBox.rect)
        text_surface = base_font.render(inputBox.text, True, (0, 0, 0))

    # render at position stated in arguments
        screen.blit(text_surface, (inputBox.rect.x + 5, inputBox.rect.y + 5))

    # set width of textfield so that text cannot get
    # outside of user's text input
        inputBox.rect.w = max(100, text_surface.get_width() + 10)

    # display.flip() will update only a portion of the
    # screen to updated, not full area
    pygame.display.flip()

    pygame.display.update()
    FramePerSec.tick(FPS)



def go():
    print("Initial velocity (m/s): ")
    velocity_initial = int(input())

    print("Launch angle (degrees): ")
    angle = int(input())

    print("Launch platform height: ")
    height_initial = int(input())

    velocity_initial_x = velocity_initial * math.cos(angle * math.pi / 180.0)
    velocity_initial_y = velocity_initial * math.sin(angle * math.pi / 180.0)

    print("Initial x velocity is:", velocity_initial_x)
    print("Initial y velocity is:", velocity_initial_y)

    acceleration_x = 0
    acceleration_y = -9.8
    drag_coefficient = 0.42
    cross_sectional_area = 0.0032

    mass = 0.055

    # Find the maximum altitude of the object using kinetic energy to potential energy conversion
    vertical_kinetic_energy = 1/2 * mass * velocity_initial_y * velocity_initial_y
    maximum_potential_energy = -vertical_kinetic_energy
    altitude = maximum_potential_energy / (mass * acceleration_y)

    # Use mechanics to find the flight time to the peak of the flight
    rise_time = math.sqrt(abs(2 * altitude / acceleration_y))

    # Use mechanics to find the flight time from the peak of the flight to landing
    drop = altitude + height_initial
    fall_time = math.sqrt(abs(2 * drop / acceleration_y))


    flight_time = rise_time + fall_time

    t = np.linspace(0, flight_time, 100)

    '''
    plt.plot(t, f(t, 0, velocity_initial_x, acceleration_x), color='red')
    plt.show()

    plt.plot(t, f(t, height_initial, velocity_initial_y, acceleration_y), color='green')
    plt.show()
    '''

    plt.plot(f(t, 0, velocity_initial_x, acceleration_x), f(t, height_initial, velocity_initial_y, acceleration_y), color='green')
    plt.show()

def f(t, x0, v0, a):
    return x0 + v0 * t + 1/2 * a * t * t

# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
    #go()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
