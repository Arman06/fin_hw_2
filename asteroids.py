from tkinter import Tk, Canvas
from PIL import Image, ImageTk
import math
import random

WIDTH = 1000
HEIGHT = 800


class GameObject:
    def __init__(self, canvas, x, y, angle, speed, size, game, color=None, img_name=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = size
        self.color = color
        self.game = game
        self.state = 'alive'
        if img_name:
            self.img_name = img_name
            image = Image.open(self.img_name)
            image = image.resize(self.size)
            image = image.rotate(self.angle)
            self.image = ImageTk.PhotoImage(image)
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
                self.x = WIDTH - 10
                self.redraw()
            elif self.x > WIDTH:
                self.x = 0
                self.redraw()
            if self.y < 0:
                self.y = HEIGHT - 10
                self.redraw()
            elif self.y > HEIGHT:
                self.y = 0
                self.redraw()
        else:
            if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
                self.canvas.delete(self.id)
                self.state = 'destroyed'
        if always_moving:
            return self.move()


class Laser(GameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game):
        super().__init__(canvas, x, y, angle, speed, size, game, color='red')

    def move(self):
        destroyed = []
        super().move()
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0] - 2, self.y + self.size[1] - 2)
        print(coll_coords)
        print(self.id)
        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord != self.game.bg and coll_coord != self.game.spaceship.id:
                self.canvas.delete(coll_coord)
                destroyed.append(coll_coord)
                self.canvas.delete(self.id)
                self.state = 'destroyed'
                break
        return destroyed


class Spaceship(GameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)
        self.lasers = set()

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


class Asteroid(GameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)

    def place_on_canvas(self, x, y):
        return self.canvas.create_image(self.x, self.y, image=self.image)

    def crush(self):
        self.canvas.delete(self.id)
        self.state = 'destroyed'


class Game:
    def __init__(self):
        self.window = Tk()
        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.img = Image.open("assets/background.jpg")
        self.img = self.img.resize((WIDTH, HEIGHT))
        self.bg_img = ImageTk.PhotoImage(self.img)
        self.bg = self.canvas.create_image(0, 0, image=self.bg_img, anchor="nw")

        self.spaceship = Spaceship(self.canvas, 500, 300, 0, 15, (100, 100), self, img_name='assets/spaceship.png')
        self.window.bind('<Left>', lambda event: self.spaceship.rotate(clockwise=False))
        self.window.bind('<Right>', lambda event: self.spaceship.rotate())

        self.window.bind('<Up>', lambda event: self.spaceship.move())
        self.window.bind('<space>', lambda event: self.spaceship.fire_laser())

        self.asteroids = set([Asteroid(self.canvas, random.randint(100, 700), random.randint(100, 700),
                                       random.randint(0, 360), 1, (100, 100), self, img_name='assets/asteroid.png') for _ in range(5)])

    def game_loop(self):
        while True:
            current_lasers = self.spaceship.lasers.copy()
            self.spaceship.lasers = set()
            destroyed_asteroids = set()

            for laser in current_lasers:
                for asteroid in laser.update():
                    destroyed_asteroids.add(asteroid)
                if laser.state == 'alive':
                    self.spaceship.lasers.add(laser)

            current_asteroids = self.asteroids.copy()
            self.asteroids = set()
            for asteroid in current_asteroids:
                asteroid.update(True)
                if asteroid.id not in destroyed_asteroids:
                    self.asteroids.add(asteroid)
            self.spaceship.update(True, False)

            self.canvas.update()


def main():
    game = Game()
    game.game_loop()


main()
