import sys, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util
import random 
"""
TODO
- Bullets (key_press --> creation --> collision w/ asteroid --> destroy asteroid & create 2 a fraction of the size)
    * bullets shouldn't wrap around / should have a timer (check the game)
"""

class Sprite(pygame.sprite.Sprite):
	def __init__(self, pymunk_body):
		pygame.sprite.Sprite.__init__(self)

	def get_bodies(self):
		return [self.body, self.shape]

	def update(self):
		pass

class Player(Sprite):
	def __init__(self, position):
		# set physical properties of shup
		self.gravity = Vec2d(0, 0)
		self.mass = 5
		self.radius = 10
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass,0,self.radius),pymunk.Body.DYNAMIC)
		self.shape = pymunk.Poly(self.body, [(-5,0),(5,0),(0,10)])
		self.body.position = position
		self.shape.friction = 1.0
		
		# legal buttons for player actions
		self.legal_actions = [K_UP,K_DOWN,K_LEFT,K_RIGHT]

		# tune rocket's forward and turning thrust
		self.forward_thrust = 30 # as an instantaneous force (impulse)
		self.turning_speed = 0.1 # as radians per step

		Sprite.__init__(self, self.body)

	def move(self, buttons_pressed):
		# up key applies forward force
		if K_UP in buttons_pressed and not K_DOWN in buttons_pressed:
			self.body.apply_impulse_at_local_point((0,self.forward_thrust), (0,0))

		# down key decreases velocity by 10%
		elif K_DOWN in buttons_pressed and not K_UP in buttons_pressed:
			self.body.velocity = self.body.velocity[0] * 0.9, self.body.velocity[1] * 0.9

		# right and left keys turn right and left, respectively, a constant amount
		if K_RIGHT in buttons_pressed and not K_LEFT in buttons_pressed:
			self.body.angle -= self.turning_speed
		elif K_LEFT in buttons_pressed and not K_RIGHT in buttons_pressed:
			self.body.angle += self.turning_speed

	def update(self):
		# get key press and apply action
		keys_pressed_binary = pygame.key.get_pressed()
		keys_pressed_list = []
		for key in self.legal_actions:
			if keys_pressed_binary[key]:
				keys_pressed_list.append(key)
		self.move(keys_pressed_list)
			
class Asteroid(Sprite):
	def __init__(self, size, position, velocity):
		# set physical properties
		self.gravity = Vec2d(0, 0)
		self.mass = 5
		self.radius = size
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass,0,self.radius),pymunk.Body.KINEMATIC)
		self.shape = pymunk.Circle(self.body, self.radius)
		self.shape.friction = 1.0
		self.body.velocity = velocity
		print self.body.velocity
		self.body.position = position

		Sprite.__init__(self, self.body)

class Game():
	def __init__(self):
		self.space = pymunk.Space()
		self.space.gravity = (0, 0)
		self.sprites = pygame.sprite.Group()

	def add_sprite(self, sprite):
		self.sprites.add(sprite)
		self.space.add(sprite.get_bodies())

	def wrap_around(self,sprites,screen_size):
		"""
		Make it so sprites that go off screen teleport to the other side.
		"""
		screen_width = screen_size[0]
		screen_height = screen_size[1]
		for sprite in self.sprites:
			x,y = pymunk.pygame_util.to_pygame(sprite.body.position, self.background)

			if x < 0:
				x = screen_width + x
			elif x > screen_width:
				x = x % screen_width 
			
			if y < 0:
				y = screen_height + y
			elif y > screen_height:
				y = y % screen_height 

			sprite.body.position = pymunk.pygame_util.from_pygame((x,y), self.background)

	def add_collision_handler(self, sprite1, sprite2, collision_handler, collision_type='begin'):
		type1 = sprite1.shape.collision_type
		type2 = sprite2.shape.collision_type
		if collision_type == 'begin':
			self.space.add_collision_handler(type1, type2).begin = collision_handler
		elif collision_type == 'separate':
			self.space.add_collision_handler(type1, type2).separate = collision_handler

	def run_game(self, size):
		
		pygame.init()

		### initialize display settings ###
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps


		### Add objects to the game world ###

		# add player to the game world
		player = Player((300, 220))
		player.body.filter = pymunk.ShapeFilter(categories=1)
		self.add_sprite(player)

		# add 10 asteroids
		for _ in range(5):
			random_position = random.randrange(0,size[0]), random.randrange(0,size[1])
			random_velocity = random.randrange(-100,100), random.randrange(-100,100)
			random_size = random.randrange(20,60)
			asteroid = Asteroid(random_size,random_position,random_velocity)
			asteroid.body.filter = pymunk.ShapeFilter(categories=2)
			self.add_sprite(asteroid)

		# add player-asteroid collision handler (nothing happens)
		self.add_collision_handler(player, asteroid, lambda x, y, z: False)


		### Set up debug draw mode ###

		draw_options = pymunk.pygame_util.DrawOptions(self.screen)
		self.background = pygame.Surface(size)
		self.background.fill(Color('white'))

		self.running = True
		while self.running:
			# refresh the screen
			self.screen.blit(self.background, (0, 0))
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False
			self.sprites.update()
			self.wrap_around(self.sprites,size)
			self.space.debug_draw(draw_options)			
			self.space.step(self.dt)
			self.clock.tick(self.fps)
			pygame.display.flip()
		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))