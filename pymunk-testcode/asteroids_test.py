import sys, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util
import random 

from Basics import Sprite
from Basics import Game
"""
TODO
- Bullets (key_press --> creation --> collision w/ asteroid --> destroy asteroid & create 2 a fraction of the size)
    * bullets shouldn't wrap around / should have a timer (check the game)
"""


class WrapSprite(Sprite):
	radius = 0

	def passive_update(self, game):
		screen_width, screen_height = game.screen.get_size()
		x, y = self.body.position.x, self.body.position.y
		new_x = x%(screen_width+0.0)
		new_y = y%(screen_height+0.0)
		self.body.position = Vec2d(new_x, new_y)


class Player(WrapSprite):
	def __init__(self, position, game):
		WrapSprite.__init__(self, position, (0, 0))
		# set physical properties of ship
		self.gravity = Vec2d(0, 0)
		self.mass = 1
		self.radius = 10
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass,0,self.radius),pymunk.Body.DYNAMIC)
		self.shape = pymunk.Poly(self.body, [(-5,0),(5,0),(0,10)])
		self.body.position = position
		self.shape.friction = 0.0
		
		# legal buttons for player actions
		self.legal_actions = [K_UP,K_DOWN,K_LEFT,K_RIGHT,K_SPACE]

		# tune rocket's forward and turning thrust
		self.forward_thrust = 500 # as an instantaneous force (impulse)
		self.turning_speed = 0.1 # as radians per step

		self.game = game

		

	def move(self, buttons_pressed, game):
		# up key applies forward force
		if K_UP in buttons_pressed and not K_DOWN in buttons_pressed:
			self.body.apply_force_at_local_point((0,self.forward_thrust), (0,0))

		# down key decreases velocity by 10%
		elif K_DOWN in buttons_pressed and not K_UP in buttons_pressed:
			self.body.velocity = self.body.velocity[0] * 0.9, self.body.velocity[1] * 0.9

		# right and left keys turn right and left, respectively, a constant amount
		if K_RIGHT in buttons_pressed and not K_LEFT in buttons_pressed:
			self.body.angle -= self.turning_speed
		elif K_LEFT in buttons_pressed and not K_RIGHT in buttons_pressed:
			self.body.angle += self.turning_speed

		# space shoots a bullet
		if K_SPACE in game.keypress_events["KEY_DOWN"]:
			bullet = Bullet(self.body.position,self.body.angle)
			game.add_sprite(bullet)

	def active_update(self, game):
		# get key press and apply action
		keys_pressed_binary = pygame.key.get_pressed()

		keys_pressed_list = []
		for key in self.legal_actions:
			if keys_pressed_binary[key]:
				keys_pressed_list.append(key)

		self.move(keys_pressed_list, game)
			
class Asteroid(WrapSprite):
	def __init__(self, position, size, velocity):
		WrapSprite.__init__(self, position, size)
		# set physical properties
		self.gravity = Vec2d(0, 0)
		self.mass = 5
		self.radius = size[0]/2
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass,0,self.radius),pymunk.Body.KINEMATIC)
		self.shape = pymunk.Circle(self.body, self.radius)
		self.shape.friction = 1.0
		self.body.velocity = velocity
		self.body.position = position


class Bullet(Sprite):
	def __init__(self, position, angle):
		bullet_size = 10,10
		bullet_speed = 100000
		
		Sprite.__init__(self,position,bullet_size)
		self.gravity = Vec2d(0, 0)
		self.mass = 5
		self.radius = bullet_size[0]/2
		self.body = pymunk.Body(self.mass, pymunk.moment_for_circle(self.mass,0,self.radius),pymunk.Body.KINEMATIC)
		self.body.position = position
		self.shape = pymunk.Circle(self.body, self.radius)
		self.shape.friction = 1.0
		self.image.fill((200, 100, 50))
		self.body.velocity = self.angle_to_velocity(bullet_speed,angle)

	def angle_to_velocity(self,angle,speed):
		return speed * pymunk.Vec2d.normalized(Vec2d(math.cos(angle), math.sin(angle)))
	
	# def passive_update(self):


if __name__ == '__main__':
	game = Game((600, 600), debug_mode = True)

	### Add objects to the game world ###

	# add player to the game world
	player = Player((300, 220),game)
	player.body.filter = pymunk.ShapeFilter(categories=1)
	game.add_sprite(player)

	# # add 5 asteroids
	# for _ in range(5):
	# 	random_position = random.randrange(0, game.size[0]), random.randrange(0, game.size[1])
	# 	random_velocity = random.randrange(-100,100), random.randrange(-100,100)
	# 	random_size = [random.randrange(20,60)]*2
	# 	asteroid = Asteroid(random_position, random_size, random_velocity)
	# 	asteroid.body.filter = pymunk.ShapeFilter(categories=2)
	# 	game.add_sprite(asteroid)

	# add player-asteroid collision handler (nothing happens)
	# game.add_collision_handler(player, asteroid, lambda x, y, z: False)
	game.run_game()