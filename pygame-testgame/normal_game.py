import pygame
from pygame.locals import *
from sprite_sheet import SpriteSheet

# A game is an enviroment for which objects in the game can exist

class Sprite(pygame.sprite.Sprite):

	def __init__(self, image):
		#initialize the class with the base class
		pygame.sprite.Sprite.__init__(self)
		self.size = 50
		try:
			self.ss = SpriteSheet(image)
			self.image = self.ss.image_at((0, 0, 32, 32), (255, 0, 255))
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
	def update(self, actions):
		# if actions: print '----'
		# self.rect.y += 1

		for action in actions:
			if action.key in self.keys:
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
		self.background.fill((0, 0, 0))

		player = Sprite('images/goomba_sheet-1.png')

		self.sprites = pygame.sprite.Group()
		self.sprites.add(player)
		self.sprites.clear(self.screen, self.background)

		self.running = True
		self.clock = pygame.time.Clock()
		self.framerate = 30
		
		while self.running:
			self.clock.tick()
			self.screen.blit(self.background, (0, 0))
			actions = []
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False
				if event.type == pygame.KEYDOWN:
					actions.append(event)
			
			self.sprites.update(actions)
			player.updates = 0
			self.sprites.draw(self.screen)
			pygame.display.update()

		pygame.display.quit()


game = Game()
game.run_game((600, 600))