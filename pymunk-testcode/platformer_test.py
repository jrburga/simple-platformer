import sys, math

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

class Sprite(pygame.sprite.Sprite):

	def __init__(self, position, size):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface(size)
		self.image.fill((0, 0, 0))
		self.rect = self.image.get_rect()
	def get_bodies(self):
		return [self.body, self.shape]

	def update(self, screen):
		self.pymunk2pygame(screen)

	def pymunk2pygame(self, screen):
		self.rect.x, self.rect.y = pymunk.pygame_util.to_pygame(self.body.position, screen)

class Player(Sprite):
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		self.image = pygame.image.load('images/apple.png')
		self.image.convert()
		self.size = size
		self.image = pygame.transform.scale(self.image, Vec2d(size)*3)
		self.faces = [None, pygame.transform.flip(self.image, True, False), self.image]
		self.gravity = Vec2d(0, -1000)
		self.mass = 5
		self.body = pymunk.Body(self.mass, pymunk.inf)
		self.shape = pymunk.Circle(self.body,size[0])
		self.body.position = position
		

		self.actions = {
			K_LEFT: lambda: self.walk(-1),
			K_RIGHT: lambda: self.walk(1),
			K_UP: lambda: self.jump()
		}

		self.max_speed = 100*2.
		self.shape.friction = 1.0
		self.grounded = False

	def ground_collision(self, arbiter):
		# checks the normal vector between the player and the object it's colliding with
		# if the slope is less than its coefficient of friction, it is grounded
		N = arbiter.contact_point_set.normal
		if arbiter.shapes[1].body:
			if (N.y != 0 and abs(N.x/N.y) < self.shape.friction):
				self.grounded = True

	def walk(self, direction):
		self.direction = direction
		self.shape.surface_velocity = Vec2d(-self.max_speed*direction, 0)
		self.image = self.faces[self.direction]



	def jump(self):
		# jump if the object is properly grounded
		# set grounded to False
		if self.grounded:
			self.grounded = False
			self.body.apply_impulse_at_local_point(Vec2d(0, 500))

	def update(self, screen):

		# check if object is properly "grounded"
		self.body.each_arbiter(self.ground_collision)
		# apply gravity
		self.body.apply_force_at_local_point(self.gravity, (0, 0))
		# reset surface velocity
		self.shape.surface_velocity = Vec2d(0, 0)
		# get key press and apply action
		keys = pygame.key.get_pressed()
		for player_key in self.actions:
			if keys[player_key]:
				self.actions[player_key]()
		self.pymunk2pygame(screen)
		self.rect.x -= self.size[0]*1.5
		self.rect.y -= self.size[1]*1.8



class Platform(Sprite):
	# creates a rectangle of the given size
	# position is top left corner of the rectangle
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
		p = Vec2d(position)
		s = Vec2d(size)
		self.shape = pymunk.Poly(self.body, [(p.x, p.y), (p.x, p.y-s.y), (p.x+s.x, p.y-s.y), (p.x+s.x, p.y)])
		self.shape.friction = 1.
		

class MovingPlatform(Platform):

	# moves in a path relative to its position
	# where a path is a list of points
	def __init__(self, position, size, path, speed):
		Platform.__init__(self, position, size)
		self.path = [Vec2d(point)+self.body.position for point in path]
		self.dest_index = 0
		self.destination = self.path[self.dest_index]


	def update(self, screen):
		# distance = self.body.position.
		pass
		

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

		# initialize 
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps

		# add objects to the game world
		player = Player((300, 220), (20, 20))
		walls = []
		walls.append(Platform((100, 200), (400, 20)))
		walls.append(Platform((100, 400), (20, 200)))
		walls += [Platform((500, 200+y), (20, 20)) for y in xrange(0, 200, 20)]
		walls.append(Platform((220, 220), (20, 20)))
		self.add_sprite(player)
		for wall in walls:
			self.add_sprite(wall)

		moving_platform = MovingPlatform((300, 250), (60, 10), [(-40, 0), (40, 0)], 1)

		self.add_sprite(moving_platform)

		# set up debug draw mode
		# actually displaying real graphics will take some more effort
		# because the (0, 0) point is in the bottom left (unlike the pygame screen)
		draw_options = pymunk.pygame_util.DrawOptions(self.screen)

		self.running = True

		# create a white background to refresh the screen
		self.background = pygame.Surface(size)
		self.background.fill(Color('white'))

		while self.running:
			# refresh the screen
			self.screen.blit(self.background, (0, 0))
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False

			self.sprites.update(self.screen)
			self.space.debug_draw(draw_options)	
			self.sprites.draw(self.screen)
					

			self.space.step(self.dt)
			self.clock.tick(self.fps)

			pygame.display.flip()
		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))