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


collision_types = {
	"Player" : 1,
	"Asteroid" : 2,
	"Bullet": 3
}

"""
Sprite class that wraps around the screen, i.e. going off the screen teleports
you over to the other side.
"""
class WrapSprite(Sprite):	
	def passive_update(self, game):
		screen_width, screen_height = game.screen.get_size()
		x, y = self.body.position
		new_x = x % screen_width
		new_y = y % screen_height
		self.body.position = Vec2d(new_x, new_y)


class Player(WrapSprite):
	def __init__(self, position): 
		WrapSprite.__init__(self, position, (0, 0))
		"""
		Physical properties of ship.
		"""
		triangle_vertices = [(-5,5),(-5,-5),(5,0)] # vertices of triangular shape of ship
		mass = 1.0 # arbitrary
		self.gravity = Vec2d(0, 0) # no gravity
		self.body = pymunk.Body(mass=mass, moment=pymunk.moment_for_poly(mass,triangle_vertices), body_type=pymunk.Body.DYNAMIC)
		self.body.angle = math.pi / 2. # initialize facing up
		self.shape = pymunk.Poly(self.body, [(-5,5),(-5,-5),(5,0)]) # initialize trianglur shape
		self.body.position = position 
		self.shape.friction = 0.0 # arbitrary
		self.shape.collision_type = collision_types["Player"]
		self.shape.game_over = False # flag triggered by collision handler detecting ship was killed by asteroid
		
		# legal buttons for player actions
		self.legal_actions = [K_UP,K_DOWN,K_LEFT,K_RIGHT,K_SPACE]

		# tune rocket's forward  and turning speed
		self.forward_thrust = 20  # as an impulse
		self.turning_speed = 0.1 # as radians per step
 
	def active_update(self, game):
		self._move(game)

	"""
	Ends the game if the end_game flag is triggered (i.e. the player lost)
	"""
	def passive_update(self,game):
		super(Player,self).passive_update(game)
		if self.shape.game_over == True: 
			game.running = False

	"""
 	Applies player actions based on keyboard ipnut
 	"""
	def _move(self, game):
		# up key applies forward force
		if K_UP in game.keypress_events["KEY_HELD"] and not K_DOWN in game.keypress_events["KEY_HELD"]:
			self.body.apply_impulse_at_local_point((self.forward_thrust,0), (0,0))

		# down key decreases velocity by 10 %
		elif K_DOWN in game.keypress_events["KEY_HELD"] and not K_UP in game.keypress_events["KEY_HELD"]:
			self.body.velocity = self.body.velocity[0] * 0.9, self.body.velocity[1] * 0.9

		# right and left keys turn right and left, respectively, at a constant angle
		if K_RIGHT in game.keypress_events["KEY_HELD"] and not K_LEFT in game.keypress_events["KEY_HELD"]:
			self.body.angle -= self.turning_speed
		elif K_LEFT in game.keypress_events["KEY_HELD"] and not K_RIGHT in game.keypress_events["KEY_HELD"]:
			self.body.angle += self.turning_speed

		# space key shoots a bullet
		if K_SPACE in game.keypress_events["KEY_DOWN"]:
			bullet = Bullet(self.body.local_to_world(Vec2d(15,0)),self.body.rotation_vector)
			game.add_sprite(bullet)
			

class Asteroid(WrapSprite):
	def __init__(self, position, size):
		WrapSprite.__init__(self, position, size)
		# set physical properties
		radius = size[0]/2. # I'm using the first field in size as the radius of the circle (wtvr)
		self.gravity = Vec2d(0, 0)
		self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
		self.shape = pymunk.Circle(self.body, radius)
		self.shape.collision_type = collision_types["Asteroid"]
		self.shape.friction = 1.0
		self.body.velocity = random.randrange(-100,100), random.randrange(-100,100) # random directions and speed for each asteroid
		self.body.position = position
		self.shape.kill = False

	def passive_update(self,game): 
		# preserve the wrap-around effect from WrapSprite
		super(Asteroid,self).passive_update(game)

		# destroy asteroid if "hit by bullet" flag was triggered
		if self.shape.kill == True: 
			self.dead = True
			# game.space.remove(self.body)

			# spawn two smaller asteroids where the original was (up to a point)
			if self.size[0] > 20:
				child_asteroid1 = Asteroid(self.body.position, (self.size[0]/2,self.size[1]/2))
				child_asteroid2 = Asteroid(self.body.position, (self.size[0]/2,self.size[1]/2))
				game.add_sprite(child_asteroid1)
				game.add_sprite(child_asteroid2)


class Bullet(Sprite):
	def __init__(self, position, direction):
		bullet_size = (10,10)
		bullet_speed = 1000
		radius = bullet_size[0]/2

		Sprite.__init__(self,position,bullet_size)
		self.gravity = Vec2d(0, 0)
		self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
		self.body.position = position
		self.shape = pymunk.Circle(self.body, radius)
		self.shape.friction = 1.0
		self.shape.collision_type = collision_types["Bullet"]
		self.body.velocity = bullet_speed * direction
		self.shape.kill = False # death flag triggered when hits asteroid

	# destroys bullet when "hit asteroid" flag is raised
	def passive_update(self,game): 
		if self.shape.kill == True: 
			self.dead = True
			# game.space.remove(self.body)

"""
Collision handlers
"""
def kill_both_sprites(arbiter,space,data):
	for shape in arbiter.shapes:
		shape.kill = True
	return True

def end_game(arbiter,space,data):
	player_shape = arbiter.shapes[0] # assumes player is instantiated first
	player_shape.game_over = True
	return True

if __name__ == '__main__':
	game = Game((600, 600), debug_mode = True)

	"""
	Add objects to the game world
	"""
	# 1 player at the center
	player = Player((300, 300))
	game.add_sprite(player)

	# 5 asteroids at random places
	screen_width, screen_height = game.size
	for _ in range(5):
		random_position = random.randrange(0, screen_width), random.randrange(0, screen_height)
		random_size = (random.randrange(20,60),0) # second field is just 0 because only the first is used for the radius
		asteroid = Asteroid(random_position, random_size)
		game.add_sprite(asteroid)

	dummy_bullet = Bullet((0,0),Vec2d(1,0)) # used to pass into collision handlers
	
	"""
	Special collisions
	"""
	game.add_collision_handler(dummy_bullet,asteroid, kill_both_sprites)
	game.add_collision_handler(player,asteroid,end_game)

	"""
	Collisions we want to ignore
	"""
	# game.add_collision_handler(player, asteroid, lambda x, y, z: False)
	game.add_collision_handler(asteroid, asteroid, lambda x, y, z: False)
	game.add_collision_handler(player,  dummy_bullet, lambda x, y, z: False)
	game.add_collision_handler(dummy_bullet, dummy_bullet, lambda x, y, z: False)
	
	game.run_game()