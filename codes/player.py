import pygame
from random import randint
from settings import *
from timer import AnimateTimer
from sprites import Generic, Sky, Planet

class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups: list[pygame.sprite.Group]):
		super().__init__(groups)
		
		# Attribute
		self.water = 200
		self.year = 0
		self.energy = 0
		self.people = 1e9

		# Image
		self.image_timer = AnimateTimer('./assets/textures/rocket', 400)
		self.image = pygame.transform.rotate(self.image_timer.update(), 135)
		self.rect = self.image.get_rect(center = pos)
		self.z = LAYERS['main']
		# Fire
		self.fire_timer = AnimateTimer('./assets/textures/fire', 100)
		self.fire = Generic(
			pos = self.rect.bottomleft,
			surf = pygame.image.load('./assets/textures/fire/empty.png').convert_alpha(),
			groups = groups,
			z = LAYERS['main']
			)
		
		# Button sound
		self.button_sound = pygame.mixer.Sound('./assets/button.mp3')
		self.button_sound.set_volume(0.2)

		# A blank sprite to limit other sprites updating
		self.blank = Generic(
			pos = (0, 0),
			surf = pygame.image.load('./assets/textures/rocket/empty.png').convert_alpha(),
			groups = groups,
			z = LAYERS['main']
			)
		# A blank sprite to blit small map
		self.map = Generic(
			pos = (0, 0),
			surf = pygame.image.load('./assets/textures/rocket/map.png').convert_alpha(),
			groups = groups,
			z = LAYERS['main'] 
		)

		# Move
		self.move_speed = 0
		self.angle = 135
		self.acceleration = MOVE['min_acceleration']
		self.direction = pygame.math.Vector2(1, 1)
		self.pos = pygame.math.Vector2(self.rect.center)

	def input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_w]:
			self.acceleration = self.acceleration + 0.005 if self.acceleration < MOVE['max_acceleration'] else MOVE['max_acceleration']
			self.direction = pygame.math.Vector2(1, 1).rotate(-(self.angle))
			self.fire_rotate()
		elif keys[pygame.K_s]:
			self.acceleration = self.acceleration - 0.02 if self.acceleration > MOVE['min_acceleration'] else MOVE['min_acceleration']
			self.fire_clear()
		else:
			if self.move_speed > 0:
				self.acceleration = self.acceleration - 0.002 if self.acceleration > 0 else 0
			elif self.move_speed == 0 and self.acceleration != MOVE['min_acceleration']:
				self.acceleration = MOVE['min_acceleration']
				self.fire_clear()
			if self.acceleration > 0:
				self.fire_clear()

		if keys[pygame.K_d]:
			self.angle -= MOVE['rotate_speed']
		elif keys[pygame.K_a]:
			self.angle += MOVE['rotate_speed']

	def planet_input(self, planet: Planet):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_q] and planet.migrated == False:
			self.button_sound.play()

			while planet.attribute['energy_level'] > 0:
				self.energy += randint(1e7, 12e6)
				planet.attribute['energy_level'] -= 1
			planet.textbox()
			self.migrate_level = planet.check_migrate()

		elif keys[pygame.K_e] and planet.migrated == False:
			self.button_sound.play()

			planet.migrated = True
			self.people -= planet.migrate_level * randint(17e6, 19e6) * planet.attribute['volume'] if self.people - planet.migrate_level * randint(17e6, 19e6) * planet.attribute['volume'] > 0 else 0

	def rotate(self):
		self.image = pygame.transform.rotate(self.image_timer.update(), self.angle)
		self.rect = self.image.get_rect(center = self.rect.center)

		self.blank.rect.center = self.rect.center
		self.map.rect.center = self.rect.center

	def move(self, dt):
		if self.acceleration > 0:
			self.move_speed = self.move_speed + self.acceleration if self.move_speed < MOVE['max_move_speed'] else MOVE['max_move_speed']
		else:
			self.move_speed = self.move_speed + self.acceleration if self.move_speed > 0 else 0

		self.pos.x += self.direction.x * self.move_speed * dt
		self.rect.centerx = self.pos.x

		self.pos.y += self.direction.y * self.move_speed * dt
		self.rect.centery = self.pos.y

	def fire_rotate(self):
		self.fire.image = pygame.transform.rotate(self.fire_timer.update(), self.angle - 135)
		self.fire.rect = self.fire.image.get_rect(center = self.rect.center)

	def fire_clear(self):
		self.fire.image = pygame.image.load('./assets/textures/fire/empty.png').convert_alpha()

	def sky_move(self, sky: Sky):
		for hited in pygame.sprite.spritecollide(self, sky, False):
			if hited.name != 'middle':
				# if hited.name == 'bottom_right':
				# 	sky.move((1, 1))
				# elif hited.name == 'top_left':
				# 	sky.move((-1, -1))
				# elif hited.name == 'top_right':
				# 	sky.move((1, -1))
				# elif hited.name == 'bottom_left':
				# 	sky.move((-1, 1))
				if hited.name == 'bottom':
					sky.move((0, 1))
				elif hited.name == 'right':
					sky.move((1, 0))
				elif hited.name == 'left':
					sky.move((-1, 0))
				elif hited.name == 'top':
					sky.move((0, -1))

	def update(self, dt, sky):
		self.year += 0.08 * dt
		self.input()

		self.sky_move(sky)
		self.rotate()
		self.move(dt)