import sys, math

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

class Sprite(pygame.sprite.Sprite):

	def __init__(self, pymunk_body):
		pygame.sprite.Sprite.__init__(self)

	def get_bodies(self):
		return [self.body, self.shape]

	def update(self):
		pass

class Player(Sprite):
	def __init__(self):
		self.gravity = Vec2d(0, -1000)
		self.mass = 5
		self.body = pymunk.Body(self.mass, pymunk.inf)
		self.shape = pymunk.Circle(self.body, 10)
		self.body.position = (300, 300)
		Sprite.__init__(self, self.body)

		self.actions = {
			K_LEFT: lambda: self.walk(-1),
			K_RIGHT: lambda: self.walk(1),
			K_UP: lambda: self.jump()
		}

		self.max_speed = 100. *2.
		self.accel_time = 0.05
		self.accel = (self.max_speed/self.accel_time)
		self.target_vx = 0
		self.jumping = False
	def walk(self, direction):
		self.direction = direction
		# self.target_vx = direction*self.max_speed
		self.shape.surface_velocity = (-self.max_speed*direction, 0)
		# print 'walking', direction
		# self.body.apply_impulse_at_local_point(Vec2d(direction*100, 0), (0, 0))
		# self.body.velocity = Vec2d(self.max_speed*direction, self.body.velocity.y)

	def jump(self):
		print 'jump'
		if not self.jumping:
			self.jumping = True
			self.body.apply_impulse_at_local_point(Vec2d(0, 500))

	def update(self):
		self.body.apply_force_at_local_point(self.gravity, (0, 0))
		# self.body.velocity = Vec2d(0, self.body.velocity.y)
		self.target_vx = 0
		keys = pygame.key.get_pressed()
		for player_key in self.actions:
			if keys[player_key]:
				# print player_key
				self.actions[player_key]()
		# print self.body.velocity
		# self.shape.surface_velocity = Vec2d(-self.target_vx, 0)
		# print self.shape.surface_velocity
		self.shape.friction = -self.accel/self.gravity.y
		# print self.shape.surface_velocity



class Wall(Sprite):
	def __init__(self):
		self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
		self.shape = pymunk.Poly(self.body, [(200, 200), (200, 100), (400, 100), (400, 200)])
		# self.body.position = (300, 200)
		Sprite.__init__(self, self.body)


class Game():
	def __init__(self):
		self.space = pymunk.Space()
		self.space.gravity = (0, 0)
		self.sprites = pygame.sprite.Group()

	def add_sprite(self, sprite):
		self.sprites.add(sprite)
		self.space.add(sprite.get_bodies())


	def run_game(self, size):
		pygame.init()
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps

		player = Player()
		wall = Wall()
		self.add_sprite(player)
		self.add_sprite(wall)
		draw_options = pymunk.pygame_util.DrawOptions(self.screen)

		self.running = True

		self.background = pygame.Surface(size)
		self.background.fill(Color('white'))
		while self.running:
			self.screen.blit(self.background, (0, 0))
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False

			self.sprites.update()
			print player.shape.surface_velocity

			self.space.step(self.dt)
			self.clock.tick(self.fps)

			self.space.debug_draw(draw_options)
			pygame.display.flip()
		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))