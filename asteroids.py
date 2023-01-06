import tkinter
from tkinter import Tk, Canvas, font
from PIL import Image, ImageTk
import math
import random
import time

WIDTH = 800
HEIGHT = 800


class GameObject:
    def __init__(self, canvas, x, y, size, game, img_name=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.game = game
        self.img_name = img_name
        if self.img_name:
            image = Image.open(self.img_name)
            image = image.resize(self.size)
            self.image = ImageTk.PhotoImage(image)


class StaticGameObject(GameObject):
    def __init__(self, canvas, x, y, size, game, img_name=None, text=None):
        super().__init__(canvas, x, y, size, game, img_name)
        self.text = text


class MovingGameObject(GameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, color=None, img_name=None):
        super().__init__(canvas, x, y, size, game, img_name)
        self.angle = angle
        self.speed = speed
        self.color = color
        self.state = 'alive'
        self.id = self.place_on_canvas(self.x, self.y)

    def place_on_canvas(self, x, y):
        return self.canvas.create_rectangle(x - self.size[0], y - self.size[1],
                                            x + self.size[0], y + self.size[1], fill=self.color)

    def redraw(self):
        self.canvas.delete(self.id)
        self.id = self.place_on_canvas(self.x, self.y)

    def move(self):
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = -math.sin(math.radians(self.angle)) * self.speed
        self.canvas.move(self.id, dx, dy)
        self.x += dx
        self.y += dy

    def update(self, toroidal=False, always_moving=True):
        if toroidal:
            if self.x < 0:
                self.x += WIDTH - 10
                self.canvas.move(self.id, WIDTH - 10, 0)
            elif self.x > WIDTH:
                self.x -= WIDTH
                self.canvas.move(self.id, -WIDTH, 0)
            elif self.y < 0:
                self.y += HEIGHT
                self.canvas.move(self.id, 0, HEIGHT - 10)
            elif self.y > HEIGHT:
                self.y -= HEIGHT
                self.canvas.move(self.id, 0, -HEIGHT)
        else:
            if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
                self.canvas.delete(self.id)
                self.state = 'destroyed'
        if always_moving:
            return self.move()


class Laser(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game):
        super().__init__(canvas, x, y, angle, speed, size, game, color='red')

    def move(self):
        destroyed = []
        super().move()
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0] - 2, self.y + self.size[1] - 2)

        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord not in self.game.untouchables and coll_coord != self.game.spaceship.id:
                self.canvas.delete(coll_coord)
                destroyed.append(coll_coord)
                self.canvas.delete(self.id)
                self.state = 'destroyed'
                self.game.up_score()
                break
        return destroyed


class Spaceship(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)
        self.lasers = set()

    def update(self, toroidal=False, always_moving=True):
        if self.x < 0:
            self.x += WIDTH - 10
            self.canvas.move(self.id, WIDTH - 10, 0)
        elif self.x > WIDTH - 10:
            self.x -= WIDTH
            self.canvas.move(self.id, -WIDTH, 0)
        elif self.y < 0:
            self.y += HEIGHT - 10
            self.canvas.move(self.id, 0, HEIGHT - 10)
        elif self.y > HEIGHT - 10:
            self.y -= HEIGHT
            self.canvas.move(self.id, 0, -HEIGHT)
        destroyed = []
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0] / 3, self.y + self.size[1] / 3)

        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord not in self.game.untouchables:
                self.canvas.delete(coll_coord)
                destroyed.append(coll_coord)
                self.x = WIDTH // 2
                self.y = HEIGHT // 2
                self.redraw()
                # self.state = 'destroyed'
                self.game.lower_lives()
                break
        return destroyed

    def rotate(self, clockwise=True):
        if clockwise:
            self.angle -= 10
        else:
            self.angle += 10
        self.angle %= 360
        self.rotate_image()

    def rotate_image(self):
        image = Image.open(self.img_name)
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        self.redraw()

    def place_on_canvas(self, x, y):
        return self.canvas.create_image(self.x, self.y, image=self.image)

    def fire_laser(self):
        dx = math.cos(math.radians(self.angle)) * 75
        dy = -math.sin(math.radians(self.angle)) * 75
        self.lasers.add(Laser(self.canvas, self.x + dx, self.y + dy, self.angle, 5, (4, 4), self.game))


class Asteroid(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)

    def place_on_canvas(self, x, y):
        return self.canvas.create_image(self.x, self.y, image=self.image)


class Game:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.window = Tk()
        self.window.title('Asteroids')
        self.state = 'start'

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT)

        self.canvas.pack()

        img = Image.open("assets/background.jpg")
        img = img.resize((WIDTH, HEIGHT))
        self.bg_img = ImageTk.PhotoImage(img)
        self.bg = self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        img = Image.open("assets/start_screen.png")
        img = img.resize((WIDTH // 2, HEIGHT // 2))
        self.start_img = ImageTk.PhotoImage(img)
        self.start_page = self.canvas.create_image(WIDTH / 2, HEIGHT / 2, image=self.start_img,
                                                   anchor=tkinter.CENTER, tag='startTag')
        self.canvas.tag_bind('startTag', '<ButtonPress-1>', lambda ev: self.on_start_click(ev))

        helv36 = font.Font(family='Helvetica',
                           size=36, weight='bold')
        self.score_text = self.canvas.create_text(50, 50, anchor=tkinter.NW, text=f'Score: {self.score}',
                                                  fill="green", font=helv36)
        self.lives_text = self.canvas.create_text(WIDTH - 50, 50, anchor=tkinter.NE, text=f'Lives: {self.lives}',
                                                  fill="green", font=helv36)

        self.canvas.tag_raise(self.score_text)
        self.canvas.tag_raise(self.lives_text)
        self.canvas.tag_lower(self.bg)
        self.set_start()
        self.untouchables = {self.score_text, self.lives_text, self.bg, self.start_page}
        self.spaceship = None
        self.asteroids = None

    def on_start_click(self, event):
        self.state = 'play'
        self.canvas.itemconfig(self.start_page, state='hidden')

    def up_score(self):
        self.score += 1
        self.canvas.itemconfigure(self.score_text, text=f'Score: {self.score}')

    def lower_lives(self):
        self.lives -= 1
        self.canvas.itemconfigure(self.lives_text, text=f'Lives: {self.lives}')
        if self.lives <= 0:
            self.set_start()

    def set_start(self):
        self.state = 'start'
        self.lives = 3
        self.score = 0
        self.canvas.itemconfig(self.start_page, state='normal')
        self.canvas.itemconfigure(self.score_text, text=f'Score: {self.score}')
        self.canvas.itemconfigure(self.lives_text, text=f'Lives: {self.lives}')
        self.canvas.tag_raise(self.start_page)

    def game_loop(self):
        while True:
            if self.state == 'start':
                self.canvas.update()
            else:
                self.actual_game()

    def actual_game(self):
        self.spaceship = Spaceship(self.canvas, 500, 300, 0, 15, (100, 100), self, img_name='assets/spaceship2.png')
        self.window.bind('<Left>', lambda event: self.spaceship.rotate(clockwise=False))
        self.window.bind('<Right>', lambda event: self.spaceship.rotate())

        self.window.bind('<Up>', lambda event: self.spaceship.move())
        self.window.bind('<space>', lambda event: self.spaceship.fire_laser())
        self.window.bind('<Escape>', lambda event: self.set_start())

        self.asteroids = set([Asteroid(self.canvas, random.randint(0, WIDTH-100), random.randint(500, 700),
                                       random.randint(0, 360), 2, (100, 100), self, img_name='assets/asteroid2.png')
                              for _ in range(8)])

        start_time = time.time()

        while self.state == 'play':
            elapsed_time = time.time() - start_time
            if elapsed_time > 3:
                for _ in range(2):
                    self.asteroids.add(Asteroid(self.canvas, random.randint(100, 700), random.randint(50, 100),
                                       random.randint(0, 360), 2, (100, 100), self, img_name='assets/asteroid2.png'))
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
            self.canvas.tag_raise(self.score_text)
            self.canvas.tag_raise(self.lives_text)
            self.canvas.update()
        for asteroid in self.asteroids:
            self.canvas.delete(asteroid.id)
        self.asteroids.clear()

        self.canvas.delete(self.spaceship.id)
        self.spaceship = None

    def start_screen(self):
        pass


def main():
    game = Game()
    game.game_loop()


main()
