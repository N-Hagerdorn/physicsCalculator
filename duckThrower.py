# Python standard modules
import math
import sys

# Pygame module
import pygame
from pygame.locals import *
from pygame.math import Vector2 as Vec

# Custom modules
from duck import Duck
from inputbox import InputBox


class DuckThrower:

    def __init__(self):
        """
        Initializes a DuckThrower object with all the parameters needed to run the simulation.

        Returns:
            None
        """
        # Initialize the pygame engine
        pygame.init()

        # Parameters for the app window
        self.HEIGHT = 480
        self.WIDTH = 640
        self.FPS = 60

        # Parameters for scaling the simulation to fit within the app window
        self.world_offset_x = 0                                                 # X offset to scroll the screen and keep the duck in frame
        self.world_offset_y = 0                                                 # Y offset to scroll the screen and keep the duck in frame
        self.flight_points = [0, 0]                                             # List to hold important points in the flight trajectory
        self.scale = 1                                                          # Scale of the virtual world within the app window
        self.virtual_width = self.WIDTH * self.scale                            # Width of the virtual world
        self.virtual_height = self.HEIGHT * self.scale                          # Height of the virtual world
        self.ground_thickness = self.HEIGHT * 1 / 8                             # Thickness of the ground Platform
        self.ground_height = int(self.virtual_height - self.ground_thickness)   # Level of the top of the ground above the bottom of the app window

        # Physics constants
        self.GRAVITY = Vec(0, 980)

        # Not sure what this thingamabob does, but it sounds important
        self.FramePerSec = pygame.time.Clock()

        # Flag to indicate if the simulation has ended
        self.running = False

        # Set the app window size and give it an appropriate title and icon
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("The Duck Thrower")
        pygame.display.set_icon(pygame.image.load('assets/duck7.png'))

        # Create a virtual screen that scales to contain the entire simulation world
        self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))

        # Define the duck as a custom sprite using the Duck class
        self.duck = Duck(self.ground_height)

        # Define the ground as a simple sprite
        self.ground = pygame.sprite.Sprite()
        self.ground.surf = pygame.Surface((self.virtual_width + 2 * self.world_offset_x, self.ground_thickness))
        self.ground.surf.fill((0, 150, 0))
        self.ground.pos = (self.virtual_width / 2, self.HEIGHT - self.ground_thickness / 2)
        self.ground.rect = self.ground.surf.get_rect(center=self.ground.pos)

        # Define the slingshot as a simple sprite
        self.slingshot = pygame.sprite.Sprite()
        self.slingshot.surf = pygame.Surface((100, 100))
        self.slingshot.image = pygame.transform.scale(pygame.image.load('assets/slingshot.png'), (100,100))
        self.slingshot.pos = (self.WIDTH * 0.15, self.HEIGHT * 0.8)
        self.slingshot.rect = self.slingshot.surf.get_rect(center=self.slingshot.pos)

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
            Vec(float, float): A 2D vector in the form (x, y)
        """

        x = polar_vect[0] * math.cos(polar_vect[1] * math.pi / 180)
        # y must be negative because pygame uses inverted y-axis coordinates
        y = -polar_vect[0] * math.sin(polar_vect[1] * math.pi / 180)

        return Vec(x, y)

    def cartesianToPolar(self, cartesian_vect):
        """
        Converts a Cartesian vector to a polar vector.

        Args:
            cartesian_vect (vec2(float, float)): A 2D vector or 2-element list in the form (x, y)

        Returns:
            Vec(float, float): A 2D vector in the form (magnitude, angle)
        """

        magnitude = math.sqrt(cartesian_vect[0] * cartesian_vect[0] + cartesian_vect[1] * cartesian_vect[1])
        angle = math.atan2(cartesian_vect[1], cartesian_vect[0])

        return Vec(magnitude, angle)

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
        Calculates the peak and landing points of a simple ballistic trajectory given the initial launch velocity.

        Args:
            initial_velocity (vec2(float, float)): The 2D cartesian vector representing the velocity of the duck in cm/s
            acceleration (vec2(float, float)): The 2D cartesian vector representing the acceleration of the duck in cm/s^2

        Returns:
            peak_point (vec2(float, float)): The peak point of the duck's trajectory relative to its initial point of launch
            landing_point (vec2(float, float)): The landing point of the duck relative to its initial point of launch
        """

        # Mass actually doesn't matter because flight path is independent of mass, but it's in the equation for KE
        mass = 1

        # Find the maximum altitude of the object using kinetic energy to potential energy conversion
        vertical_kinetic_energy = 1/2 * mass * initial_velocity[1] * initial_velocity[1]
        maximum_potential_energy = -vertical_kinetic_energy
        altitude = maximum_potential_energy / (mass * acceleration[1])

        # Use kinematics equations to find the flight time to the peak of the flight
        rise_time = math.sqrt(abs(2 * altitude / acceleration[1]))

        # Use kinematics to find the flight time from the peak of the flight to landing
        drop = altitude
        fall_time = math.sqrt(abs(2 * drop / acceleration[1]))

        flight_time = rise_time + fall_time

        distance = flight_time * initial_velocity[0]

        return [distance / 100, altitude / 100]

    def reset_sim(self):
        """
        Resets the simulation so it may be run again with different starting parameters.

        Returns:
            None
        """

        # Reset the duck's physics parameters
        self.duck.reset()

        # Stop the simulation
        self.running = False

        # Set the screen scaling to restore the original camera zoom
        self.scale = 1
        self.virtual_width = self.WIDTH * self.scale
        self.virtual_height = self.HEIGHT * self.scale

        # Reset the world offsets so the camera moves back to the slingshot
        self.world_offset_x = 0
        self.world_offset_y = 0

        # Reset the calculated flight data so it is ready for the next run
        self.flight_points = [0, 0]

    def sim(self):
        """
        Runs the duck throwing simulation loop.

        Returns:
            None
        """

        # The simulation runs as an infinite loop
        while True:

            # Process events, which consist of user inputs
            for event in pygame.event.get():

                # QUIT event occurs when the user clicks the X to close the app window
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                # MOUSEBUTTONDOWN events occur whenever the user clicks
                # All click events in this simulation occur only when the duck launch routine is not running
                if not self.running and event.type == pygame.MOUSEBUTTONDOWN:

                    # If the user clicks on the duck, swap the duck's sprite image
                    if self.duck.rect.collidepoint(event.pos):
                        self.duck.swapImage()
                        self.reset_sim()

                    # The other clickable objects are text input boxes, which can be clicked to select them
                    else:

                        # Assume no box was clicked, so none are considered active
                        self.active_box_idx = -1

                        # Loop through the list of input boxes to find which one has been clicked
                        for i in range(len(self.input_boxes)):
                            if self.input_boxes[i].rect.collidepoint(event.pos):

                                # Mark the clicked box as active
                                self.active_box_idx = i
                                break

                # Check if the event is a keyboard input and there is an active input box
                if event.type == pygame.KEYDOWN and self.active_box_idx >= 0:

                    # Get the active text input box
                    active_box = self.input_boxes[self.active_box_idx]

                    # Check for a Backspace
                    if event.key == pygame.K_BACKSPACE:

                        # Drop the last character from the input box's contents
                        active_box.text = active_box.text[:-1]

                    # Check for a Tab
                    elif event.key == pygame.K_TAB:

                        # Move focus to the next text input box
                        self.active_box_idx += 1

                        # Wrap around to the first input box if the end of the box list is reached
                        if self.active_box_idx >= len(self.input_boxes):
                            self.active_box_idx = 0

                    # Check for an Enter/Return
                    elif event.key == pygame.K_RETURN:

                        # If the sim is running and the duck is not flying, the sim must have ended
                        if self.running and not self.duck.flying:
                            # At this point, the function of the ENTER key is to reset the sim
                            self.reset_sim()

                        # If the sim is not running, get the numbers from the input boxes and launch the duck
                        elif not self.running:

                            # Magnitude is given in m/s, but the sim uses the scale 1px = 1cm, so convert to cm/s
                            magnitude = float(self.input_boxes[0].text) * 100
                            angle = float(self.input_boxes[1].text)

                            # Convert the velocity to cartesian for easier use
                            initial_velocity = self.polarToCartesian((magnitude, angle))

                            # Change the sim state to running and launch the duck
                            self.running = True
                            self.duck.launch(initial_velocity, self.GRAVITY)

                            # Calculate the peak altitude and distance the duck flies
                            self.flight_points = self.calcLaunch(initial_velocity, self.GRAVITY)

                    # Check for Escape
                    elif event.key == pygame.K_ESCAPE:

                        # Escape resets the simulation regardless of the simulation state
                        self.reset_sim()

                    # Check if the input key has an equivalent unicode character
                    elif event.unicode:

                        # Only allow numeric input, including periods but not negatives, in the input boxes
                        character = event.unicode
                        if character.isnumeric() or character == '.':
                            active_box.text += event.unicode

                            # If the active box is the launch speed, limit it to 0-30 m/s
                            if self.active_box_idx == 0:
                                if float(active_box.text) > 30:
                                    active_box.text = '30'

                            # If the active box is the launch angle, limit it to 0-90 degrees
                            elif self.active_box_idx == 1:
                                if float(active_box.text) > 90:
                                    active_box.text = '90'

            # World offsets are used to shift all assets as the duck flies so the duck remains in the center of the screen
            # If the simulation is not running, the world offsets should be 0
            if not self.running:
                self.world_offset_x = 0
                self.world_offset_y = 0

            # When the duck is flying, set the world offsets
            elif self.duck.flying:

                # Wait until the duck reaches the middle of the screen horizontally, then follow the duck until it lands
                if self.duck.pos[0] > self.virtual_width / 2:
                    self.world_offset_x = self.duck.pos[0] - self.virtual_width / 2
                else:
                    self.world_offset_x = 0

                # Wait until the duck reaches twice the height of the ground vertically, then follow the duck until it lands
                if self.duck.pos[1] < self.ground_height - 2 * self.ground_thickness:
                    self.world_offset_y = self.duck.pos[1] - self.ground_height + 2 * self.ground_thickness
                else:
                    self.world_offset_y = 0

            # Draw the virtual screen and fill it with the sky color
            self.virtual_screen = pygame.Surface((self.virtual_width, self.virtual_height))
            self.virtual_screen.fill(pygame.Color('lightskyblue2'))

            # Draw the ground as a green rectangle on the virtual screen
            self.ground.surf = pygame.Surface((self.virtual_width, self.virtual_height))
            self.ground.pos = (self.virtual_width / 2 + self.world_offset_x, self.HEIGHT + self.virtual_height / 2 - self.ground_thickness)
            self.ground.surf.fill((0, 150, 0))

            # Find the left and right arms of the slingshot so a line can be drawn to represent the rubber band
            slingshot_left_arm = Vec(self.slingshot.rect.center) - Vec(self.slingshot.rect.width * 1 / 3, self.slingshot.rect.height * 1 / 3)
            slingshot_right_arm = Vec(self.slingshot.rect.center) - Vec(0, self.slingshot.rect.height * 1 / 3)

            # Draw lines to represent the rubber band of the slingshot
            if self.duck.pos[0] < slingshot_right_arm[0] and self.duck.pos[1] > slingshot_right_arm[1]:
                pygame.draw.line(self.virtual_screen, 'salmon4', self.duck.pos - Vec(self.world_offset_x, self.world_offset_y), slingshot_right_arm, width=5)
                pygame.draw.line(self.virtual_screen, 'salmon4', self.duck.pos - Vec(self.world_offset_x, self.world_offset_y), slingshot_left_arm, width=5)

            # Draw all sprites onto the screen using the world offsets for correct positioning
            for entity in self.all_sprites:
                entity.rect.update(entity.surf.get_rect(center=entity.pos - Vec(self.world_offset_x, self.world_offset_y)))

                # If the sprite has an image texture, draw the image
                if hasattr(entity, 'image'):
                    self.virtual_screen.blit(entity.image, entity.rect)
                # Otherwise draw the sprite's surface
                else:
                    self.virtual_screen.blit(entity.surf, entity.rect)

            if self.running and self.duck.flying:

                # Move the duck every tick when the duck is flying
                self.duck.move(self.FPS)

                # When the duck lands, get the peak and landing points of the duck's path,
                # which tell us how large to scale the screen to capture the entire trajectory
                if not self.duck.flying:
                    rightmost_point = self.duck.landing_point
                    topmost_point = self.duck.peak_point

                    # Set the width scale and height scales individually to capture the entire trajectory on screen
                    width_scale = (rightmost_point[0] + self.duck.surf.get_width()) / self.WIDTH
                    height_scale = (self.HEIGHT - topmost_point[1] + self.duck.surf.get_height()) / self.HEIGHT

                    # To scale the screen uniformly, choose the larger of the two scales and use that as the actual scale
                    self.scale = max(width_scale, height_scale)

                    # The screen should never be scaled smaller than the original screen size
                    if self.scale < 1:
                        self.scale = 1

            # If the duck hits the ground, stop the simulation
            if self.running and not self.duck.flying:

                # Set the world offsets to a fixed amount so the entities no longer move
                self.world_offset_x = 0
                self.world_offset_y = -(self.virtual_height - self.HEIGHT)

                # Once per tick, increment the size of the virtual screen until it is large enough to contain the trajectory
                # This creates a smooth zoom-out animation once the duck lands
                if self.virtual_width < self.WIDTH * self.scale:
                    self.virtual_width += self.virtual_width / 100 + (self.WIDTH * self.scale - self.virtual_width) / 20

                if self.virtual_height < self.HEIGHT * self.scale:
                    self.virtual_height += self.virtual_height / 100 + (self.HEIGHT * self.scale - self.virtual_height) / 20

                # Print a dashed line tracing the duck's flight path
                for i in range(int(len(self.duck.path) / 2)):
                    # Print a line from every even-indexed point in the trajectory to the next point,
                    # which creates a dashed line along the flight path
                    pygame.draw.line(self.virtual_screen, 'black', self.duck.path[i * 2] + Vec(0, self.virtual_height - self.HEIGHT), self.duck.path[i * 2 + 1] + Vec(0, self.virtual_height - self.HEIGHT), int(3 * self.scale))

                if len(self.duck.path) > 0:

                    # Draw a blue circle at the starting point, green circle at the peak, and red circle at the end point
                    pygame.draw.circle(self.virtual_screen, 'blue', self.duck.path[0] + Vec(0, self.virtual_height - self.HEIGHT), 6 * self.scale)
                    pygame.draw.circle(self.virtual_screen, 'green', self.duck.peak_point + Vec(0, self.virtual_height - self.HEIGHT), 6 * self.scale)
                    pygame.draw.circle(self.virtual_screen, 'red', self.duck.landing_point + Vec(0, self.virtual_height - self.HEIGHT), 6 * self.scale)

                # Scale the virtual screen down to fit within the actual screen
                self.virtual_screen = pygame.transform.scale(self.virtual_screen, (self.WIDTH, self.HEIGHT))

            # Draw the virtual screen onto the actual screen
            self.screen.blit(self.virtual_screen, (0, 0))

            # If the simulation is over, draw labels at each of the three important points (start, peak, end)
            if self.running and not self.duck.flying and len(self.duck.path) > 0:

                # Get the flight peak and distance calculated when the duck was launched
                distance = self.flight_points[0]
                altitude = self.flight_points[1]

                # Calculate the locations of the start, end, and peak points of the flight on the screen
                start_point = self.duck.path[0]
                end_point = self.duck.path[0] + 100 * Vec(distance / self.scale, 0)
                peak_point = self.duck.path[0] + 100 * Vec(distance / 2 / self.scale, altitude / self.scale)

                # Make text labels for each of the points
                start_label = self.base_font.render(str(Vec(0, 0)), True, 'black')
                end_label = self.base_font.render(str(Vec(distance, 0)), True, 'black')
                peak_label = self.base_font.render(str(Vec(distance / 2, -altitude)), True, 'black')

                # Offset the start point label to the right and below the start point
                start_label_pos = start_point + Vec(20, 20)

                # Offset the end point label to the left and below the end point,
                # making sure it does not clip out of the screen
                end_label_pos_x = max(end_point[0] - end_label.get_width() - 50, 20)
                end_label_pos_x = min(end_label_pos_x, self.WIDTH - end_label.get_width())
                end_label_pos = Vec(end_label_pos_x, end_point[1] + 20)

                # Ensure the end point label does not overlap the start point label
                if self.distance(end_label_pos, start_label_pos) < start_label.get_width() + 20:
                    end_label_pos += Vec(start_label.get_width() + 50, 0)

                # Offset the peak point label below the peak point,
                # Making sure it does not clip out of the screen
                peak_label_pos_x = max(peak_point[0] - peak_label.get_width() / 2, 20)
                peak_label_pos_x = min(peak_label_pos_x, self.WIDTH - peak_label.get_width())
                peak_label_pos_y = max(peak_point[1] + 60, 20)
                peak_label_pos = Vec(peak_label_pos_x, peak_label_pos_y)

                # Draw the point labels on the screen
                self.screen.blit(start_label, start_label_pos)
                self.screen.blit(end_label, end_label_pos)
                self.screen.blit(peak_label, peak_label_pos)

            # When the sim is not running, draw the text input boxes on screen
            if not self.running:
                for i in range(len(self.input_boxes)):
                    input_box = self.input_boxes[i]

                    # Activate the active input box so it renders in the proper color
                    if i == self.active_box_idx:
                        input_box.activate()
                    else:
                        input_box.deactivate()

                    # Draw a rectangle for the input box and a black frame around it
                    pygame.draw.rect(self.screen, input_box.color, input_box.rect)
                    pygame.draw.rect(self.screen, 'black', input_box.rect, width=2)

                    # Make a text label with the input box's placeholder text
                    text_surface = self.base_font.render(input_box.placeholder, True, (200, 200, 200))

                    # If there is text in the input box, replace the placeholder text with it
                    if len(input_box.text) > 0:
                        text_surface = self.base_font.render(input_box.text, True, (0, 0, 0))

                    # Render the text on the screen on top of the input box
                    self.screen.blit(text_surface, (input_box.rect.x + 5, input_box.rect.y + 5))

                    # Adjust the width of the text box so longer input will not visually overflow
                    input_box.rect.w = max(100, text_surface.get_width() + 10)

            # Update the pygame display, which allows all drawn entities to appear on screen
            pygame.display.update()

            # Wait until the next tick to continue running the simulation
            self.FramePerSec.tick(self.FPS)
