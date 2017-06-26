import sys, math

import pygame
from pygame.locals import *
from pygame.color import *

from collections import defaultdict

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util



class Sprite(pygame.sprite.Sprite):

	def __init__(self, position, size):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(size)
		self.image.fill((0, 0, 0))
		self.rect = self.image.get_rect()
		self.dead = False
		self.size = size
	
	def get_bodies(self):
		return [self.body, self.shape]

	# Used for player inputs and such
	def active_update(self, game):
		pass

	# Used for gravity effects and such
	def passive_update(self, game):
		pass

	# Used for general updating. Maybe don't update this, unless you're doing graphics things.
	# I haven't done anything better to deal with that
	def update(self, game):
		self.active_update(game)
		self.passive_update(game)
		self.pymunk2pygame(game.screen)

	def pymunk2pygame(self, screen):
		self.rect.x, self.rect.y = pymunk.pygame_util.to_pygame(self.body.position, screen)


class Game():
	def __init__(self, size, debug_mode=False):
		pygame.init()
		self.debug_mode = debug_mode
		self.size = size
		self.background = pygame.Surface(size)
		self.background.fill(Color('white'))
		# initialize 
		self.screen = pygame.display.set_mode(size)

		self.space = pymunk.Space()
		self.space.gravity = (0, 0)
		self.sprites = defaultdict(lambda: pygame.sprite.Group())

		self.running = False

		self.keypress_events = {"KEY_UP":[],"KEY_DOWN":[],"KEY_HELD":[]}
		self.last_keys_pressed = []

	def update(self):
		self.update_keypress_events()
		# print self.keypress_events
		for layer in self.sprites:
			self.sprites[layer].update(self)

	def draw(self):
		for layer in sorted(self.sprites.keys(), reverse=True):
			self.sprites[layer].draw(self.screen)


	def add_sprite(self, sprite, layer=0):

		self.sprites[layer].add(sprite)
		self.space.add(sprite.get_bodies())


	def remove_sprite(self, sprite):
		for layer in self.sprites:
			if self.sprites[layer].has(sprite):
				self.sprites[layer].remove(sprite)
		self.space.remove(sprite.get_bodies())

	def add_collision_handler(self, sprite1, sprite2, collision_handler, collision_type='begin'):
		type1 = sprite1.shape.collision_type
		type2 = sprite2.shape.collision_type
		if collision_type == 'begin':
			self.space.add_collision_handler(type1, type2).begin = collision_handler
		elif collision_type == 'separate':
			self.space.add_collision_handler(type1, type2).separate = collision_handler

	def update_keypress_events(self):
		old_keys_pressed = self.last_keys_pressed
		new_keys_pressed = self.binary_list_to_int_list(pygame.key.get_pressed())
		# print old_keys_pressed
		# print new_keys_pressed
		# print ""
		keys_down, keys_held, keys_up= [], [], []
		for key in range(323):
			if not key in old_keys_pressed and key in new_keys_pressed: 
				keys_down.append(key)
			elif key in old_keys_pressed and key in new_keys_pressed: 
				keys_held.append(key)
			elif key in old_keys_pressed and not key in new_keys_pressed:
				keys_up.append(key)
		self.keypress_events = self.keypress_events = {"KEY_UP":keys_up,"KEY_DOWN":keys_down,"KEY_HELD":keys_held}
		self.last_keys_pressed = new_keys_pressed
		print self.keypress_events
		
	def binary_list_to_int_list(self,binary_list):
		int_list = []
		for index,value in enumerate(binary_list):
			if binary_list[index]: int_list.append(index)
		return int_list
		
		
	def run_game(self):
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps
		draw_options = pymunk.pygame_util.DrawOptions(self.screen)

		self.running = True
		while self.running:
			# refresh the screen
			self.screen.blit(self.background, (0, 0))
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False

			self.update()
			if self.debug_mode:
				self.space.debug_draw(draw_options)
			else:
				self.draw()

			self.space.step(self.dt)
			self.clock.tick(self.fps)

			pygame.display.flip()
		pygame.display.quit()
		sys.exit()