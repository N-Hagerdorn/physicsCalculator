import pygame
from pygame.math import Vector2 as vec

""" Duck class
Represents a Duck being thrown by a slingshot for no reason at all other than to satisfy my sadistic impulses.
Handles the graphical representation and physical simulation of the Duck.

Inherits:
    pygame.sprite.Sprite

Returns:
    None
"""


class Duck(pygame.sprite.Sprite):

    def __init__(self, ground_height):
        """
        Initializes the Duck sprite with its included graphics and physics parameters.

        Args:
            None

        Returns:
            None
        """
        super().__init__()

        # Surfaces act like hit boxes, a rectangular area that represents the space taken up by the sprite
        self.surf = pygame.Surface((50, 50))

        # Load the sprite image file
        self.image = pygame.transform.scale(pygame.image.load('assets/duck.png'), (50, 50))

        # Get the rectangle that represents the area of the sprite
        self.rect = self.surf.get_rect()

        self.ground_height = ground_height

        # Reset all movement variables of the Duck
        self.reset()

    def launch(self, initial_velocity, gravity):
        """
        Launches the Duck at a certain initial velocity given as a 2D vector.

        Args:
            initial_velocity (vec2(float, float)): Launch velocity of the Duck given as (x_vel, y_vel)
            gravity (vec2(float, float)): Acceleration of the Duck given as (x_acc, y_acc), typically due to gravity

        Returns:
            None
        """

        # Set the Duck's velocity and acceleration due to gravity
        self.vel = initial_velocity
        self.acc = gravity

        # Set the Duck to a flying state
        self.flying = True

    def move(self, fps):
        """
        Moves the Duck for the duration of one frame.

        Args:
            fps (int): The frame rate of the simulation in frames per second

        Returns:
            None
        """

        # Check if the Duck was moving up (negative y velocity) prior to this tick
        moving_up = self.vel[1] < 0

        # Increment the position and velocity of the Duck according to the game tick
        self.pos += self.vel / fps
        self.vel += self.acc / fps

        # Check if the Duck is no longer moving up (non-negative y velocity) after this tick
        moving_down = self.vel[1] >= 0

        # When the Duck is flying, track its trajectory
        if self.flying:

            # When the Duck was moving up prior to this tick and is no longer moving up,
            # we know this point must be the peak of the Duck's trajectory
            if moving_up and moving_down:
                # Record the peak of the Duck's trajectory
                self.path.append(vec(self.pos))
                self.peak_point = vec(self.pos)
            elif self.tick_count % int(fps / 10 + 0.5) == 0:
                # Record the Duck's position every 10th of a second
                self.path.append(vec(self.pos))

            if (self.pos[1] > self.ground_height - self.surf.get_height() * 0.25):
                self.stop()

            self.tick_count += 1

    def reset(self):
        """
        Reset the Duck's position and movement. Used to reset the simulation between runs as well as initializing the duck.

        Args:
            None

        Returns:
            None
        """

        # Set the coordinates of the Duck on the app screen
        self.pos = vec(self.surf.get_width() / 2, self.ground_height - self.surf.get_height() * 0.25)

        # Set the movement parameters of the Duck to 0 so it does not move
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.tick_count = 0
        self.path = []

        self.peak_point = vec(self.pos)
        self.landing_point = vec(self.pos)

        self.flying = False

    def stop(self):

        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.flying = False

        self.landing_point = vec(self.pos)
