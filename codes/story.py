import pygame
from typing import Callable
from settings import *
from gui import Textbox
from timer import ActiveTimer, AnimateTimer

class Story():
    def __init__(self, end_func: Callable):
        self.end = end_func

        # Display
        self.display_surface = pygame.display.get_surface()
        self.image_timer = AnimateTimer('./assets/textures/story', 500)
        self.texts = [
            Textbox(['story.text_1'], 'Chinese', 40, 'white'),
            Textbox(['story.text_2'], 'Chinese', 40, 'white'),
            Textbox(['story.text_3'], 'Chinese', 40, 'white'),
            Textbox(['story.text_4'], 'Chinese', 40, 'white'),
            Textbox(['story.text_5'], 'Chinese', 40, 'aqua'),
            Textbox(['story.text_6'], 'Chinese', 40, 'aqua'),
            Textbox(['story.text_7'], 'Chinese', 40, 'aqua'),
            Textbox(['story.text_8'], 'Chinese', 40, 'aqua'),

            Textbox(['story.text_9'], 'Chinese', 40, 'aqua'),
            Textbox(['story.text_10'], 'Chinese', 80, 'yellow'),
        ]
        self.index = 0
        self.text = None
        self.show_timer = ActiveTimer(5000, True, self.show)

        # Button sound
        self.button_sound = pygame.mixer.Sound('./assets/button.mp3')
        self.button_sound.set_volume(0.2)
    
    def show(self):
        # Story show
        if self.index <= 9:
            self.text = self.texts[self.index]
            self.show_timer.activate()
            self.index += 1
        else:
            self.end()

    def run(self):
        keys = pygame.key.get_pressed()

        # Display
        self.show_timer.update()
        self.image = self.image_timer.update()

        self.display_surface.fill(('black'))
        self.display_surface.blit(self.image, self.image.get_rect(topleft = (0,0)))
        if self.text:
            self.display_surface.blit(self.text.image, self.text.image.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 130)))

        # Skip
        if keys[pygame.K_w]:
            self.button_sound.play()
            self.end()