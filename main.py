# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math, sys
import numpy as np
import pygame
from pygame.locals import *

# Initialize the pygame engine
pygame.init()
vec = pygame.math.Vector2  # 2 for two-dimensional

# Parameters for the app window
HEIGHT = 480
WIDTH = 640
FPS = 60

# Physics parameters
world_offset_x = 0
world_offset_y = 0
virtualWidth = WIDTH
virtualHeight = HEIGHT
GRAVITY = 98
ground_thickness = HEIGHT * 1 / 8
ground_height = virtualHeight - ground_thickness     # level of the top of the ground above the bottom of the game window

# Not sure what this thingamabob does, but it sounds important
FramePerSec = pygame.time.Clock()

# Set the app window size and give it a fancy-shmancy title
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Duck Thrower")
virtualScreen = pygame.Surface((virtualWidth, virtualHeight))

# Player class
# A Sprite that handles the responsibilities of the player entity on the screen
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Surfaces act like hitboxes, a non-graphics area that represents the space taken up by the sprite
        self.surf = pygame.Surface((50, 50))

        # Load the sprite image file
        self.image = pygame.transform.scale(pygame.image.load('assets/duck.png'), (50, 50))
        self.rect = self.surf.get_rect()
        self.reset()

    def launch(self, initialVelocity):
        self.vel = initialVelocity
        self.acc = vec(0, GRAVITY)

        self.flying = True

    def move(self, fps):

        # Check if the duck was moving up prior to this tick
        movingUp = self.vel[1] < 0

        # Increment the position and velocity of the Player according to the game tick
        P1.pos += P1.vel / fps
        P1.vel += P1.acc / fps

        # Check if the duck is no longer moving up after this tick
        movingDown = self.vel[1] >= 0

        currentPosition = vec(self.pos)

        # When the duck is flying, track its trajectory
        if self.flying:

            # When the duck was moving up and is no longer moving up, we know this point must be the peak of the duck's trajectory
            if movingUp and movingDown:
                self.path.append(currentPosition)         # Record the peak point of the trajectory
                self.peakPoint = currentPosition
            # Record the duck's position every other frame
            elif self.tickCount % 6 == 0:
                self.path.append(currentPosition)

            self.tickCount += 1


    def reset(self):
        # Set the coordinates of the Player on the app screen
        self.pos = vec(self.surf.get_width() / 2, ground_height - self.surf.get_height() * 0.25)

        # Set the movement of the Player
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.rect.update(self.surf.get_rect(center=self.pos))

        self.tickCount = 0
        self.path = []

        self.peakPoint = vec(self.pos)
        self.landingPoint = vec(self.pos)

        self.flying = False

    def stop(self, end):

        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.flying = False

        self.landingPoint = vec(self.pos)

class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.height = ground_height
        self.surf = pygame.Surface((virtualWidth, self.height))
        self.surf.fill((0,150,0))
        self.pos = vec(virtualWidth, virtualWidth - 10)
        self.rect = self.surf.get_rect(center = self.pos)

PT1 = platform()
P1 = Player()

slingshot = pygame.sprite.Sprite()
slingshot.surf = pygame.Surface((100, 100))
slingshot.image = pygame.transform.scale(pygame.image.load('assets/slingshot.png'), (100,100))
slingshot.pos = (WIDTH * 0.15, HEIGHT * 0.8)
slingshot.rect = slingshot.surf.get_rect(center = slingshot.pos)

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
        self.placeholder = 'test'

inputBox1 = InputBox((20, 20), (140, 30))
inputBox1.placeholder = 'speed'
inputBox2 = InputBox((20, 70), (140, 30))
inputBox2.placeholder = 'angle'

inputBoxes = [inputBox1, inputBox2]
activeBoxIdx = 0
end = False

base_font = pygame.font.Font(None, 32)

# Convert a polar vector to its equivalent Cartesian vector
# Polar vector is (magnitude, angle) where angle is in degrees
def polarToCartesian(polarVect):
    magnitude = polarVect[0]
    angle = polarVect[1]
    x = magnitude * math.cos(angle * math.pi / 180)
    y = -magnitude * math.sin(angle * math.pi / 180)

    return vec(x, y)

# Convert a Cartesian vector to its equivalent polar vector
# Cartesian vector is (x, y)
def cartesianToPolar(cartesianVect):
    x = cartesianVect[0]
    y = cartesianVect[1]
    magnitude = math.sqrt(x * x + y * y)
    angle = math.atan2(y, x)

    return vec(magnitude, angle)

def distance(positionVector1, positionVector2):
    distanceVector = positionVector2 - positionVector1
    distance = cartesianToPolar(distanceVector)[0]

    return distance

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

        # Check if the event is a keyboard input and there is an active input box
        if event.type == pygame.KEYDOWN and activeBoxIdx >= 0:

            activeBox = inputBoxes[activeBoxIdx]

            # Check for backspace
            if event.key == pygame.K_BACKSPACE:

                # get text input from 0 to -1 i.e. end.
                activeBox.text = activeBox.text[:-1]

            elif event.key == pygame.K_TAB:
                activeBoxIdx += 1
                if activeBoxIdx >= len(inputBoxes):
                    activeBoxIdx = 0

                continue

            elif event.key == pygame.K_RETURN:
                if end:
                    P1.reset()
                    end = False
                    continue

                try:
                    if P1.vel == (0, 0):
                        magnitude = float(inputBoxes[0].text)
                        angle = float(inputBoxes[1].text)

                        initialVelocity = polarToCartesian((magnitude, angle))
                        P1.launch(initialVelocity)

                        P1.vel = initialVelocity
                        virtualWidth = WIDTH
                        virtualHeight = HEIGHT

                except:
                    activeBoxIdx += 1
                    if activeBoxIdx >= len(inputBoxes):
                        activeBoxIdx = 0

            # Unicode standard is used for string
            # formation
            else:
                character = event.unicode
                if character.isnumeric() or character == '.':
                    activeBox.text += event.unicode

    if not end:
        if P1.pos[0] > virtualWidth / 2:
            world_offset_x = P1.pos[0] - virtualWidth / 2
        else:
            world_offset_x = 0

        if P1.pos[1] < ground_height - ground_thickness:
            world_offset_y = P1.pos[1] - ground_height + ground_thickness
        else:
            world_offset_y = 0

    # Draw the virtual screen
    virtualScreen = pygame.Surface((virtualWidth, virtualHeight))

    virtualScreen.fill(pygame.Color('lightskyblue2'))

    # Draw all entities on the virtual screen
    PT1.surf = pygame.Surface((virtualWidth + 2 * world_offset_x, ground_thickness))
    PT1.pos = (virtualWidth / 2, HEIGHT - ground_thickness / 2)
    PT1.surf.fill((0, 150, 0))

    slingshotLeftArm = vec(slingshot.rect.center) - vec(slingshot.rect.width * 1 / 3, slingshot.rect.height * 1 / 3)
    slingshotRightArm = vec(slingshot.rect.center) - vec(0, slingshot.rect.height * 1 / 3)

    # Draw lines to represent the sling of the slingshot
    if (P1.pos[0] < slingshotRightArm[0] and P1.pos[1] > slingshotRightArm[1]):
        pygame.draw.line(virtualScreen, 'salmon4', P1.pos - vec(world_offset_x, world_offset_y), slingshotRightArm, width=5)
        pygame.draw.line(virtualScreen, 'salmon4', P1.pos - vec(world_offset_x, world_offset_y), slingshotLeftArm, width=5)

    # Draw all sprites onto the screen
    for entity in all_sprites:
        entity.rect.update(entity.surf.get_rect(center = entity.pos - vec(world_offset_x, world_offset_y)))

        # If the sprite has an image texture, draw the image
        if hasattr(entity, 'image'):
            virtualScreen.blit(entity.image, entity.rect)
        # Otherwise draw the sprite's surface
        else:
            virtualScreen.blit(entity.surf, entity.rect)



    # If the player hits the ground, stop the simulation
    if (P1.pos[1] > ground_height - P1.surf.get_height() * 0.25):
        P1.stop(end)
        end = True

        rightmostPoint = P1.landingPoint
        topmostPoint = P1.peakPoint

        widthScale = (rightmostPoint[0] + P1.surf.get_width()) / WIDTH
        heightScale = topmostPoint[1] / HEIGHT

        scale = max(widthScale, heightScale)
        if scale < 1:
            scale = 1

    if end:
        world_offset_x = 0
        world_offset_y = 0

        if virtualWidth < WIDTH * scale:
            virtualWidth += virtualWidth / 100 + (WIDTH * scale - virtualWidth) / 20

        if virtualHeight < HEIGHT * scale:
            virtualHeight += virtualHeight / 100 + (HEIGHT * scale - virtualHeight) / 20

        # Print a dashed line tracing the duck's flight path
        for i in range(int(len(P1.path) / 2 - 0.5)):
            pygame.draw.line(virtualScreen, 'black', P1.path[i * 2] + vec(0, virtualHeight - HEIGHT), P1.path[i * 2 + 1] + vec(0, virtualHeight - HEIGHT), int(3 * scale))
        pygame.draw.circle(virtualScreen, 'blue', P1.path[0] + vec(0, virtualHeight - HEIGHT), 6 * scale)
        pygame.draw.circle(virtualScreen, 'green', P1.peakPoint + vec(0, virtualHeight - HEIGHT), 6 * scale)
        pygame.draw.circle(virtualScreen, 'red', P1.landingPoint + vec(0, virtualHeight - HEIGHT), 6 * scale)

        virtualScreen = pygame.transform.scale(virtualScreen, (WIDTH, HEIGHT))

    screen.blit(virtualScreen, (0, 0))

    for i in range(len(inputBoxes)):
        inputBox = inputBoxes[i]
        if i == activeBoxIdx:
            inputBox.color = color_active
        else:
            inputBox.color = color_passive

        pygame.draw.rect(screen, inputBox.color, inputBox.rect)
        text_surface = base_font.render(inputBox.placeholder, True, (200, 200, 200))
        if len(inputBox.text) > 0:
            text_surface = base_font.render(inputBox.text, True, (0, 0, 0))



        world_offset_y = -(virtualHeight - HEIGHT)
        world_offset_x = 0

        # render at position stated in arguments
        screen.blit(text_surface, (inputBox.rect.x + 5, inputBox.rect.y + 5))

        # set width of textfield so that text cannot get

        # outside of user's text input
        inputBox.rect.w = max(100, text_surface.get_width() + 10)

    pygame.display.update()


    # Move the player
    P1.move(FPS)

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

def f(t, x0, v0, a):
    return x0 + v0 * t + 1/2 * a * t * t

# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
    #go()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
