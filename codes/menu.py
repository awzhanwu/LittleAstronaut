import pygame, json
from typing import Callable
from settings import *
from gui import Textbox
from timer import ActiveTimer
from sprites import SpaceStation, Planet

class Menu:
    def __init__(self, lang: list[str], start: Callable, level_reset: Callable):
        self.display_surface = pygame.display.get_surface()
        
        # Start and end func
        self.start = start
        self.end_level_reset_timer = ActiveTimer(10, func = level_reset)

        # Lang
        self.lang = lang
        self.lang_index = 0
        self.lang_change_timer = ActiveTimer(200)

        # Surf
        self.surf = {
			'English': pygame.image.load('./assets/textures/menu/English/main.png').convert_alpha(),
			'Chinese': pygame.image.load('./assets/textures/menu/Chinese/main.png').convert_alpha()
		}
        # Result
        self.result_surf = {
			'English': {
                'lose': pygame.image.load('./assets/textures/menu/English/lose.png').convert_alpha(),
                'win': pygame.image.load('./assets/textures/menu/English/win.png').convert_alpha(),
            },
			'Chinese': {
                'lose': pygame.image.load('./assets/textures/menu/Chinese/lose.png').convert_alpha(),
                'win': pygame.image.load('./assets/textures/menu/Chinese/win.png').convert_alpha(),
            }
		}
        self.result_in = False
        self.result_continue_timer = ActiveTimer(200)

        # Best score
        self.best_score_load()
        self.best_score_textbox = Textbox(['menu.score',f"{self.best_score['best'] if self.best_score['best'] != 0 else '/'}",'menu.years'], self.lang[self.lang_index], size = 30)

        # Show
        self.group = pygame.sprite.Group()
        self.planet = Planet(all_group = self.group, planet_group = None, lang = self.lang[self.lang_index], seed = '0x166dc11a5bb889d')
        self.space_station = SpaceStation(all_group = self.group, planet_group = None, station_group = None, pos = (1050, 20))

        # Button sound
        self.button_sound = pygame.mixer.Sound('./assets/button.mp3')
        self.button_sound.set_volume(0.2)
        
    def run(self):
        keys = pygame.key.get_pressed()

        # Change language
        self.lang_change_timer.update()
        if keys[pygame.K_e] and not self.lang_change_timer.active and not self.result_in:
            self.button_sound.play()
            self.lang_index = self.lang_index + 1 if self.lang_index < len(self.lang) - 1 else 0
            self.best_score_textbox.update(['menu.score',f"{self.best_score['best']}",'menu.years'], self.lang[self.lang_index])
            self.lang_change_timer.activate()
        # Start
        elif keys[pygame.K_q] and not self.result_in:
            self.button_sound.play()
            self.start()

        # Display
        self.display_surface.fill((16, 16, 44))
        self.display_surface.blit(self.surf[f'{self.lang[self.lang_index]}'], self.surf[f'{self.lang[self.lang_index]}'].get_rect(bottomright = (SCREEN_WIDTH, SCREEN_HEIGHT)))
        self.display_surface.blit(self.best_score_textbox.image, self.best_score_textbox.image.get_rect(center = (SCREEN_WIDTH / 2, 100)))
        self.group.update()
        for sprite in self.group.sprites():
            self.display_surface.blit(sprite.image, sprite.rect)
        if self.result_in:
            # Textbox
            self.display_surface.blit(self.result_surf[f'{self.lang[self.lang_index]}'][self.result], self.result_surf[f'{self.lang[self.lang_index]}'][self.result].get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
            self.display_surface.blit(self.result_textbox.image, self.result_textbox.image.get_rect(center = (SCREEN_WIDTH / 2, 430)))
            # Level reset
            self.end_level_reset_timer.update()
            # Continue
            self.result_continue_timer.update()
            if keys[pygame.K_w]:
                self.button_sound.play()
                self.result_in = False if not self.result_continue_timer.active and not self.result_continue_timer.active else True
            
    def best_score_load(self):
        try: 
            with open('./best_score.json', 'r', encoding = 'utf-8') as file:
                self.best_score = json.load(file)
        except:
            self.best_score = {"best": 0}
            with open('./best_score.json', 'w', encoding = 'utf-8') as file:
                json.dump(self.best_score, file)

    def end(self, result: str, year: int | str):

        # End set and textbox
        self.result = result
        self.result_in = True
        self.result_continue_timer.activate()
        self.result_textbox = Textbox(['menu.end',f"{year}",'menu.years'], self.lang[self.lang_index], size = 30)

        # Best score check and save
        self.best_score_load()
        if self.result == 'win' and (self.best_score['best'] > year or self.best_score['best'] == 0):
            self.best_score = {"best": year}
            self.best_score_textbox.update(['menu.score',f"{year}",'menu.years'], self.lang[self.lang_index])
            with open('./best_score.json', 'w', encoding = 'utf-8') as file:
                json.dump(self.best_score, file)

        # Level reset
        self.end_level_reset_timer.activate()