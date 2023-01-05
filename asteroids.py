from tkinter import Tk, Canvas
from PIL import Image, ImageTk
import math
import random

WIDTH = 800
HEIGHT = 800


class Laser:
    def __init__(self, canvas, x, y, angle, starship):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 5
        self.size = (4, 4)
        self.starship = starship
        self.state = 'alive'
        self.id = canvas.create_rectangle(x - 4, y - 4, x + 4, y + 4, fill='red')

    def redraw(self):
        self.canvas.delete(self.id)
        self.id = self.canvas.create_rectangle(self.x - 4, self.y - 4, self.x + 4, self.y + 4, fill='red')

    def move(self):
        destroyed = []
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = -math.sin(math.radians(self.angle)) * self.speed
        self.canvas.move(self.id, dx, dy)
        self.x += dx
        self.y += dy
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0], self.y + self.size[1])
        print(coll_coords)
        print(self.id)
        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord != 1 and coll_coord != self.starship:
                self.canvas.delete(coll_coord)
                destroyed.append(coll_coord)
                self.canvas.delete(self.id)
                self.state = 'destroyed'
                break
        return destroyed
        # if self.x < 0:
        #     self.x = WIDTH - 10
        #     self.redraw()
        # elif self.x > WIDTH:
        #     self.x = 0
        #     self.redraw()
        # if self.y < 0:
        #     self.y = HEIGHT - 10
        #     self.redraw()
        # elif self.y > HEIGHT:
        #     self.y = 0
        #     self.redraw()

    def update(self):
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.canvas.delete(self.id)
            self.state = 'destroyed'
        return self.move()


class Spaceship:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 15
        self.size = (100, 100)
        image = Image.open('assets/spaceship.png')
        image = image.resize(self.size)
        image = image.rotate(self.angle)
        self.image = ImageTk.PhotoImage(image)
        self.id = canvas.create_image(self.x, self.y, image=self.image)
        self.lasers = set()

    def rotate_left(self):
        self.angle += 10
        self.angle %= 360
        image = Image.open('assets/spaceship.png')
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        self.redraw()

    def rotate_right(self):
        self.angle -= 10
        self.angle %= 360
        image = Image.open('assets/spaceship.png')
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        self.redraw()

    def move_forward(self):
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = -math.sin(math.radians(self.angle)) * self.speed
        self.canvas.move(self.id, dx, dy)
        self.x += dx
        self.y += dy

    def update(self):
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

    def redraw(self, moving=False):
        self.canvas.delete(self.id)
        self.id = self.canvas.create_image(self.x, self.y, image=self.image)

    def fire_laser(self):
        dx = math.cos(math.radians(self.angle)) * 50
        dy = -math.sin(math.radians(self.angle)) * 50
        self.lasers.add(Laser(self.canvas, self.x + dx, self.y + dy, self.angle, self.id))


class Asteroid:
    def __init__(self, canvas, x, y, angle, clockwise):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = (100, 100)
        self.angle = angle
        self.speed = 1
        self.clockwise = clockwise
        self.state = 'alive'
        image = Image.open('assets/asteroid.png')
        image = image.resize(self.size)
        image = image.rotate(self.angle)
        self.image = ImageTk.PhotoImage(image)
        self.id = canvas.create_image(self.x, self.y, image=self.image)

    def move(self):
        if self.clockwise:
            self.angle -= 1
        else:
            self.angle += 1
        self.angle %= 360
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = -math.sin(math.radians(self.angle)) * self.speed
        self.canvas.move(self.id, dx, dy)
        self.x += dx
        self.y += dy
        # self.redraw()

    def update(self):
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
        self.move()

    def redraw(self):
        image = Image.open('assets/asteroid.png')
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        self.canvas.delete(self.id)
        self.id = self.canvas.create_image(self.x, self.y, image=self.image)

    def crush(self):
        self.canvas.delete(self.id)





def main():
    window = Tk()
    canvas = Canvas(window, width=WIDTH, height=HEIGHT)
    canvas.pack()
    img = Image.open("assets/background.jpg")
    img = img.resize((WIDTH, HEIGHT))
    bg = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=bg, anchor="nw")

    spaceship = Spaceship(canvas, 500, 300)
    window.bind('<Left>', lambda event: spaceship.rotate_left())
    window.bind('<Right>', lambda event: spaceship.rotate_right())

    window.bind('<Up>', lambda event: spaceship.move_forward())
    window.bind('<space>', lambda event: spaceship.fire_laser())

    asteroids = set([Asteroid(canvas, random.randint(100, 700), random.randint(100, 700), random.randint(0, 360),
                              bool(random.getrandbits(1)))
                     for _ in range(5)])

    while True:
        current_lasers = spaceship.lasers.copy()
        spaceship.lasers = set()
        destroyed_asteroids = set()

        for laser in current_lasers:
            for asteroid in laser.update():
                destroyed_asteroids.add(asteroid)
            if laser.state == 'alive':
                spaceship.lasers.add(laser)

        current_asteroids = asteroids.copy()
        asteroids = set()
        for asteroid in current_asteroids:
            asteroid.update()
            if asteroid.id not in destroyed_asteroids:
                asteroids.add(asteroid)
        spaceship.update()

        canvas.update()


main()
