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
		# print self.shape.collision_type
		pass

class Player(Sprite):
	def __init__(self, position):
		self.gravity = Vec2d(0, -1000)
		self.mass = 5
		self.body = pymunk.Body(self.mass, pymunk.inf)
		self.shape = pymunk.Circle(self.body, 10)
		self.body.position = position
		Sprite.__init__(self, self.body)

		self.actions = {
			K_LEFT: lambda: self.walk(-1),
			K_RIGHT: lambda: self.walk(1),
			K_UP: lambda: self.jump()
		}

		self.max_speed = 100*2.

		self.shape.friction = 1.0
		print self.shape.friction


		self.target_vx = 0
		self.jumping = False

		self.grounded = False
		# self.body.each_arbiter(self.collision_handler)

	def ground_collision(self, arbiter):
		N = arbiter.contact_point_set.normal
		if arbiter.shapes[1].body:
			if (N.y != 0 and abs(N.x/N.y) < self.shape.friction):
				self.grounded = True

			
		# print 'something happened'
		# return True

	def walk(self, direction):
		self.direction = direction

		# self.target_vx = direction*self.max_speed
		self.shape.surface_velocity = Vec2d(-self.max_speed*direction, 0)
		# print self.shape.surface_velocity
		# print 'walking', direction
		# self.body.apply_impulse_at_local_point(Vec2d(direction*100, 0), (0, 0))
		# self.body.angular_velocity = self.max_speed*direction
		# self.body.velocity = (direction*self.max_speed, self.body.velocity.y)

	def jump(self):
		print self.grounded
		if self.grounded:
			self.grounded = False
			self.body.apply_impulse_at_local_point(Vec2d(0, 500))

	def update(self):
		# gravity
		# print self.body.velocity
		self.body.each_arbiter(self.ground_collision)
		self.body.apply_force_at_local_point(self.gravity, (0, 0))
		# self.body.angular_velocity = 0
		# self.body.velocity = Vec2d(0, self.body.velocity.y)
		self.shape.surface_velocity = Vec2d(0, 0)

		# print self.shape.surface_
		self.target_vx = 0
		keys = pygame.key.get_pressed()
		for player_key in self.actions:
			if keys[player_key]:
				# print player_key
				self.actions[player_key]()
		# print self.body.velocity
		# self.shape.surface_velocity = Vec2d(-self.target_vx, 0)
		# print self.shape.surface_velocity
		# print self.shape.surface_velocity
		
		# print self.shape.surface_velocity



class Platform(Sprite):
	def __init__(self, position, size):
		self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
		p = Vec2d(position)
		s = Vec2d(size)
		self.shape = pymunk.Poly(self.body, [(p.x, p.y), (p.x, p.y-s.y), (p.x+s.x, p.y-s.y), (p.x+s.x, p.y)])
		self.shape.friction = 1.
		Sprite.__init__(self, self.body)

class MovingPlatform(Platform):

	# moves in a path relative to its position
	def __init__(self, position, size, path):
		Platform.__init__(self, position, size)

	def update(self):
		print self.body.position

class Game():
	def __init__(self):
		self.space = pymunk.Space()
		self.space.gravity = (0, 0)
		self.sprites = pygame.sprite.Group()

	def add_sprite(self, sprite):
		self.sprites.add(sprite)
		self.space.add(sprite.get_bodies())

	# def collision_handler(self, arbiter, space, data):
	# 	print arbiter.contact_point_set.normal.perpendicular()

	# 	return True

	def run_game(self, size):
		pygame.init()
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps

		player = Player((300, 220))
		walls = []
		walls.append(Platform((100, 200), (400, 20)))
		walls.append(Platform((100, 400), (20, 200)))
		walls += [Platform((500, 200+y), (20, 20)) for y in xrange(0, 200, 20)]
		walls.append(Platform((220, 220), (20, 20)))
		self.add_sprite(player)
		for wall in walls:
			self.add_sprite(wall)

		# player.body.each_arbiter(self.collision_handler)
		# self.space.add_collision_handler(player.shape.collision_type, wall.shape.collision_type).begin = self.collision_handler

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
			# print player.shape.surface_velocity
			self.space.debug_draw(draw_options)			
			# print player.shape.surface_velocity

			self.space.step(self.dt)
			self.clock.tick(self.fps)

			pygame.display.flip()
		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))