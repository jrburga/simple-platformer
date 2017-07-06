import sys, math, random

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

from Graphics import SpriteSheets

from Basics import Game
from Basics import Sprite

from collections import defaultdict

class Beam(Sprite):
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
		self.a = Vec2d(position)
		self.b = Vec2d(1, 0)
		self.b.rotate_degrees(size[1])
		self.b *= size[0]
		self.b += self.a
		self.image = pygame.Surface((0, 0))
		
		print self.a, self.b

		self.shape = pymunk.Poly(self.body, ((0, 0), (0,0)))
	def update(self, game):
		screen_size = Vec2d(game.screen.get_size())
		self.scale =  screen_size.y/self.a.y
		# print 'scale', self.scale
		pygame.draw.line(game.screen, (255, 255, 255), self.a, self.b, self.scale)

class Beamrider(Sprite):
	def __init__(self, position, size, spaces, bullet_type, color = (255, 255, 255)):
		Sprite.__init__(self, position, size)
		self.body = pymunk.Body(3, pymunk.inf)
		self.body.position = Vec2d(position)
		self.body.body_type = pymunk.Body.KINEMATIC
		size = Vec2d(size)
		self.shape = pymunk.Poly(self.body, [(-size.x/2, size.y/2), (size.x/2, size.y/2), (size.x/2, -size.y/2), (-size.x/2, -size.y/2)])
		self.size = size
		self.grid_position = 2
		self.next_grid_position = None
		self.direction = Vec2d(0, 0)
		self.speed = 300
		self.spaces = spaces[:]
		self.moving_velocity = Vec2d(0, 0)
		self.bullet_type = bullet_type
		self.bullet_speed = 500
		self.last_bullet = None
		self.color = color
		self.image.fill(color)
		self.base_image = self.image.copy()
		self.scale = 1
		self.body.kill = False

	def move_space(self, direction):
		if direction != self.direction.x:
			if direction < 0:
				if self.grid_position == 0:
					return
			if direction > 0:
				if self.grid_position == 4:
					return
			self.direction.x = direction
			if self.next_grid_position:
				self.next_grid_position += direction
			else:
				self.next_grid_position = self.grid_position+direction

	def fire(self, game):
		if self.bullet_type:
			if self.next_grid_position == None and not game.exists(self.last_bullet):
				self.last_bullet = self.bullet_type(self.body.position, [5, 5], self.bullet_speed)
				game.add_sprite(self.last_bullet)

	def passive_update(self, game):
		if self.next_grid_position >= 0 and self.next_grid_position <= 4:
			# print self.body.velocity, self.next_grid_position, int(self.body.position.x/100)*100, self.spaces[self.next_grid_position]
			if int(self.body.position.x) == self.spaces[self.next_grid_position]:
				self.direction.x = 0
				self.grid_position = self.next_grid_position
				self.next_grid_position = None
			if self.direction.x:
				self.body.velocity = self.moving_velocity+self.direction*self.speed
		else:
			self.body.velocity = self.moving_velocity

		if self.body.kill:
			self.dead = True

		

	def pymunk2pygame(self, screen):
		Sprite.pymunk2pygame(self, screen)
		self.rect.x -= self.scale*self.size[0]/2
		self.rect.y -= self.scale*self.size[1]/2

class Bullet(Sprite):
	def __init__(self, position, size, velocity):
		Sprite.__init__(self, position, size)
		# print 'created bullet'
		self.image.fill((255, 255, 255))
		self.base_image = self.image.copy()
		self.body = pymunk.Body(3, pymunk.inf)
		self.body.position = position
		self.body.velocity = velocity
		self.shape = pymunk.Circle(self.body, size[0]/2)
		self.shape.collision_type = 3
		self.body.kill = False

	def passive_update(self, game):
		if self.body.position.y > game.screen.get_size()[1] or self.body.position.y < 0:
			self.dead = True
		if self.body.kill:
			self.dead = True
		screen_size = Vec2d(game.screen.get_size())
		self.scale =  (screen_size.y-self.body.position.y)/screen_size.y
		# print self.scale
		self.image = pygame.transform.rotozoom(self.base_image, 0, self.scale)

class BulletPlayer(Bullet):
	def __init__(self, position, size, speed):
		velocity = Vec2d(0, speed)
		Bullet.__init__(self, position, size, velocity)
		self.shape.collision_typ = 3


class BulletEnemy(Bullet):
	def __init__(self, position, size, speed):
		velocity = Vec2d(0, -speed)
		Bullet.__init__(self, position, size, velocity)
		self.shape.collision_type = 4



class Player(Beamrider):
	# position is a grid space
	def __init__(self, position, size, spaces, bullet_type):
		Beamrider.__init__(self, (spaces[position], size[1]*2), size, spaces, bullet_type)
		self.image.fill(pygame.Color('yellow'))
		self.grid_position = position
		self.shape.collision_type = 2

	def active_update(self, game):
		keys = game.keypress_events
		for key in keys['KEY_HELD']:
			if key == K_RIGHT:
				self.move_space(1)
			if key == K_LEFT:
				self.move_space(-1)
			if key == K_SPACE:
				self.fire(game)


class Enemy(Beamrider):
	def __init__(self, position, size, spaces, bullet_type):
		Beamrider.__init__(self, (spaces[position], 500), size, spaces, bullet_type)
		self.image.fill((255, 255, 255))
		self.bullet_direction = -1
		self.moving_velocity = Vec2d(0, 0)
		self.moving = False
		self.shape.collision_type = 1

	def active_update(self, game):
		# print self.body.position.y
		if self.moving:
			if self.body.position.y < 100:
				self.moving_velocity = Vec2d(0, 600)
			if self.body.position.y > 500 and self.body.velocity.y > 0:
				self.moving_velocity = Vec2d(0, 0)
				self.moving = False

			if random.random() > .95 and self.body.position.y < 400:
				self.fire(game)
		else:
			if random.random() > .95:
				self.moving = True
				self.moving_velocity = Vec2d(0, -300)

		if random.random() > .95:
			if random.random() > .5:
				self.move_space(1)
			else:
				self.move_space(-1)


		screen_size = Vec2d(game.screen.get_size())
		self.scale =  (screen_size.y-self.body.position.y)/screen_size.y
		self.image = pygame.transform.rotozoom(self.base_image, 0, self.scale)





def kill_both(arbiter, space, data):
	print 'collision'
	for shape in arbiter.shapes:
		if shape.body.position.y >= 500:
			return False
		shape.body.kill = True
	return True

def ignore(arbiter, space, data):
	return False

if __name__ == '__main__':
	game = Game((600, 600), debug_mode=False)
	game.background.fill((0, 0, 0))
	grid_width = game.screen.get_size()[0]/6
	print grid_width
	spaces = [(x+1)*grid_width for x in xrange(5)]
	print spaces

	player = Player(2, [50, 30], spaces, bullet_type = BulletPlayer)
	game.add_sprite(player)

	enemies = [
		Enemy(2, [30, 20], spaces, bullet_type = BulletEnemy),
		Enemy(1, [30, 20], spaces, bullet_type = BulletEnemy),
		Enemy(3, [30, 20], spaces, bullet_type = BulletEnemy)
		]
	for enemy in enemies:
		game.add_sprite(enemy)

	beams = [
		# Beam((275, 50), (800, 94)),
		# Beam((325, 50), (800, 86)),
		# Beam((225, 50), (800, 98)),
		# Beam((375, 50), (800, 82)),
		# Beam((175, 50), (800, 102)),
		# Beam((425, 50), (800, 78)),
		Beam((0, 90), (600, 0)),
		Beam((0, 110), (600, 0)),
		Beam((0, 150), (600, 0)),
		Beam((0, 230), (600, 0)),
		Beam((0, 400), (600, 0)),
		# Beam((0, 340), (600, 0)),

	]
	for beam in beams:
		game.add_sprite(beam)

	bullet_player = BulletPlayer((0, 0), (0, 0), 0)
	bullet_enemy = BulletEnemy((0, 0), (0, 0), 0)
	game.add_collision_handler(enemies[0], bullet_player, kill_both)
	game.add_collision_handler(player, bullet_enemy, kill_both)
	game.add_collision_handler(bullet_player, bullet_enemy, ignore)
	game.add_collision_handler(bullet_enemy, bullet_enemy, ignore)
	game.add_collision_handler(enemies[0], enemies[0], ignore)


	game.run_game()