import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()

        self.surf = pygame.Surface((width, height))
        self.surf.fill((0,150,0))
        self.pos = pygame.math.Vector2(width, height - 10)
        self.rect = self.surf.get_rect(center = self.pos)

