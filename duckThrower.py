# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import math, sys
from duck import Duck
from inputbox import InputBox
import pygame
from pygame.locals import *
from pygame.math import Vector2 as vec

class DuckThrower:

    def __init__(self):
        # Initialize the pygame engine
        pygame.init()

        # Parameters for the app window
        self.HEIGHT = 480
        self.WIDTH = 640
        self.FPS = 60

        # Parameters for scaling the simulation to fit within the app window
        self.world_offset_x = 0                                                 # X offset to scroll the screen and keep the duck in frame
        self.world_offset_y = 0                                                 # Y offset to scroll the screen and keep the duck in frame
        self.scale = 1                                                          # Scale of the virtual world within the app window
        self.virtual_width = self.WIDTH * self.scale                            # Width of the virtual world
        self.virtual_height = self.HEIGHT * self.scale                          # Height of the virtual world
        self.ground_thickness = self.HEIGHT * 1 / 8                             # Thickness of the ground Platform
        self.ground_height = int(self.virtual_height - self.ground_thickness)   # Level of the top of the ground above the bottom of the app window

        # Physics constants
        self.GRAVITY = vec(0, 980)

        # Not sure what this thingamabob does, but it sounds important
        self.FramePerSec = pygame.time.Clock()

        # Flag to indicate if the simulation has ended
        self.running = False

        # Set the app window size and give it a fancy-shmancy title
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("The Duck Thrower")

        # Create a virtual screen that scales to contain the entire simulation world
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))

        # Define the duck as a custom sprite using the Duck class
        self.duck = Duck(self.ground_height)

        # Define the ground as a simple sprite
        self.ground = pygame.sprite.Sprite()
        self.ground.surf = pygame.Surface((self.virtual_width + 2 * self.world_offset_x, self.ground_thickness))
        self.ground.surf.fill((0, 150, 0))
        self.ground.pos = (self.virtual_width / 2, self.HEIGHT - self.ground_thickness / 2)
        self.ground.rect = self.ground.surf.get_rect(center = self.ground.pos)


        # Define the slingshot as a simple sprite
        self.slingshot = pygame.sprite.Sprite()
        self.slingshot.surf = pygame.Surface((100, 100))
        self.slingshot.image = pygame.transform.scale(pygame.image.load('assets/slingshot.png'), (100,100))
        self.slingshot.pos = (self.WIDTH * 0.15, self.HEIGHT * 0.8)
        self.slingshot.rect = self.slingshot.surf.get_rect(center = self.slingshot.pos)

        # Add all sprites to a sprite group for easier handling
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.ground)
        self.all_sprites.add(self.duck)
        self.all_sprites.add(self.slingshot)

        # Instantiate two text input boxes for receiving user input values
        input_box1 = InputBox((20, 20), (140, 30))
        input_box1.placeholder = 'speed'
        input_box2 = InputBox((20, 70), (140, 30))
        input_box2.placeholder = 'angle'

        self.base_font = pygame.font.Font(None, 32)

        # Place the input boxes in a list for easier handling
        self.input_boxes = [input_box1, input_box2]
        self.active_box_idx = 0

    # Convert a polar vector to its equivalent Cartesian vector
    # Polar vector is (magnitude, angle) where angle is in degrees
    def polarToCartesian(self, polar_vect):
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

    def cartesianToPolar(self, cartesian_vect):
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

    def distance(self, position_vector1, position_vector2):
        """
        Finds the distance between two objects based on their position vectors.

        Args:
            position_vector1 (vec2(float, float)): The 2D cartesian position vector of the first object
            position_vector2 (vec2(float, float)): The 2D cartesian position vector of the second object

        Returns:
            float: The distance between the two position vectors
        """
        distance_vector = position_vector2 - position_vector1
        dist = self.cartesianToPolar(distance_vector)[0]

        return dist


    def calcLaunch(self, initial_velocity, acceleration):
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

    def reset_sim(self):
        self.duck.reset()
        self.running = False
        self.scale = 1
        self.virtual_width = self.WIDTH * self.scale
        self.virtual_height = self.HEIGHT * self.scale
        self.world_offset_x = 0
        self.world_offset_y = 0

    def sim(self):
        while True:

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if not self.running and event.type == pygame.MOUSEBUTTONDOWN:
                    if self.duck.rect.collidepoint(event.pos):
                        self.duck.swapImage()
                        self.reset_sim()
                        continue
                    else:
                        self.active_box_idx = -1
                        for i in range(len(self.input_boxes)):
                            if self.input_boxes[i].rect.collidepoint(event.pos):
                                self.active_box_idx = i
                                break

                # Check if the event is a keyboard input and there is an active input box
                if event.type == pygame.KEYDOWN and self.active_box_idx >= 0:

                    active_box = self.input_boxes[self.active_box_idx]

                    # Check for backspace
                    if event.key == pygame.K_BACKSPACE:

                        # get text input from 0 to -1 i.e. end.
                        active_box.text = active_box.text[:-1]

                    elif event.key == pygame.K_TAB:
                        self.active_box_idx += 1
                        if self.active_box_idx >= len(self.input_boxes):
                            self.active_box_idx = 0

                        continue

                    elif event.key == pygame.K_RETURN:

                        # If the sim is running and the duck is not flying, the sim must have ended
                        if self.running and not self.duck.flying:
                            # At this point, the function of the ENTER key is to reset the sim
                            self.reset_sim()
                            continue
                        try:
                            if not self.running:
                                magnitude = float(self.input_boxes[0].text) * 100
                                angle = float(self.input_boxes[1].text)

                                initial_velocity = self.polarToCartesian((magnitude, angle))
                                self.running = True
                                self.duck.launch(initial_velocity, self.GRAVITY)

                                self.calcLaunch(initial_velocity, self.GRAVITY)

                                self.virtual_width = self.WIDTH
                                self.virtual_height = self.HEIGHT

                        except:
                            self.active_box_idx += 1
                            if self.active_box_idx >= len(self.input_boxes):
                                self.active_box_idx = 0

                    elif event.key == pygame.K_ESCAPE:
                        self.reset_sim()

                    # Unicode standard is used for string formation
                    elif event.unicode:
                        character = event.unicode
                        if character.isnumeric() or character == '.':
                            active_box.text += event.unicode

            if not self.running:
                self.world_offset_x = 0
                self.world_offset_y = 0
            elif self.duck.flying:
                if self.duck.pos[0] > self.virtual_width / 2:
                    self.world_offset_x = self.duck.pos[0] - self.virtual_width / 2
                else:
                    self.world_offset_x = 0

                if self.duck.pos[1] < self.ground_height - 2 * self.ground_thickness:
                    self.world_offset_y = self.duck.pos[1] - self.ground_height + 2 * self.ground_thickness
                else:
                    self.world_offset_y = 0

            # Draw the virtual screen
            self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))

            self.virtual_screen.fill(pygame.Color('lightskyblue2'))

            # Draw all entities on the virtual screen
            self.ground.surf = pygame.Surface((self.virtual_width, self.virtual_height))
            self.ground.pos = (self.virtual_width / 2 + self.world_offset_x, self.HEIGHT + self.virtual_height / 2 - self.ground_thickness)
            self.ground.surf.fill((0, 150, 0))

            slingshotLeftArm = vec(self.slingshot.rect.center) - vec(self.slingshot.rect.width * 1 / 3, self.slingshot.rect.height * 1 / 3)
            slingshotRightArm = vec(self.slingshot.rect.center) - vec(0, self.slingshot.rect.height * 1 / 3)

            # Draw lines to represent the sling of the slingshot
            if (self.duck.pos[0] < slingshotRightArm[0] and self.duck.pos[1] > slingshotRightArm[1]):
                pygame.draw.line(self.virtual_screen, 'salmon4', self.duck.pos - vec(self.world_offset_x, self.world_offset_y), slingshotRightArm, width=5)
                pygame.draw.line(self.virtual_screen, 'salmon4', self.duck.pos - vec(self.world_offset_x, self.world_offset_y), slingshotLeftArm, width=5)

            # Draw all sprites onto the screen
            for entity in self.all_sprites:
                entity.rect.update(entity.surf.get_rect(center = entity.pos - vec(self.world_offset_x, self.world_offset_y)))

                # If the sprite has an image texture, draw the image
                if hasattr(entity, 'image'):
                    self.virtual_screen.blit(entity.image, entity.rect)
                # Otherwise draw the sprite's surface
                else:
                    self.virtual_screen.blit(entity.surf, entity.rect)

            if self.running and self.duck.flying:
                self.duck.move(self.FPS)
                if not self.duck.flying:
                    rightmost_point = self.duck.landing_point
                    topmost_point = self.duck.peak_point

                    width_scale = (rightmost_point[0] + self.duck.surf.get_width()) / self.WIDTH
                    height_scale = (self.HEIGHT - topmost_point[1] + self.duck.surf.get_height()) / self.HEIGHT

                    self.scale = max(width_scale, height_scale)
                    if self.scale < 1:
                        self.scale = 1

            # If the Duck hits the ground, stop the simulation
            if self.running and not self.duck.flying:

                self.world_offset_x = 0
                self.world_offset_y = -(self.virtual_height - self.HEIGHT)

                if self.virtual_width < self.WIDTH * self.scale:
                    self.virtual_width += self.virtual_width / 100 + (self.WIDTH * self.scale - self.virtual_width) / 20

                if self.virtual_height < self.HEIGHT * self.scale:
                    self.virtual_height += self.virtual_height / 100 + (self.HEIGHT * self.scale - self.virtual_height) / 20

                # Print a dashed line tracing the duck's flight path
                for i in range(int(len(self.duck.path) / 2)):
                    pygame.draw.line(self.virtual_screen, 'black', self.duck.path[i * 2] + vec(0, self.virtual_height - self.HEIGHT), self.duck.path[i * 2 + 1] + vec(0, self.virtual_height - self.HEIGHT), int(3 * self.scale))
                if len(self.duck.path) > 0:
                    pygame.draw.circle(self.virtual_screen, 'blue', self.duck.path[0] + vec(0, self.virtual_height - self.HEIGHT), 6 * self.scale)
                    pygame.draw.circle(self.virtual_screen, 'green', self.duck.peak_point + vec(0, self.virtual_height - self.HEIGHT), 6 * self.scale)
                    pygame.draw.circle(self.virtual_screen, 'red', self.duck.landing_point + vec(0, self.virtual_height - self.HEIGHT), 6 * self.scale)

                self.virtual_screen = pygame.transform.scale(self.virtual_screen, (self.WIDTH, self.HEIGHT))

            self.screen.blit(self.virtual_screen, (0, 0))

            if not self.running:
                for i in range(len(self.input_boxes)):
                    input_box = self.input_boxes[i]
                    if i == self.active_box_idx:
                        input_box.activate()
                    else:
                        input_box.deactivate()

                    # Draw a rectangle for the input box
                    pygame.draw.rect(self.screen, input_box.color, input_box.rect)
                    pygame.draw.rect(self.screen, 'black', input_box.rect, width = 2)
                    text_surface = self.base_font.render(input_box.placeholder, True, (200, 200, 200))
                    if len(input_box.text) > 0:
                        text_surface = self.base_font.render(input_box.text, True, (0, 0, 0))

                    # Render at position stated in arguments
                    self.screen.blit(text_surface, (input_box.rect.x + 5, input_box.rect.y + 5))

                    # Set width of textfield so that text cannot get outside of user's text input
                    input_box.rect.w = max(100, text_surface.get_width() + 10)

            pygame.display.update()

            # Wait until the next tick to continue running the simulation
            self.FramePerSec.tick(self.FPS)
