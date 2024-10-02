import pygame
from sys import exit
from settings import *
from level import Level
from menu import Menu
from story import Story

class Game:
	def __init__(self):
		
		# Pygame init
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
		pygame.display.set_icon(pygame.image.load('./assets/textures/icon.png').convert_alpha())
		pygame.display.set_caption('LittleAstronaut')
		self.clock = pygame.time.Clock()

		# Langs
		self.langs = ['Chinese', 'English']

		# Music
		pygame.mixer.music.load('./assets/music.mp3')
		pygame.mixer.music.set_volume(0.6)

		# Story
		self.story = Story(self.story_end)
		self.in_story = True
		
		# Menu
		self.menu = Menu(self.langs, self.start, self.level_reset)
		self.in_menu = False

		# Level
		self.level_reset()
	
	def story_end(self):
		del self.story
		self.in_menu = True
		self.in_story = False
		pygame.mixer.music.stop()
		pygame.mixer.music.play(-1)

	def level_reset(self):

		# Level in different lang
		self.level_list = []
		for lang in self.langs:
			self.level_list.append(
				Level(
					lang = lang,
					win = self.win,
					lose = self.lose
			)
		)
		
		# Menu continue timer
		self.menu.result_continue_timer.activate()

	def start(self):
		for level in self.level_list:
			if self.menu.lang[self.menu.lang_index] == level.lang:
				self.level = level
		self.in_menu = False
		pygame.mixer.music.stop()
		pygame.mixer.music.play(-1)
	
	def win(self, year):
		self.menu.end('win', year)
		self.in_menu = True
		pygame.mixer.music.stop()
		pygame.mixer.music.play(-1)
	
	def lose(self, year):
		self.menu.end('lose', year)
		self.in_menu = True
		pygame.mixer.music.stop()
		pygame.mixer.music.play(-1)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					exit()

			# Run
			if self.in_menu:
				self.menu.run()
			elif self.in_story:
				self.story.run()
			else:
				dt = self.clock.tick() / 1000
				self.level.run(dt)
				# print(f"{self.clock.get_fps():.0f}") ## Show fps
			
			# Display
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()