import pygame
from typing import Callable
from random import randint
from settings import *
from sprites import *
from gui import Gui
from player import Player

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()

	def custom_draw(self, player: Player, sky: Sky, dt):
		offsetx = player.rect.centerx - SCREEN_WIDTH / 2
		offsety = player.rect.centery - SCREEN_HEIGHT / 2

		for layer in LAYERS.values():
			for sprite in pygame.sprite.spritecollide(player.blank, self, False):
				if sprite.z == layer:
					offset_rect = sprite.rect.copy()
					offset_rect.center = (offset_rect.centerx - offsetx, offset_rect.centery - offsety)
					self.display_surface.blit(sprite.image, offset_rect)
					sprite.update(dt, sky = sky)

class Level:
	def __init__(self, lang: str, win: Callable, lose: Callable):

		# Camera
		self.display_surface = pygame.display.get_surface()
		self.all_sprites = CameraGroup()

		# Lang
		self.lang = lang
		
		# Sprites
		self.sky = Sky(self.all_sprites)
		self.player = Player((640, 360), self.all_sprites)
		
		self.planet_count = randint(35, 40)
		self.planet_group = pygame.sprite.Group()
		self.station_group = pygame.sprite.Group()
		while len(self.planet_group) < self.planet_count:
			Planet(all_group = self.all_sprites, planet_group = self.planet_group, lang = self.lang)
		while len(self.station_group) < self.planet_count - 20:
			SpaceStation(all_group = self.all_sprites, planet_group = self.planet_group, station_group = self.station_group)
		SpaceStation(all_group = self.all_sprites, planet_group = self.planet_group, station_group = self.station_group, pos = (640, 360))

		# Gui
		self.gui = Gui(self.player, self.lang)

		# End func
		self.win = win
		self.lose = lose

	def run(self, dt: float):
		# Background
		self.display_surface.fill((16, 16, 44))

		# Sprites
		self.all_sprites.custom_draw(self.player, self.sky, dt)

		# Gui
		self.gui.display()

		# Map
		self.gui.map_update(
			planet_list = pygame.sprite.spritecollide(self.player.map, self.planet_group, False) + pygame.sprite.spritecollide(self.player.map, self.station_group, False),
			player = self.player
			)

		# Water remove and refill
		if pygame.sprite.spritecollide(self.player, self.station_group, False):
			self.player.water = self.player.water + 0.3 if self.player.water < 200 else 200
		else:
			self.player.water -= 2 * dt
		
		# Infobox
		if not pygame.sprite.spritecollide(self.player, self.planet_group, False):
			self.gui.info_offset = self.gui.info_offset + 15 if self.gui.info_offset < 602 else 602
		else:
			planet = pygame.sprite.spritecollide(self.player, self.planet_group, False)[0]
			planet.mark_index = 'after'
			self.player.planet_input(planet)
			self.gui.show_info(planet)

		# End
		if self.player.energy / self.player.people >= 2:
			self.win(f'{self.player.year:.1f}')
		elif self.player.water <= 0:
			self.lose(f'{self.player.year:.1f}')