import pygame

# Colors indicate whether an input box is in focus or not
color_active = pygame.Color('khaki2')
color_passive = pygame.Color('white')

class InputBox:

    def __init__(self, pos, size):
        self.rect = pygame.Rect(pos, size)
        self.active = False
        self.color = color_passive
        self.text = ''
        self.placeholder = 'test'

    def activate(self):
        self.color = color_active
    def deactivate(self):
        self.color = color_passive
