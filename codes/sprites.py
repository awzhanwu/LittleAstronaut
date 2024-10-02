import pygame
from random import randint, choices
from settings import *
from gui import Textbox
from timer import AnimateTimer

class Generic(pygame.sprite.Sprite):
	def __init__(self, pos, surf: pygame.surface.Surface, groups: list[pygame.sprite.Group] | pygame.sprite.Group, z = LAYERS['main']):
		super().__init__(groups)
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)
		self.z = z

class Sky(pygame.sprite.Group):
	def __init__(self, groups: list[pygame.sprite.Group] | pygame.sprite.Group):
		super().__init__()

		for x in range(-1, 2):
			for y in range(-1, 2):
				self.add(Generic(
				pos = (x * SCREEN_WIDTH, y * SCREEN_HEIGHT),
				surf = pygame.image.load('./assets/textures/sky.png').convert_alpha(),
				groups = groups, 
				z = LAYERS['sky']
				))

		self.set_up()

	def set_up(self):
		for sprite in self.sprites():
			sprite.pos_as = (sprite.rect.topleft[0] / SCREEN_WIDTH, sprite.rect.topleft[1] / SCREEN_HEIGHT)
			if sprite.pos_as == (1, 1):
				sprite.name = 'bottom_right'
			elif sprite.pos_as == (0, 1):
				sprite.name = 'bottom'
			elif sprite.pos_as == (1, 0):
				sprite.name = 'right'
			elif sprite.pos_as == (0, 0):
				sprite.name = 'middle'
			elif sprite.pos_as == (-1, 0):
				sprite.name = 'left'
			elif sprite.pos_as == (-1, -1):
				sprite.name = 'top_left'
			elif sprite.pos_as == (0, -1):
				sprite.name = 'top'
			elif sprite.pos_as == (1, -1):
				sprite.name = 'top_right'
			elif sprite.pos_as == (-1, 1):
				sprite.name = 'bottom_left'

	def move(self, offset):
		for sprite in self.sprites():
			sprite.pos_as = (sprite.pos_as[0] + offset[0], sprite.pos_as[1] + offset[1])
			sprite.rect = sprite.image.get_rect(topleft = (sprite.pos_as[0] * SCREEN_WIDTH, sprite.pos_as[1] * SCREEN_HEIGHT))

class SpaceStation(Generic):
	def __init__(self, all_group: pygame.sprite.Group, planet_group: pygame.sprite.Group, station_group: pygame.sprite.Group, pos: tuple[int] = None):
		pos = pos if pos else (randint(-5000, 5000), randint(-5000, 5000))
		self.original_image = pygame.image.load(f'./assets/textures/planet/station.png').convert_alpha()
		super().__init__(
			pos = pos,
			surf = self.original_image,
			groups = all_group,
			z = LAYERS['planet']
		)

		# Prevent collide other planets or stations
		if planet_group != None and station_group != None:
			pygame.sprite.spritecollide(self, planet_group, True)
			pygame.sprite.spritecollide(self, station_group, True)
			self.add(station_group)
		# Angle for rotating
		self.angle = 0
		# Mark in map
		self.mark = {'station': pygame.image.load(f'./assets/textures/planet/mark/yellow.png').convert_alpha()}
		self.mark_index = 'station'

	def update(self, dt: int = None, sky: Sky = None):
		self.angle += 0.1
		self.image = pygame.transform.rotate(self.original_image, self.angle)
		self.rect = self.image.get_rect(center = self.rect.center)

class Planet(Generic):
	def __init__(self, all_group: pygame.sprite.Group, planet_group: pygame.sprite.Group, lang: str, seed: str = None):
		self.path = './assets/textures/planet'

		# Spawn
		if seed:
			if not self.translate(seed):
				self.spawn()
				### Here need a textbox to show the seed is wrong ###
		else:
			self.spawn()
		super().__init__(
			pos = (self.attribute['posx'],self.attribute['posy']),
			surf = self.check_image(),
			groups = all_group,
			z = LAYERS['planet']
		)
		self.lang = lang
		self.textbox(self.lang)
		self.migrate_level = self.check_migrate()

		# Prevent collide other planets
		if planet_group != None:
			pygame.sprite.spritecollide(self, planet_group, True)
			self.add(planet_group)
		# Angle for rotating
		self.angle = 0
		# Migrated
		self.migrated = False
		# Mark in map
		self.mark = {
			'before': pygame.image.load(f'{self.path}/mark/blue.png').convert_alpha(),
			'after': pygame.image.load(f'{self.path}/mark/green.png').convert_alpha()
		}
		self.mark_index = 'before'

	def spawn(self):	
		# Attribute
		self.attribute = {
			'radiation': randint(1, 30),
			'gravitation': randint(1, 30),
			'atmosphere': randint(1, 30),
			'energy_level': int(choices([0, 1, 2, 3, 4], weights = [2, 2, 2, 2, 1])[0]),
			'life': int(choices([0, 1], weights = [8, 2])[0]),
			'volume': int(choices([1, 2, 3], weights = [5, 5, 3])[0]),
			'posx': randint(-5000, 5000),
			'posy': randint(-5000, 5000)
		}

		# Seed translate and save
		self.seed = ''
		for key in self.attribute:
			if key == 'radiation' or key == 'gravitation' or key == 'atmosphere':
				self.seed += str(self.attribute[key]).zfill(2)
			elif key == 'posx' or key == 'posy':
				self.seed += str(self.attribute[key]).zfill(5)
			else:
				self.seed += str(self.attribute[key])
		self.seed = str(hex(int(self.seed.replace('-', '9'))))

	def translate(self, seed: str) -> bool:
		try:
			seed_10 = str(int(str(seed), 16)).zfill(19)
			if seed_10[9] == '9':
				seed_10 = seed_10[:9] + '-' + seed_10[10:]
			if seed_10[14] == '9':
				seed_10 = seed_10[:14] + '-' + seed_10[15:]
				
			self.attribute = {
				'radiation': int(seed_10[0:2]),
				'gravitation': int(seed_10[2:4]),
				'atmosphere': int(seed_10[4:6]),
				'energy_level': int(seed_10[6]),
				'life': int(seed_10[7]),
				'volume': int(seed_10[8]),
				'posx': int(seed_10[9:14]),
				'posy': int(seed_10[14:])
			}
			self.seed = seed
			return True
		except:
			return False
	
	def check_image(self) -> pygame.surface.Surface:
		self.timer = None
		while not self.timer:
			if self.attribute['radiation'] <= 5 and self.attribute['volume'] >= 2:
				self.timer = AnimateTimer(f"{self.path}/sun/Uranus", 1600)
				self.sketch = 'planet.sketch.Uranus'
			elif self.attribute['radiation'] <= 10 and self.attribute['volume'] >= 2:
				self.timer = AnimateTimer(f"{self.path}/sun/Neptune", 1600)
				self.sketch = 'planet.sketch.Neptune'
			elif self.attribute['radiation'] < 20 and self.attribute['radiation'] > 10 and self.attribute['gravitation'] >= 20 and self.attribute['volume'] == 3:
				self.timer = AnimateTimer(f"{self.path}/sun/Jupiter", 1600)
				self.sketch = 'planet.sketch.Jupiter'
			elif (self.attribute['radiation'] >= 20 or self.attribute['radiation'] <= 10) and self.attribute['volume'] == 1:
				self.timer = AnimateTimer(f"{self.path}/sun/Mercury", 1600)
				self.sketch = 'planet.sketch.Mercury'
			elif self.attribute['atmosphere'] <= 10 and self.attribute['radiation'] <= 15 and self.attribute['volume'] == 2:
				self.timer = AnimateTimer(f"{self.path}/sun/Mars", 1600)
				self.sketch = 'planet.sketch.Mars'
			elif self.attribute['radiation'] >= 20 and self.attribute['gravitation'] >= 20 and self.attribute['volume'] == 2:
				self.timer = AnimateTimer(f"{self.path}/sun/Venus", 1600)
				self.sketch = 'planet.sketch.Venus'
			elif self.attribute['life'] == 1 and self.attribute['radiation'] <= 15 and self.attribute['gravitation'] <= 5:
				self.timer = AnimateTimer(f"{self.path}/type5/v{self.attribute['volume']}", 1600)
				self.sketch = 'planet.sketch.life'
			elif self.attribute['radiation'] <= 20 and self.attribute['gravitation'] <= 10 and self.attribute['energy_level'] >= 3:
				self.timer = AnimateTimer(f"{self.path}/type6/v{self.attribute['volume']}", 1600)
				self.sketch = 'planet.sketch.soft'
			elif self.attribute['radiation'] <= 10 and self.attribute['atmosphere'] >= 20:
				self.timer = AnimateTimer(f"{self.path}/type1/v{self.attribute['volume']}", 1600)
				self.sketch = 'planet.sketch.snow'
			elif self.attribute['energy_level'] >= 4 and self.attribute['life'] == 0:
				self.timer = AnimateTimer(f"{self.path}/type2/v{self.attribute['volume']}", 1600)
				self.sketch = 'planet.sketch.red_far'
			elif self.attribute['atmosphere'] >= 10 and self.attribute['atmosphere'] <= 20:
				self.timer = AnimateTimer(f"{self.path}/type3/v{self.attribute['volume']}", 1600)
				self.sketch = 'planet.sketch.ocean'
			elif self.attribute['radiation'] >= 20 and self.attribute['energy_level'] >= 3:
				self.timer = AnimateTimer(f"{self.path}/type4/v{self.attribute['volume']}", 1600)
				self.sketch = 'planet.sketch.light'
			else:
				self.spawn()
		return self.timer.update()

	def check_migrate(self) -> float:
		migrate_level = 0
		migrate_level += 2 if self.attribute['life'] else 0
		migrate_level -= (self.attribute['radiation'] - 15) ** 2 / 100
		migrate_level -= (self.attribute['gravitation'] - 15) ** 2 / 100
		migrate_level -= (self.attribute['atmosphere'] - 15) ** 2 / 100
		migrate_level += self.attribute['energy_level'] / 3
		
		return abs(migrate_level) if migrate_level > -2 else 0

	def textbox(self, lang: str = None):
		lang = lang if lang else self.lang 
		self.text_box = [
			# Textbox(f"Gravitation:{str(self.attribute['gravitation']).zfill(2)} / 15    Vital Signs:{'Yes' if self.attribute['life'] else 'No'}", lang),
			# Textbox(f"""Atmosphere: {str(self.attribute['atmosphere']).zfill(2)} / 15    Energy Level:{self.attribute['energy_level']}{ENERGY_LEVEL[f"{self.attribute['energy_level']}"] if lang == 'Chinese' else ''}""", lang),
			# Textbox(f"Radiation:  {str(self.attribute['radiation']).zfill(2)} / 15    Seed:{self.seed}", lang),
			# Textbox(f"Sketch:{self.sketch}", lang)
			Textbox(['planet.gravitation', f"{str(self.attribute['gravitation']).zfill(2)} / 15    ", 'planet.vital_signs', f"{'planet.life_yes' if self.attribute['life'] else 'planet.life_no'}"], lang),
			Textbox(['planet.atmosphere', f"{str(self.attribute['atmosphere']).zfill(2)} / 15    ", 'planet.energy_level', f"""{self.attribute['energy_level']}{ENERGY_LEVEL[f"{self.attribute['energy_level']}"] if lang == 'Chinese' else ''}"""], lang),
			Textbox(['planet.radiation', f"{str(self.attribute['radiation']).zfill(2)} / 15    ", 'planet.seed', f'{self.seed}'], lang),
			Textbox(['planet.sketch', f'{self.sketch}'], lang)
		]

	def update(self, dt: int = None, sky: Sky = None):
		self.angle += 0.15

		self.image = pygame.transform.rotate(self.timer.update(), self.angle)
		self.rect = self.image.get_rect(center = self.rect.center)