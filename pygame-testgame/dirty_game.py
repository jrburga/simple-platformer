import pygame
from pygame.locals import *

# A game is an enviroment for which objects in the game can exist

class Sprite(pygame.sprite.DirtySprite):
	updates = 0
	def __init__(self, image):
		#initialize the class with the base class
		pygame.sprite.DirtySprite.__init__(self)
		self.size = 50
		try:
			self.image = pygame.image.load(image)
			self.image.convert()
			self.image = pygame.transform.scale(self.image, [self.size]*2)
		except:
			self.image = pygame.Surface([self.size]*2)
			self.image.fill((0, 0, 0))
		# print self.image
		self.speed = self.size
		# self.image.fill((255, 255, 255))

		self.keys = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
		self.rect = self.image.get_rect()

	def update(self, action):
		# for action in actions:
		if not action: return
		if action.key in self.keys:
			self.dirty = 1
			if action.key == K_UP:
				self.rect.y -= self.speed
			elif action.key == K_DOWN:
				self.rect.y += self.speed
			elif action.key == K_LEFT:
				self.rect.x -= self.speed
			elif action.key == K_RIGHT:
				self.rect.x += self.speed


class Game():
	def __init__(self):
		pass
		# self.screen = pygame.display.set_mode(())

	def run_game(self, screen_size, caption = 'Game'):
		pygame.init()
		self.screen = pygame.display.set_mode(screen_size)
		self.background = pygame.Surface(screen_size)
		self.background.fill((255, 255, 255))
		player = Sprite('images/apple.png')
		self.sprites = pygame.sprite.LayeredDirty()
		self.sprites.add(player)
		self.sprites.clear(self.screen, self.background)

		self.running = True
		self.clock = pygame.time.Clock()
		self.framerate = 1
		while self.running:
			self.clock.tick()
			action = None
			# print 'getting events'
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False
				if event.type == pygame.KEYDOWN:
					player.update(event)
			self.sprites.update(None)
			player.updates = 0
			dirty_rects = self.sprites.draw(self.screen)
			pygame.display.update(dirty_rects)

		pygame.display.quit()


game = Game()
game.run_game((600, 600))