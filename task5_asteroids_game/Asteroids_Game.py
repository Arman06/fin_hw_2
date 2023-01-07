import random
import time
import tkinter
from tkinter import Tk, Canvas, font
import os
from pathlib import Path
from GameObjects import *
from Spaceship import Spaceship
from Asteroid import Asteroid


class Game:
    def __init__(self):
        self.score = 0
        self.resistance = 0.05
        self.lives = LIVES
        self.window = Tk()
        self.window.title('Asteroids')
        self.state = 'start'
        self.images = {'background': './assets/background.jpg', 'start_page': 'assets/start_screen.png',
                       'spaceship': 'assets/spaceship2.png', 'asteroid': 'assets/asteroid2.png',
                       'missile': 'assets/missile2.png', 'moving_spaceship': 'assets/spaceship2_moving.png'}

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT)

        self.canvas.pack()

        self.bg = StaticGameObject(self.canvas, 0, 0, (WIDTH, HEIGHT), self, img_name=self.get_path(
            self.images['background']),
                                   anchor=tkinter.NW)

        self.start_page = StaticGameObject(self.canvas, WIDTH // 2, HEIGHT // 2, (WIDTH // 2, HEIGHT // 2), self,
                                           img_name=self.get_path(self.images['start_page']), tag='startTag', anchor=tkinter.CENTER)

        self.canvas.tag_bind('startTag', '<ButtonPress-1>', lambda ev: self.on_start_click(ev))

        helv36 = font.Font(family='Helvetica',
                           size=36, weight='bold')

        self.score_text = StaticGameObject(self.canvas, 50, 50, anchor=tkinter.NW, text=f'Score: {self.score}',
                                           color="green", font_obj=helv36, game=self, size=None)

        self.lives_text = StaticGameObject(self.canvas, WIDTH - 50, 50, anchor=tkinter.NE, text=f'Lives: {self.lives}',
                                           color="green", font_obj=helv36, game=self, size=None)

        self.canvas.tag_raise(self.score_text.id)
        self.canvas.tag_raise(self.lives_text.id)
        self.canvas.tag_lower(self.bg.id)
        self.set_start()
        self.untouchables = {self.score_text.id, self.lives_text.id, self.bg.id, self.start_page.id}
        self.spaceship = None
        self.asteroids = None

    def on_start_click(self, event):
        self.state = 'play'
        self.canvas.itemconfig(self.start_page.id, state='hidden')

    def up_score(self):
        self.score += 1
        self.score_text.change_text(f'Score: {self.score}')

    def lower_lives(self):
        self.lives -= 1
        self.lives_text.change_text(f'Lives: {self.lives}')
        if self.lives <= 0:
            self.set_start()

    def set_start(self):
        self.state = 'start'
        self.lives = LIVES
        self.score = 0
        self.canvas.itemconfig(self.start_page.id, state='normal')
        self.score_text.change_text(f'Score: {self.score}')
        self.lives_text.change_text(f'Lives: {self.lives}')
        self.canvas.tag_raise(self.start_page.id)

    def game_loop(self):
        while True:
            if self.state == 'start':
                self.start_screen()
            else:
                self.actual_game()

    def start_screen(self):
        self.asteroids = set([Asteroid(self.canvas, random.randint(0, WIDTH), random.randint(0, HEIGHT),
                                       180, 5,
                                       (50, 50), self,
                                       img_name=self.get_path(self.images['asteroid'])) for _ in range(25)])
        while self.state == 'start':
            for asteroid in self.asteroids:
                asteroid.update(toroidal=True)
            self.canvas.tag_raise(self.start_page.id)
            self.canvas.tag_raise(self.score_text.id)
            self.canvas.tag_raise(self.lives_text.id)
            self.canvas.update()
        for asteroid in self.asteroids:
            self.canvas.delete(asteroid.id)
        self.asteroids.clear()

    def actual_game(self):
        self.spaceship = Spaceship(self.canvas, WIDTH // 2, HEIGHT // 2, 0, 2.5, (150, 150), self,
                                   still_img_name=self.get_path(self.images['spaceship']),
                                   moving_img_name=self.get_path(self.images['moving_spaceship']))
        self.window.bind('<Left>', lambda event: self.spaceship.rotate(clockwise=False))
        self.window.bind('<Right>', lambda event: self.spaceship.rotate())

        self.window.bind('<Up>', lambda event: self.spaceship.move_forward())
        self.window.bind('<space>', lambda event: self.spaceship.fire_laser())
        self.window.bind('<Escape>', lambda event: self.set_start())

        print(self.asteroids)
        self.asteroids = set([Asteroid(self.canvas, random.randint(0, WIDTH-100), random.randint(30, 100),
                                       random.randint(0, 360), 2, (100, 100), self, img_name=self.get_path(
                self.images['asteroid']))
                              for _ in range(5)])

        start_time = time.time()

        while self.state == 'play':
            elapsed_time = time.time() - start_time
            if elapsed_time > 3:
                for _ in range(3):
                    self.asteroids.add(Asteroid(self.canvas, random.randint(100, 700), random.randint(50, 100),
                                                random.randint(0, 360), 2, (100, 100), self, img_name=self.get_path(
                            self.images['asteroid'])))
                start_time = time.time()
            current_rockets = set()
            destroyed_asteroids = set()

            for rocket in self.spaceship.rockets:
                for asteroid in rocket.update():
                    destroyed_asteroids.add(asteroid)
                if rocket.state == 'alive':
                    current_rockets.add(rocket)
            self.spaceship.rockets = current_rockets

            for asteroid in self.spaceship.update():
                destroyed_asteroids.add(asteroid)

            current_asteroids = self.asteroids.copy()
            self.asteroids = set()
            for asteroid in current_asteroids:
                asteroid.update(toroidal=True)
                if asteroid.id not in destroyed_asteroids:
                    self.asteroids.add(asteroid)
            self.canvas.tag_raise(self.score_text.id)
            self.canvas.tag_raise(self.lives_text.id)
            self.canvas.update()

        for asteroid in self.asteroids:
            self.canvas.delete(asteroid.id)
        self.asteroids.clear()

        self.canvas.delete(self.spaceship.id)
        for rocket in self.spaceship.rockets:
            self.canvas.delete(rocket.id)
        self.spaceship.rockets.clear()
        self.spaceship = None

    def get_path(self, file_path):
        return os.path.join(os.path.dirname(Path(__file__).absolute()), file_path)


def main():
    game = Game()
    game.game_loop()


main()
