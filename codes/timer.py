import pygame
from os import walk
from re import match
from typing import Callable

class Timer:
	def __init__(self, duration: int):
		self.duration = duration
		self.start_time = pygame.time.get_ticks()

	def update(self) -> bool:
		current_time = pygame.time.get_ticks()
		return True if current_time - self.start_time > self.duration else False


class ActiveTimer(Timer):
	def __init__(self, duration: int, default: bool = False, func: Callable = None) -> Timer:
		super().__init__(duration)
		self.active = default
		self.func = func

	def activate(self):
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def update(self):
		if self.active and super().update():
			self.active = False
			if self.func:
				self.func()


class AnimateTimer(Timer):
	def __init__(self, path: str, duration: int) -> Timer:
		super().__init__(duration)
		self.images = []
		self.index = 0

		for _, _, files in walk(path):
			for file in files:
				if match('.*\d{1,2}.png$', file):
					self.images.append(f'{path}/{file}')

	def update(self) -> pygame.Surface:
		if super().update():
			self.index = self.index + 1 if (self.index < len(self.images) - 1) else 0
			self.start_time = pygame.time.get_ticks()
		return pygame.image.load(self.images[self.index]).convert_alpha()