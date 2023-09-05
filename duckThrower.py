# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math, sys
from duck import Duck
from platform import Platform
from inputbox import InputBox
import pygame
from pygame.locals import *

# Initialize the pygame engine
pygame.init()
vec = pygame.math.Vector2  # 2 for two-dimensional

# Parameters for the app window
HEIGHT = 480
WIDTH = 640
FPS = 60

# Parameters for scaling the simulation to fit within the app window
world_offset_x = 0                                          # X offset to scroll the screen and keep the duck in frame
world_offset_y = 0                                          # Y offset to scroll the screen and keep the duck in frame
scale = 1                                                   # Scale of the virtual world within the app window
virtual_width = WIDTH * scale                               # Width of the virtual world
virtual_height = HEIGHT * scale                             # Height of the virtual world
ground_thickness = HEIGHT * 1 / 8                           # Thickness of the ground Platform
ground_height = int(virtual_height - ground_thickness)      # Level of the top of the ground above the bottom of the app window

# Physics constants
GRAVITY = vec(0, 980)

# Not sure what this thingamabob does, but it sounds important
FramePerSec = pygame.time.Clock()

# Set the app window size and give it a fancy-shmancy title
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Duck Thrower")

# Create a virtual screen that scales to contain the entire simulation world
virtual_screen = pygame.Surface((virtual_width, virtual_height))

# Define the duck as a custom sprite using the Duck class
duck = Duck(ground_height)

# Define the ground as a simple sprite
#ground = Platform(virtual_width, ground_height)

ground = pygame.sprite.Sprite()
ground.surf = pygame.Surface((virtual_width + 2 * world_offset_x, ground_thickness))
ground.surf.fill((0, 150, 0))
ground.pos = (virtual_width / 2, HEIGHT - ground_thickness / 2)
ground.rect = ground.surf.get_rect(center = ground.pos)


# Define the slingshot as a simple sprite
slingshot = pygame.sprite.Sprite()
slingshot.surf = pygame.Surface((100, 100))
slingshot.image = pygame.transform.scale(pygame.image.load('assets/slingshot.png'), (100,100))
slingshot.pos = (WIDTH * 0.15, HEIGHT * 0.8)
slingshot.rect = slingshot.surf.get_rect(center = slingshot.pos)

# Add all sprites to a sprite group for easier handling
all_sprites = pygame.sprite.Group()
all_sprites.add(ground)
all_sprites.add(duck)
all_sprites.add(slingshot)

# Instantiate two text input boxes for receiving user input values
input_box1 = InputBox((20, 20), (140, 30))
input_box1.placeholder = 'speed'
input_box2 = InputBox((20, 70), (140, 30))
input_box2.placeholder = 'angle'

base_font = pygame.font.Font(None, 32)

# Place the input boxes in a list for easier handling
input_boxes = [input_box1, input_box2]
activeBoxIdx = 0

# Flag to indicate if the simulation has ended
running = False
end = False

# Convert a polar vector to its equivalent Cartesian vector
# Polar vector is (magnitude, angle) where angle is in degrees
def polarToCartesian(polar_vect):
    """
    Converts a polar vector to a Cartesian vector.

    Args:
        polar_vect (vec2(float, float)): A 2D vector or 2-element list in the form (magnitude, angle)

    Returns:
        vec(float, float): A 2D vector in the form (x, y)
    """
    x = polar_vect[0] * math.cos(polar_vect[1] * math.pi / 180)
    # y must be negative because pygame uses inverted y-axis coordinates
    y = -polar_vect[0] * math.sin(polar_vect[1] * math.pi / 180)

    return vec(x, y)

def cartesianToPolar(cartesian_vect):
    """
    Converts a Cartesian vector to a polar vector.

    Args:
        cartesian_vect (vec2(float, float)): A 2D vector or 2-element list in the form (x, y)

    Returns:
        vec(float, float): A 2D vector in the form (magnitude, angle)
    """

    magnitude = math.sqrt(cartesian_vect[0] * cartesian_vect[0] + cartesian_vect[1] * cartesian_vect[1])
    angle = math.atan2(cartesian_vect[1], cartesian_vect[0])

    return vec(magnitude, angle)

def distance(position_vector1, position_vector2):
    """
    Finds the distance between two objects based on their position vectors.

    Args:
        position_vector1 (vec2(float, float)): The 2D cartesian position vector of the first object
        position_vector2 (vec2(float, float)): The 2D cartesian position vector of the second object

    Returns:
        float: The distance between the two position vectors
    """
    distance_vector = position_vector2 - position_vector1
    dist = cartesianToPolar(distance_vector)[0]

    return dist


def calcLaunch(initial_velocity, acceleration):
    """
    Calculates the peak and landing points of a simple ballistic trajectory given the initial launch velocity
    TODO: Finish this comment

    Args:
        position_vector1 (vec2(float, float)): The 2D cartesian position vector of the first object
        position_vector2 (vec2(float, float)): The 2D cartesian position vector of the second object

    Returns:
        float: The distance between the two position vectors
    """

    velocity_initial_x = initial_velocity[0] / 100
    velocity_initial_y = initial_velocity[1] / 100

    #print("Initial x velocity is:", velocity_initial_x)
    #print("Initial y velocity is:", velocity_initial_y)

    mass = 1 # Mass actually doesn't matter, because flight path is independent of mass

    # Find the maximum altitude of the object using kinetic energy to potential energy conversion
    vertical_kinetic_energy = 1/2 * mass * velocity_initial_y * velocity_initial_y
    maximum_potential_energy = -vertical_kinetic_energy
    altitude = maximum_potential_energy / (mass * acceleration[1])

    # Use kinematics equations to find the flight time to the peak of the flight
    rise_time = math.sqrt(abs(2 * altitude / acceleration[1]))

    # Use mechanics to find the flight time from the peak of the flight to landing
    drop = altitude
    fall_time = math.sqrt(abs(2 * drop / acceleration[1]))


    flight_time = rise_time + fall_time

    #print("Flight time: ", flight_time)

    distance = flight_time * velocity_initial_x

    #print("Flight distance: ", distance)
    #print("Peak altitude: ", altitude)

    # TODO: Return the peak and landing points relative to the launch point

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            activeBoxIdx = -1
            for i in range(len(input_boxes)):
                if input_boxes[i].rect.collidepoint(event.pos):
                    activeBoxIdx = i
                    break

        # Check if the event is a keyboard input and there is an active input box
        if event.type == pygame.KEYDOWN and activeBoxIdx >= 0:

            activeBox = input_boxes[activeBoxIdx]

            # Check for backspace
            if event.key == pygame.K_BACKSPACE:

                # get text input from 0 to -1 i.e. end.
                activeBox.text = activeBox.text[:-1]

            elif event.key == pygame.K_TAB:
                activeBoxIdx += 1
                if activeBoxIdx >= len(input_boxes):
                    activeBoxIdx = 0

                continue

            elif event.key == pygame.K_RETURN:

                # If the sim is running and the duck is not flying, the sim must have ended
                if running and not duck.flying:
                    # At this point, the function of the ENTER key is to reset the sim
                    duck.reset()
                    running = False
                    scale = 1
                    continue

                try:
                    if not running:
                        magnitude = float(input_boxes[0].text) * 100
                        angle = float(input_boxes[1].text)

                        initial_velocity = polarToCartesian((magnitude, angle))
                        running = True
                        duck.launch(initial_velocity, GRAVITY)

                        calcLaunch(initial_velocity, GRAVITY)

                        virtual_width = WIDTH
                        virtual_height = HEIGHT

                except:
                    activeBoxIdx += 1
                    if activeBoxIdx >= len(input_boxes):
                        activeBoxIdx = 0

            # Unicode standard is used for string
            # formation
            else:
                character = event.unicode
                if character.isnumeric() or character == '.':
                    activeBox.text += event.unicode

    if not running:
        world_offset_x = 0
        world_offset_y = 0
    elif duck.flying:
        if duck.pos[0] > virtual_width / 2:
            world_offset_x = duck.pos[0] - virtual_width / 2
        else:
            world_offset_x = 0

        if duck.pos[1] < ground_height - ground_thickness:
            world_offset_y = duck.pos[1] - ground_height + ground_thickness
        else:
            world_offset_y = 0

    # Draw the virtual screen
    virtual_screen = pygame.Surface((virtual_width, virtual_height))

    virtual_screen.fill(pygame.Color('lightskyblue2'))

    # Draw all entities on the virtual screen
    ground.surf = pygame.Surface((virtual_width + 2 * world_offset_x, ground_thickness))
    ground.pos = (virtual_width / 2, HEIGHT - ground_thickness / 2)
    ground.surf.fill((0, 150, 0))

    slingshotLeftArm = vec(slingshot.rect.center) - vec(slingshot.rect.width * 1 / 3, slingshot.rect.height * 1 / 3)
    slingshotRightArm = vec(slingshot.rect.center) - vec(0, slingshot.rect.height * 1 / 3)

    # Draw lines to represent the sling of the slingshot
    if (duck.pos[0] < slingshotRightArm[0] and duck.pos[1] > slingshotRightArm[1]):
        pygame.draw.line(virtual_screen, 'salmon4', duck.pos - vec(world_offset_x, world_offset_y), slingshotRightArm, width=5)
        pygame.draw.line(virtual_screen, 'salmon4', duck.pos - vec(world_offset_x, world_offset_y), slingshotLeftArm, width=5)

    # Draw all sprites onto the screen
    for entity in all_sprites:
        entity.rect.update(entity.surf.get_rect(center = entity.pos - vec(world_offset_x, world_offset_y)))

        # If the sprite has an image texture, draw the image
        if hasattr(entity, 'image'):
            virtual_screen.blit(entity.image, entity.rect)
        # Otherwise draw the sprite's surface
        else:
            virtual_screen.blit(entity.surf, entity.rect)

    if running and duck.flying:
        duck.move(FPS)
        if not duck.flying:
            rightmost_point = duck.landing_point
            topmost_point = duck.peak_point

            widthScale = (rightmost_point[0] + duck.surf.get_width()) / WIDTH
            heightScale = (HEIGHT - topmost_point[1] + duck.surf.get_height()) / HEIGHT

            scale = max(widthScale, heightScale)
            if scale < 1:
                scale = 1

    # If the Duck hits the ground, stop the simulation
    if running and not duck.flying:

        world_offset_x = 0
        world_offset_y = -(virtual_height - HEIGHT)

        if virtual_width < WIDTH * scale:
            virtual_width += virtual_width / 100 + (WIDTH * scale - virtual_width) / 20

        if virtual_height < HEIGHT * scale:
            virtual_height += virtual_height / 100 + (HEIGHT * scale - virtual_height) / 20

        # Print a dashed line tracing the duck's flight path
        for i in range(int(len(duck.path) / 2)):
            pygame.draw.line(virtual_screen, 'black', duck.path[i * 2] + vec(0, virtual_height - HEIGHT), duck.path[i * 2 + 1] + vec(0, virtual_height - HEIGHT), int(3 * scale))
        if len(duck.path) > 0:
            pygame.draw.circle(virtual_screen, 'blue', duck.path[0] + vec(0, virtual_height - HEIGHT), 6 * scale)
            pygame.draw.circle(virtual_screen, 'green', duck.peak_point + vec(0, virtual_height - HEIGHT), 6 * scale)
            pygame.draw.circle(virtual_screen, 'red', duck.landing_point + vec(0, virtual_height - HEIGHT), 6 * scale)

        virtual_screen = pygame.transform.scale(virtual_screen, (WIDTH, HEIGHT))

    screen.blit(virtual_screen, (0, 0))

    if not running:
        for i in range(len(input_boxes)):
            input_box = input_boxes[i]
            if i == activeBoxIdx:
                input_box.activate()
            else:
                input_box.deactivate()

            # Draw a rectangle for the input box
            pygame.draw.rect(screen, input_box.color, input_box.rect)
            pygame.draw.rect(screen, 'black', input_box.rect, width = 2)
            text_surface = base_font.render(input_box.placeholder, True, (200, 200, 200))
            if len(input_box.text) > 0:
                text_surface = base_font.render(input_box.text, True, (0, 0, 0))

            # Render at position stated in arguments
            screen.blit(text_surface, (input_box.rect.x + 5, input_box.rect.y + 5))

            # Set width of textfield so that text cannot get outside of user's text input
            input_box.rect.w = max(100, text_surface.get_width() + 10)

    pygame.display.update()

    # Wait until the next tick to continue running the simulation
    FramePerSec.tick(FPS)