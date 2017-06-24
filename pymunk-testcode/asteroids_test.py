import sys, math
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk
from pymunk.vec2d import Vec2d
import pymunk.pygame_util

def radians_to_vector(angle):
	
	# if angle > math.pi:
	# 	angle = angle % (2 * math.pi )
	# elif angle < - math.pi:
	# 	angle = - (abs(angle) % math.pi)
	# while not (angle >= -math.pi and angle <= math.pi):
	# 	if angle > math.pi:
	# 		angle = angle - (2 * math.pi)
	# 	elif angle < -math.pi:
	# 		angle = angle + (2 * math.pi)

	return Vec2d((math.cos(angle) ,math.sin(angle)))

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
		self.shape = pymunk.Circle(self.body, self.radius)
		self.body.position = position
		# self.body_type = pymunk.Body.KINEMATIC
		self.shape.friction = 1.0
		print "initial forces:" + str(self.body.force)
		# set legal button presses
		self.legal_actions = [K_UP,K_DOWN,K_LEFT,K_RIGHT]

		# set rocket's forward and turning thrusts (as forces)
		self.forward_thrust = 20
		self.turning_speed = 0.05

		Sprite.__init__(self, self.body)

	def move(self, buttons_pressed):
		# up key applies forward force
		if K_UP in buttons_pressed and not K_DOWN in buttons_pressed:
			# thrust = Vec2d((math.cos(self.body.angle % (math.pi)) ,math.sin(self.body.angle % (math.pi)))) *  self.forward_thrust
			thrust = Vec2d(1, 0) *  self.forward_thrust
			print thrust
			self.body.apply_impulse_at_local_point(thrust, (0,0))

		# down key decreases velocity at flat rate
		elif K_DOWN in buttons_pressed and not K_UP in buttons_pressed:
			# decrease velocity
			self.body.velocity = self.body.velocity[0] * 0.9, self.body.velocity[1] * 0.9


		# right and left keys turn right and left, respectively, a fixed amount
		if K_RIGHT in buttons_pressed and not K_LEFT in buttons_pressed:
			self.body.angle += self.turning_speed
			# self.body.apply_impulse_at_local_point((self.turning_speed,0), (0,10))
			# print self.body.angle
			# print math.cos(self.body.angle) ,math.sin(self.body.angle)

		elif K_LEFT in buttons_pressed and not K_RIGHT in buttons_pressed:
			self.body.angle -= self.turning_speed
			# self.body.apply_impulse_at_local_point((-self.turning_speed,0), (0,10))
			# print self.body.angle
			# print math.cos(self.body.angle) ,math.sin(self.body.angle)



	def update(self):
		# get key press and apply action
		keys_pressed_binary = pygame.key.get_pressed()
		keys_pressed_list = []
		for key in self.legal_actions:
			if keys_pressed_binary[key]:
				keys_pressed_list.append(key)

		self.move(keys_pressed_list)
		# if  K_RIGHT in keys_pressed_list and not K_LEFT in keys_pressed_list:
		# 	self.body.angular_velocity = 0.
			


class Wall(Sprite):
	def __init__(self, position, size):
		"""
		creates a rectangle of the given size
		position is top left corner of the rectangle
		"""
		self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
		p = Vec2d(position)
		s = Vec2d(size)
		self.shape = pymunk.Poly(self.body, [(p.x, p.y), (p.x, p.y-s.y), (p.x+s.x, p.y-s.y), (p.x+s.x, p.y)])
		self.shape.friction = 1.
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

		### initialize display settings ###
		self.screen = pygame.display.set_mode(size)
		self.clock = pygame.time.Clock()
		self.fps = 60
		self.dt = 1./self.fps


		### Add objects to the game world ###

		# add player to the game world
		player = Player((300, 220))
		self.add_sprite(player)

		# add walls to the game world
	
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

			self.sprites.update()
			self.space.debug_draw(draw_options)			

			self.space.step(self.dt)
			self.clock.tick(self.fps)

			pygame.display.flip()
		pygame.display.quit()
		sys.exit()


if __name__ == '__main__':
	game = Game()
	game.run_game((600, 600))