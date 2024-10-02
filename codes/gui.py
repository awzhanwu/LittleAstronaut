import pygame
from settings import *

class Textbox:
	def __init__(self, texts: list[str], lang: str = 'Chinese', size: int = 20, color: tuple | str = 'black'):
		self.size = size
		self.color = color
		self.update(texts, lang)
	
	def update(self, texts: list[str], lang: str = 'Chinese'):
		# Translate dict
		for key in LANGUAGE:
			if key == lang:
				lang_dict = LANGUAGE[f'{key}']

		# Translate
		text_translated = ''
		for text in texts:
			try:
				text_translated += lang_dict[f'{text}']
			except:
				text_translated += text
		
		# Display
		self.image = pygame.font.Font('./assets/fonts/simkai.ttf', self.size).render(text_translated, True, self.color)

class Gui:
	def __init__(self, player: pygame.sprite.Sprite, lang: str = 'Chinese'):
		# Input
		self.display_surface = pygame.display.get_surface()
		self.player = player
		self.path = './assets/textures/gui'

		# Attribute
		self.gui_surf = pygame.image.load(f'{self.path}/attr.png').convert_alpha()
		self.water_surf = pygame.image.load(f'{self.path}/water.png').convert_alpha()
		self.energy = Textbox(f'{self.player.energy}', size = 15)
		self.people = Textbox(f'{self.player.people:.0f}', size = 15)
		self.year = Textbox(f'{self.player.year:.0f}', size = 15)

		# Info
		self.info_surf = pygame.image.load(f'{self.path}/info/{lang}/info.png').convert_alpha()
		self.button_left = {
			'on': pygame.image.load(f'{self.path}/info/{lang}/button_left_on.png').convert_alpha(),
			'off': pygame.image.load(f'{self.path}/info/{lang}/button_left_off.png').convert_alpha()
		}
		self.button_right = {
			'on': pygame.image.load(f'{self.path}/info/{lang}/button_right_on.png').convert_alpha(),
			'off': pygame.image.load(f'{self.path}/info/{lang}/button_right_off.png').convert_alpha()
		}
		self.button_index = {
			'left': 'on',
			'right': 'on'
		}
		self.info_offset = 602

		# Map
		self.map_up = pygame.image.load(f'{self.path}/map_up.png').convert_alpha()
		self.map_down = pygame.image.load(f'{self.path}/map_down.png').convert_alpha()

	def display(self):
		# Attribute
		self.display_surface.blit(self.water_surf, self.water_surf.get_rect(right = SCREEN_WIDTH, bottom = SCREEN_HEIGHT + 57 - (self.player.water / (200 / 57))))
		self.display_surface.blit(self.gui_surf, self.gui_surf.get_rect(right = SCREEN_WIDTH, bottom = SCREEN_HEIGHT))
		self.display_surface.blit(self.energy.image, self.energy.image.get_rect(right = SCREEN_WIDTH - 98, bottom = SCREEN_HEIGHT - 37))
		self.display_surface.blit(self.people.image, self.people.image.get_rect(right = SCREEN_WIDTH - 98, bottom = SCREEN_HEIGHT - 7))
		self.year.update(f'{self.player.year:.0f}')
		self.display_surface.blit(self.year.image, self.year.image.get_rect(right = SCREEN_WIDTH - 193 if self.player.year <= 99 else SCREEN_WIDTH - 185, bottom = SCREEN_HEIGHT - 11))

		# Info
		self.info_rect = self.info_surf.get_rect(right = SCREEN_WIDTH + self.info_offset, centery = SCREEN_HEIGHT / 2)
		self.display_surface.blit(self.info_surf, self.info_rect)
		self.display_surface.blit(self.button_left[self.button_index['left']], self.info_rect)
		self.display_surface.blit(self.button_right[self.button_index['right']], self.info_rect)

	def show_info(self, planet: pygame.sprite.Sprite):
		# Attribute
		self.energy.update(f'{self.player.energy}')
		self.people.update(f'{self.player.people:.0f}')

		# Button
		self.button_index['left'] = 'off' if planet.attribute['energy_level'] == 0 or planet.migrated == True else 'on'
		self.button_index['right'] = 'off' if planet.migrated == True else 'on'

		# Info come into
		self.info_offset = self.info_offset - 15 if self.info_offset > 0 else 0
		texty_offset = 2
		for text in planet.text_box:
			self.display_surface.blit(text.image, text.image.get_rect(left = self.info_rect.left + 60, centery = SCREEN_HEIGHT / 2 + 15 - texty_offset * 50))
			texty_offset -= 1

	def map_update(self, planet_list: list[pygame.sprite.Sprite], player: pygame.sprite.Sprite):
		self.display_surface.blit(self.map_down, self.map_down.get_rect(left = 0, bottom = SCREEN_HEIGHT))
		for planet in planet_list:
			offsetx = (planet.rect.centerx - player.rect.centerx) / 20
			offsety = (planet.rect.centery - player.rect.centery) / 20
			self.display_surface.blit(planet.mark[f'{planet.mark_index}'], planet.mark[f'{planet.mark_index}'].get_rect(center = (94 + offsetx , SCREEN_HEIGHT + offsety - 80)))
		self.display_surface.blit(self.map_up, self.map_up.get_rect(left = 0, bottom = SCREEN_HEIGHT))