# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math, sys
import numpy as np
from matplotlib import pyplot as plt
import pygame
from pygame.locals import *

# Initialize the pygame engine
pygame.init()
vec = pygame.math.Vector2  # 2 for two dimensional

# Parameters for the app window
HEIGHT = 450
WIDTH = 400
FPS = 60

# Physics parameters
# Might not be needed, but leaving them here until further notice
ACC = 0.5
FRIC = -0.12

# Not sure what this thingamabob does, but it sounds important
FramePerSec = pygame.time.Clock()

# Set the app window size and give it a fancy shmancy title
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Duck Thrower")

# Player class
# A Sprite that handles the responsibilities of the player entity on the screen
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Surfaces act like hitboxes, a non-graphics area that represents the space taken up by the sprite
        self.surf = pygame.Surface((100, 100))

        # Load the sprite image file
        self.image = pygame.transform.scale(pygame.image.load('assets/duck.png'), (100,100))

        # Set the coordinates of the
        self.rect = self.surf.get_rect(center = (10, 420))

        # Set the coordinates of the Player on the app screen
        self.pos = vec((10, 385))

        # Set the movement of the Player
        self.vel = vec(100, -50)
        self.acc = vec(0, 0)

class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((0,150,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))

PT1 = platform()
P1 = Player()

slingshot = pygame.sprite.Sprite()
slingshot.surf = pygame.Surface((100, 100))
slingshot.image = pygame.transform.scale(pygame.image.load('assets/slingshot.png'), (100,100))
slingshot.rect = slingshot.surf.get_rect(center = (100, 420))

all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(P1)
all_sprites.add(slingshot)


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
activeBoxIdx = -1

base_font = pygame.font.Font(None, 32)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            activeBoxIdx = -1
            for i in range(len(inputBoxes)):
                if inputBoxes[i].rect.collidepoint(event.pos):
                    activeBoxIdx = i
                    break

        # Check if the event isa keyboard input and there is an active input box
        if event.type == pygame.KEYDOWN and activeBoxIdx >= 0:

            activeBox = inputBoxes[activeBoxIdx]

            # Check for backspace
            if event.key == pygame.K_BACKSPACE:

                # get text input from 0 to -1 i.e. end.
                activeBox.text = activeBox.text[:-1]

            elif event.key == pygame.K_RETURN or event.key == pygame.K_TAB:
                # TODO: submit the entered number to the physics calculation
                activeBoxIdx += 1
                if activeBoxIdx >= len(inputBoxes):
                    activeBoxIdx = 0

                continue

            # Unicode standard is used for string
            # formation
            else:
                character = event.unicode
                if character.isnumeric() or character == '.':
                    activeBox.text += event.unicode

    screen.fill(pygame.Color('lightskyblue2'))

    # Draw all sprites onto the screen
    for entity in all_sprites:
        # If the sprite has an image texture, draw the image
        if hasattr(entity, 'image'):
            screen.blit(entity.image, entity.rect)
        # Otherwise draw the sprite's surface
        else:
            screen.blit(entity.surf, entity.rect)


    for i in range(len(inputBoxes)):
        inputBox = inputBoxes[i]
        if i == activeBoxIdx:
            inputBox.color = color_active
        else:
            inputBox.color = color_passive

        pygame.draw.rect(screen, inputBox.color, inputBox.rect)
        text_surface = base_font.render(inputBox.text, True, (0, 0, 0))

        # render at position stated in arguments
        screen.blit(text_surface, (inputBox.rect.x + 5, inputBox.rect.y + 5))

        # set width of textfield so that text cannot get
        # outside of user's text input
        inputBox.rect.w = max(100, text_surface.get_width() + 10)

    pygame.display.update()

    # Increment the position and velocity of the Player according to the game tick
    P1.pos += P1.vel / FPS
    P1.vel += P1.acc / FPS
    P1.acc[0] = -P1.vel[0] / 10
    P1.acc[1] = 9.8

    P1.rect.update(P1.surf.get_rect(center = P1.pos))

    # Wait until the next tick to continue running the simulation
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
