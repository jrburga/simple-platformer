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

from platformer_test import *
from asteroids_test import WrapSprite

class AppearingPlatforms():
	def __init__(self, position_size_list):
		self.platforms = []
		for position, size in position_size_list:
			self.platforms.append(Platform(position, size))


	


def kill_sprite(arbiter, space, data):
	if pass_through(arbiter, space, data):
		arbiter.shapes[0].body.kill = True
		space.remove(arbiter.shapes[0])
		return True
	return False

if __name__ == '__main__':
	game = Game((600, 600))

	game.background.fill((0x00, 0x18, 0x7C))

	player = Player((300, 300), (5, 5))
	player.body.mass = 2.5
	player.max_speed = 100.
	game.add_sprite(player, 0)

	ground = PassThrough((200, 300), (200, 20))
	ground.image.fill(((0xDC, 0xDC, 0xDC)))
	game.add_sprite(ground, 1)

	floes = [
		MovingPlatform((200, 250), (100, 10), [(0, 0), (100, 0)], 50),
		MovingPlatform((300, 200), (100, 10), [(0, 0), (-100, 0)], 50),
		MovingPlatform((200, 150), (100, 10), [(0, 0), (100, 0)], 50)
		]
	for floe in floes:
		floe.image.fill((0xDC, 0xDC, 0xDC))
		game.add_sprite(floe, 1)

	kill_water = [
		MovingPlatform((100, 250), (100, 10), [(0, 0), (100,0)], 50),
		MovingPlatform((300, 250), (100, 10), [(0, 0), (100,0)], 50),
		MovingPlatform((200, 200), (100, 10), [(0, 0), (-100,0)], 50),
		MovingPlatform((400, 200), (100, 10), [(0, 0), (-100,0)], 50),
		MovingPlatform((100, 150), (100, 10), [(0, 0), (100,0)], 50),
		MovingPlatform((300, 150), (100, 10), [(0, 0), (100,0)], 50)
	]

	for water in kill_water:
		# water.image.fill((0x00, 0x18, 0x7C))
		water.shape.collision_type = 10
		game.add_sprite(water, 1 )

	igloo = AppearingPlatforms([
			((330, 310), (20, 10))
		])

	for part in igloo.platforms:
		game.add_sprite(part, 1)



	game.add_collision_handler(player, floes[0], pass_through)
	game.add_collision_handler(player, kill_water[0], kill_sprite)


	game.run_game()