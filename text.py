import pygame

pygame.init()

class TextSprite(pygame.sprite.Sprite):
	def __init__(self, name):
		pygame.sprite.Sprite.__init__(self)
		self.name = name


class TextGroup(pygame.sprite.Group):
	def __init__(self):
		pygame.sprite.Group.__init__(self)

	def draw(self, surface):
		for sprite in self.sprites():
			print sprite.name

s = TextSprite('Jake')
g = TextGroup()
