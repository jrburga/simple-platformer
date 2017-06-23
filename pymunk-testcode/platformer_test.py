import sys, math

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

from Graphics import SpriteSheets


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

	def update(self, game):
		self.pymunk2pygame(game.screen)

	def pymunk2pygame(self, screen):
		self.rect.x, self.rect.y = pymunk.pygame_util.to_pygame(self.body.position, screen)

class Player(Sprite):
	def __init__(self, position, size):
		Sprite.__init__(self, position, size)
		scale = [32, 48]
		self.animation = SpriteSheets.Animation('images/xmasgirl1.png', (32, 48), colorkey=None, scale=scale)
		self.animation.animate(2)
		self.image = self.animation.next()
		self.image.convert()
		self.size = scale
		# self.image = pygame.transform.scale(self.image, Vec2d(size)*3)
		self.faces = [None, pygame.transform.flip(self.image, True, False), self.image]
		self.gravity = Vec2d(0, -2000)
		self.mass = 5
		self.body = pymunk.Body(self.mass, pymunk.inf)
		self.shape = pymunk.Circle(self.body,size[0])
		self.head = pymunk.Circle(self.body, size[0], (0, 10))
		self.shape.collision_type = 1
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

		self.targetvx = 0
		self.direction = 1

	def get_bodies(self):
		return [self.body, self.shape, self.head]

	def ground_collision(self, arbiter):
		# checks the normal vector between the player and the object it's colliding with
		# if the slope is less than its coefficient of friction, it is grounded
		N = arbiter.contact_point_set.normal
		if arbiter.shapes[1].body:
			if (N.y != 0 and abs(N.x/N.y) < self.shape.friction):
				self.grounded = True

	def walk(self, direction):
		self.direction = direction
		if self.grounded:
			self.target_vx += direction*self.max_speed
			self.image = self.animation.next()
		



	def jump(self):
		# jump if the object is properly grounded
		# set grounded to False
		if self.grounded:
			self.grounded = False
			self.body.apply_impulse_at_local_point(Vec2d(0, self.jump_impulse))

	def update(self, game):

		# check if object is properly "grounded"
		self.body.each_arbiter(self.ground_collision)
		self.body.apply_force_at_local_point(self.gravity, (0, 0))

		self.target_vx = 0
		# self.shape.surface_velocity = Vec2d(0, 0)
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
		
		keys = pygame.key.get_pressed()
		for player_key in self.actions:
			if keys[player_key]:
				self.actions[player_key]()

		self.shape.surface_velocity = Vec2d(-self.target_vx, 0)

		self.pymunk2pygame(game.screen)
		self.rect.x -= self.size[0]/2
		self.rect.y -= self.size[1]/2+16



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

class KillBox(Platform):
	def __init__(self, position, size):
		Platform.__init__(self, position, size)
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


class MovingPlatform(Platform):

	# moves in a path relative to its position
	# where a path is a list of points
	def __init__(self, position, size, path, speed):
		Platform.__init__(self, position, size)
		self.body.position
		self.path = [Vec2d(point)+self.body.position for point in path]
		self.dest_index = 0
		self.destination = self.path[self.dest_index]
		self.speed = speed

	def update(self, game):
		current = self.body.position
		distance = current.get_distance(self.destination)
		if distance < self.speed:
			self.dest_index = (self.dest_index + 1)%len(self.path)
			self.destination = self.path[self.dest_index]
		if distance > 0:
			new = current.interpolate_to(self.destination, self.speed / distance)
			self.body.velocity = (new - current)/game.dt
		self.pymunk2pygame(game.screen)




class Game():
	def __init__(self):
		self.space = pymunk.Space()
		self.space.gravity = (0, 0)
		self.sprites = pygame.sprite.Group()

	def add_sprite(self, sprite):
		self.sprites.add(sprite)
		self.space.add(sprite.get_bodies())

	def remove_sprite(self, sprite):
		self.sprites.remove(sprite)
		self.space.remove(sprite.get_bodies())

	def add_collision_handler(self, sprite1, sprite2, collision_handler):
		type1 = sprite1.shape.collision_type
		type2 = sprite2.shape.collision_type
		self.space.add_collision_handler(type1, type2).begin = collision_handler

	def run_game(self, size):



		pygame.init()

		# initialize 
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps

		# add objects to the game world
		player = Player((300, 220), (5, 5))
		walls = []
		walls.append(Platform((100, 200), (400, 20)))
		walls.append(Platform((100, 400), (20, 200)))
		walls += [Platform((500, 200+y), (20, 20)) for y in xrange(0, 200, 20)]
		# walls.append(Platform((200, 220), (40, 20)))
		self.add_sprite(player)
		for wall in walls:
			self.add_sprite(wall)

		moving_platform = MovingPlatform((300, 260), (60, 10), [(-40, 0), (40, 0)], 1)
		self.add_sprite(moving_platform)

		kill_box = KillBox((350, 230), (30, 30))
		self.add_sprite(kill_box)

		color_box = ColorBox((200, 230), (30, 30))
		self.add_sprite(color_box)

		transform_box = TransformBox((120, 230), (30, 30), Platform)
		self.add_sprite(transform_box)

		# set up debug draw mode
		# actually displaying real graphics will take some more effort
		# because the (0, 0) point is in the bottom left (unlike the pygame screen)
		draw_options = pymunk.pygame_util.DrawOptions(self.screen)

		self.running = True

		# create a white background to refresh the screen
		self.background = pygame.Surface(size)
		self.background.fill(Color('white'))

		def kill_sprite(arbiter, space, data):
			arbiter.shapes[0].kill = True
			return True

		def change_color(arbiter, space, data):
			print arbiter
			arbiter.shapes[0].change = True
			return True

		def transform_sprite(arbiter, space, data):
			arbiter.shapes[0].transform = True
			return True

		self.add_collision_handler(kill_box, player, kill_sprite)
		self.add_collision_handler(color_box, player, change_color)
		self.add_collision_handler(transform_box, player, transform_sprite)

		while self.running:
			# refresh the screen
			self.screen.blit(self.background, (0, 0))
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False

			self.sprites.update(self)
			self.sprites.draw(self.screen)
					

			self.space.step(self.dt)
			self.clock.tick(self.fps)

			pygame.display.flip()
		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))