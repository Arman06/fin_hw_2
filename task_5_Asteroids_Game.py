import random
import time
import tkinter
from tkinter import Tk, Canvas, font

from GameObjects import *
from Spaceship import Spaceship
from Asteroid import Asteroid


class Game:
    def __init__(self):
        self.score = 0
        self.lives = LIVES
        self.window = Tk()
        self.window.title('Asteroids')
        self.state = 'start'

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT)

        self.canvas.pack()

        self.bg = StaticGameObject(self.canvas, 0, 0, (WIDTH, HEIGHT), self, img_name="./assets/background.jpg",
                                   anchor=tkinter.NW)

        self.start_page = StaticGameObject(self.canvas, WIDTH // 2, HEIGHT // 2, (WIDTH // 2, HEIGHT // 2), self,
                                           img_name="./assets/start_screen.png", tag='startTag', anchor=tkinter.CENTER)

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
                self.canvas.update()
            else:
                self.actual_game()

    def actual_game(self):
        self.spaceship = Spaceship(self.canvas, WIDTH // 2, HEIGHT // 2, 0, 15, (100, 100), self,
                                   img_name='./assets/spaceship2.png')
        self.window.bind('<Left>', lambda event: self.spaceship.rotate(clockwise=False))
        self.window.bind('<Right>', lambda event: self.spaceship.rotate())

        self.window.bind('<Up>', lambda event: self.spaceship.move())
        self.window.bind('<space>', lambda event: self.spaceship.fire_laser())
        self.window.bind('<Escape>', lambda event: self.set_start())

        self.asteroids = set([Asteroid(self.canvas, random.randint(0, WIDTH-100), random.randint(500, 700),
                                       random.randint(0, 360), 2, (100, 100), self, img_name='./assets/asteroid2.png')
                              for _ in range(8)])

        start_time = time.time()

        while self.state == 'play':
            elapsed_time = time.time() - start_time
            if elapsed_time > 3:
                for _ in range(2):
                    self.asteroids.add(Asteroid(self.canvas, random.randint(100, 700), random.randint(50, 100),
                                       random.randint(0, 360), 2, (100, 100), self, img_name='./assets/asteroid2.png'))
                start_time = time.time()
            current_lasers = self.spaceship.lasers.copy()
            self.spaceship.lasers = set()
            destroyed_asteroids = set()

            for laser in current_lasers:
                for asteroid in laser.update():
                    destroyed_asteroids.add(asteroid)
                if laser.state == 'alive':
                    self.spaceship.lasers.add(laser)

            for asteroid in self.spaceship.update():
                destroyed_asteroids.add(asteroid)

            current_asteroids = self.asteroids.copy()
            self.asteroids = set()
            for asteroid in current_asteroids:
                asteroid.update(True)
                if asteroid.id not in destroyed_asteroids:
                    self.asteroids.add(asteroid)
            self.canvas.tag_raise(self.score_text.id)
            self.canvas.tag_raise(self.lives_text.id)
            self.canvas.update()

        for asteroid in self.asteroids:
            self.canvas.delete(asteroid.id)
        self.asteroids.clear()

        self.canvas.delete(self.spaceship.id)
        for laser in self.spaceship.lasers:
            self.canvas.delete(laser.id)
        self.spaceship.lasers.clear()
        self.spaceship = None

    def start_screen(self):
        pass


def main():
    game = Game()
    game.game_loop()


main()
