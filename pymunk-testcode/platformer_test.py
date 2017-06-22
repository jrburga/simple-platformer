import sys, math

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

class Sprite(pygame.sprite.Sprite):

	def __init__(self, pymunk_body):
		pygame.sprite.Srite.__init__(self)

	def update(self):
		pass

class Player(Sprite):
	def __init__(self):
		self.body = pymunk.Body(5, pymunk.inf)
		Sprite.__init__(self, self.body)
		self.shape = pymunk.Circle(self.body, 10, (0, -5))

	def update(self):
		pass

class Game():
	def __init__(self):
		self.space = pymunk.Space()
		self.space.gravity = (0, -1000)
		self.sprites = pygame.sprite.Group()

	def add_sprite(self, sprite):
		self.sprites.add(sprite)
		self.space.add(sprite.body, sprite.shape)


	def run_game(self, size):
		pygame.init()
		self.screen = pygame.display.set_mode(size)
		self.fps = 60
		self.dt = 1./self.fps

		player = Player()

		self.running = True
		while self.running:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False

		self.space.debug_draw(pymunk.pygame_util.DrawOptions(self.screen))

		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))