import sys, math

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

from Graphics import SpriteSheets

from Basics import Game
from Basics import Sprite


class InteractBox(Sprite):
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		# moment = pymunk.moment_for_poly(5, map(lambda p: Vec2d(p), [(0, 0), (0, -size.y), (size.x, -size.y), (size.x, 0)]))
		self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
		self.image.fill((200, 100, 50))
		self.body.mass = 5
		self.body.moment = pymunk.inf
		self.body.position = Vec2d(position)
		size = Vec2d(size)
		self.shape = pymunk.Poly(self.body, [(0, 0), (0, -size.y), (size.x, -size.y), (size.x, 0)], radius=1)
		self.shape.friction = 1.0
		self.shape.elasticity = 1
		self.gravity = Vec2d(0, -1000)
		self.shape.collision_type = 10

	def passive_update(self, game):
		force = self.body.mass*self.gravity
		self.body.apply_force_at_local_point(force, (0, 0))


class Player(Sprite):
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		scale = [32, 48]
		self.animation = SpriteSheets.Animation('images/xmasgirl1.png', (32, 48), colorkey=None, scale=scale)
		self.animation.animate(2)

		self.image = self.animation.next()
		self.image.convert()

		self.size = scale
		self.gravity = Vec2d(0, -1000) # an acceleration of some sort?

		self.body = pymunk.Body(3, pymunk.inf)
		self.shape = pymunk.Circle(self.body,size[0])
		self.shape.name = 'feet'
		self.head = pymunk.Circle(self.body, size[0]*2, (0, 25))
		self.head.friction = 0
		self.torso = pymunk.Circle(self.body, size[0]*1.5, (0, 10))
		self.torso.friction = 0
		self.shape.collision_type, self.head.collision_type, self.torso.collision_type = 1, 1, 1
		self.body.position = position
		

		self.actions = {
			K_LEFT: lambda: self.walk(-1),
			K_RIGHT: lambda: self.walk(1),
			K_UP: lambda: self.jump()
		}


		self.max_speed = 100*2.
		self.accel_time = 0.05
		self.accel = (self.max_speed/self.accel_time)

		self.shape.friction = -self.accel/self.gravity.y
		self.grounded = False
		self.jump_impulse = 800
		self.air_speed_max = 10000
		self.air_speed = self.air_speed_max

		self.targetvx = 0
		self.direction = 1
		self.body.passing = False

	def get_bodies(self):
		return [self.body, self.shape, self.head, self.torso]

	def ground_collision(self, arbiter):
		# checks the normal vector between the player and the object it's colliding with
		# if the slope is less than its coefficient of friction, it is grounded
		for shape in arbiter.shapes:
			if 'name' in shape.__dict__:
				N = arbiter.contact_point_set.normal
				if arbiter.shapes[1].body:
					if (N.y != 0 and abs(N.x/N.y) < self.shape.friction):
						self.grounded = True
						self.body.passing = False
						self.air_speed = self.air_speed_max
				return
		

	def walk(self, direction):
		self.direction = direction
		if self.grounded:
			self.target_vx += direction*self.max_speed
			self.image = self.animation.next()
		else:
			nv = self.body.velocity.x+direction*self.air_speed
			if abs(nv) <= self.air_speed_max or abs(nv) <= self.body.velocity.x:
				self.body.apply_force_at_local_point(Vec2d(direction*self.air_speed, 0), (0, 0))
				# self.air_speed *= .5
		

	def jump(self):
		# jump if the object is properly grounded
		# set grounded to False
		if self.grounded:
			self.grounded = False
			self.body.apply_impulse_at_local_point(Vec2d(0, self.jump_impulse))

	def passive_update(self, game):
		force = self.body.mass*self.gravity
		self.body.apply_force_at_local_point(force, (0, 0))
		self.body.each_arbiter(self.ground_collision)

	def animate(self):
		self.image = self.animation.default()

		if self.direction == -1:
			if self.grounded:
				self.animation.animate(1)
			else:
				self.image = self.animation.sprite_sheet.image((1, 1))
		else:
			if self.grounded:
				self.animation.animate(2)
			else:
				self.image = self.animation.sprite_sheet.image((1, 2))

	def active_update(self, game):
		self.target_vx = 0
		keys = pygame.key.get_pressed()
		for player_key in self.actions:
			if keys[player_key]:
				self.actions[player_key]()

		self.shape.surface_velocity = Vec2d(-self.target_vx, 0)

	def update(self, game):

		# check if object is properly "grounded"
		self.passive_update(game)
		self.animate()
		self.active_update(game)
		self.pymunk2pygame(game.screen)
		self.rect.x -= self.size[0]/2
		self.rect.y -= self.size[1]/2+16

class PreciseJumper(Player):
	gravity = Vec2d(0, 0)
	def __init__(self, position, size):
		Player.__init__(self, position, size)
		self.jump_impulse = 500
		self.jump_direction = 0
		self.jumping = False
		self.jump_time = 0
		self.jump_time_max = 30
		self.jump_speed = 200
		# self.gravity = Vec2d(0, 0)
	def ground_collision(self, arbiter):
		# checks the normal vector between the player and the object it's colliding with
		# if the slope is less than its coefficient of friction, it is grounded
		N = arbiter.contact_point_set.normal
		for shape in arbiter.shapes:
			if 'name' in shape.__dict__:
				if arbiter.shapes[1].body:
					if (N.y != 0 and abs(N.x/N.y) < self.shape.friction):
						self.grounded = True
						self.body.passing = False
				return
		else:
			if abs(N.x) == 1:
				self.jump_direction = 0
	def jump(self):

		if self.grounded:
			self.grounded = False
			self.jumping = True
			self.jump_time = 0
			self.jump_direction = self.body.velocity.normalized().x
			self.body.apply_impulse_at_local_point(Vec2d(0, self.jump_impulse))

	def passive_update(self):
		self.body.each_arbiter(self.ground_collision)
		if self.grounded:
			self.body.apply_force_at_local_point(self.gravity, (0, 0))
		elif self.jumping:
			direction = 1
			self.jump_time += 1
			if self.jump_time >= self.jump_time_max/2:
				if self.jump_time >= self.jump_time_max:
					self.jumping = False
				else:
					direction = -1
			self.body.velocity = Vec2d(self.jump_direction*self.jump_speed, direction*self.jump_speed)
		else:
			self.body.velocity = Vec2d(0, -self.jump_speed)


class Platform(Sprite):
	# creates a rectangle of the given size
	# position is top left corner of the rectangle
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
		self.body.position = Vec2d(position)
		size = Vec2d(size)
		self.shape = pymunk.Poly(self.body, [(0, 0), (0, -size.y), (size.x, -size.y), (size.x, 0)])
		self.shape.friction = 1.
		self.shape.collision_type = 2


class PassThrough(Platform):
	def __init__(self, position, size):
		Platform.__init__(self, position, size)
		self.image.fill((255, 255, 0))
		self.shape.collision_type = 6


class KillBox(Platform):
	def __init__(self, position, size):
		Platform.__init__(self, position, size)
		self.image.fill((50, 100, 200))
		self.shape.kill = False
		self.shape.collision_type = 3
	def update(self, game):
		self.pymunk2pygame(game.screen)
		if self.shape.kill:
			self.dead = True
			game.remove_sprite(self)

class ColorBox(Platform):
	def __init__(self, position, size):
		Platform.__init__(self, position, size)
		self.color = 0
		self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
		self.image.fill((255, 0, 0))
		self.shape.collision_type = 4
		self.shape.change = False

	def update(self, game):
		self.pymunk2pygame(game.screen)
		if self.shape.change:
			self.color = (self.color + 1)%len(self.colors)
			self.image.fill(self.colors[self.color])
			self.shape.change = False

class TransformBox(Platform):
	def __init__(self, position, size, TransformSprite):
		Platform.__init__(self, position, size)
		self.image.fill((0, 255, 255))
		pygame.draw.rect(self.image, (255, 255, 0), [size[0]/4, size[1]/4, size[0]/2, size[1]/2])
		self.TransformSprite = TransformSprite
		self.shape.transform = False

	def update(self, game):
		
		if self.shape.transform:
			self.dead = True
			game.remove_sprite(self)
			new_sprite = self.TransformSprite(self.body.position, self.size)
			new_sprite.update(game)
			game.add_sprite(new_sprite)
		self.pymunk2pygame(game.screen)


class MovingPlatform(PassThrough):

	# moves in a path relative to its position
	# where a path is a list of points
	def __init__(self, position, size, path, speed):
		PassThrough.__init__(self, position, size)
		self.body.position
		self.path = [Vec2d(point)+self.body.position for point in path]
		self.dest_index = 0
		self.destination = self.path[self.dest_index]
		self.set_direction()
		self.speed = speed

	def set_direction(self):
		self.direction = self.destination-self.body.position
		self.direction = self.direction.normalized()

	def next_destination(self):
		self.dest_index = (self.dest_index + 1)%len(self.path)
		self.set_direction()
		return self.path[self.dest_index]


	def passive_update(self, game):
		current = self.body.position
		distance = current.get_distance(self.destination)

		# print distance, self.body.velocity.length
		if distance <= 1:
			self.destination = self.next_destination()
			self.set_direction()
		self.body.velocity = self.speed*self.direction

class PhysicsBox(Platform):
	def __init__(self, position, size):
		Platform.__init__(self, position, size)
		self.image.fill((100, 100, 100))
		self.shape.collision_type = 5

if __name__ == '__main__':
	game = Game((600, 600))
	# add objects to the game world
	# player = PreciseJumper((300, 220), (5, 5))
	player = Player((300, 220), (5, 5))
	game.add_sprite(player)


	walls = []
	walls.append(Platform((100, 200), (400, 20)))
	walls.append(Platform((100, 400), (180, 20)))
	walls.append(Platform((320, 400), (200, 20)))
	walls.append(Platform((100, 500), (20, 300)))
	walls.append(Platform((100, 500), (400, 20)))
	walls += [Platform((500, 200+y), (20, 20)) for y in xrange(0, 200, 20)]
	# walls.append(Platform((200, 220), (40, 20)))
	
	for wall in walls:
		game.add_sprite(wall)

	pass_through_platform = PassThrough((280, 400), (40, 20))
	game.add_sprite(pass_through_platform, 1)

	pass_through_platform2 = PassThrough((400, 260), (40, 60))
	game.add_sprite(pass_through_platform2, 1)

	moving_platforms = [
		# MovingPlatform((300, 260), (60, 10), [(-40, 0), (40, 0)], 1),
		MovingPlatform((300, 320), (60, 10), [(60, 0), (-60, 0), (0, -30)], 50),	
	]
	for moving_platform in moving_platforms:
		game.add_sprite(moving_platform, 1)

	kill_box = KillBox((400, 490), (20, 90))
	game.add_sprite(kill_box, 1)

	color_box = ColorBox((200, 230), (30, 30))
	game.add_sprite(color_box, 1)

	transform_box = TransformBox((120, 230), (30, 30), Platform)
	game.add_sprite(transform_box, 1)

	physics_box = PhysicsBox((470, 230), (30, 30))
	game.add_sprite(physics_box, 1)

	box = InteractBox((200, 440), (30, 30))
	game.add_sprite(box)

	# set up debug draw mode
	# actually displaying real graphics will take some more effort
	# because the (0, 0) point is in the bottom left (unlike the pygame screen)

	game.running = True
	def kill_sprite(arbiter, space, data):
		arbiter.shapes[0].kill = True
		return True

	def change_color(arbiter, space, data):
		arbiter.shapes[0].change = True
		return True

	def transform_sprite(arbiter, space, data):
		arbiter.shapes[0].transform = True
		return True

	def change_physics(arbiter, space, data):
		arbiter.shapes[0].body.mass = 2
		return True

	def pass_through(arbiter, space, data):
		N = arbiter.contact_point_set.normal
		shape1, shape2 = arbiter.shapes
		if shape2.body.position.y <= shape1.body.position.y and abs(N.x/N.y) < shape1.friction:
			return True
		return False

	game.add_collision_handler(kill_box, box, kill_sprite)
	game.add_collision_handler(color_box, player, change_color)
	game.add_collision_handler(transform_box, player, transform_sprite)
	game.add_collision_handler(player, physics_box, change_physics)
	game.add_collision_handler(player, pass_through_platform, pass_through)
	game.add_collision_handler(box, pass_through_platform, pass_through)


	game.run_game()