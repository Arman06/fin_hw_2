import random
import tkinter as tk
import math

WIDTH = 1000
HEIGHT = 500


class Raindrop:
    def __init__(self, canvas, x, y, length, speed=1.0, color='blue'):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.length = length
        self.width = math.log(length, 10)
        self.speed = math.log(length) * speed
        self.id = canvas.create_line(x, y, x, y + length, width=self.width, fill=color)

    def fall(self):
        self.canvas.move(self.id, 0, self.speed)
        self.y += self.speed

        if self.y >= HEIGHT:
            self.y = -150
            self.canvas.move(self.id, 0, -650)


class Rain:
    def __init__(self, canvas, n):
        self.canvas = canvas
        self.n = n
        self.raindrops = []

        for i in range(n):
            x = random.randint(0, WIDTH)
            y = random.randint(-HEIGHT, 100)
            length = random.randint(20, 40)
            speed = 1.3
            raindrop = Raindrop(canvas, x, y, length, speed)
            self.raindrops.append(raindrop)

    def start_animation(self):
        while True:
            for raindrop in self.raindrops:
                raindrop.fall()
            self.canvas.update()


def main():
    window = tk.Tk()
    window.title('Rain')
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT)
    canvas.pack()

    rain = Rain(canvas, 500)
    rain.start_animation()


main()
