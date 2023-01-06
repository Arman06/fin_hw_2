from Const import *
from PIL import Image, ImageTk
import math


class GameObject:
    def __init__(self, canvas, x, y, size, game, img_name=None, color=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.game = game
        self.img_name = img_name
        if self.img_name:
            image = Image.open(self.img_name)
            image = image.resize(self.size)
            self.image = ImageTk.PhotoImage(image)
        self.id = self.place_on_canvas(self.x, self.y)

    def place_on_canvas(self, x, y):
        pass


class StaticGameObject(GameObject):
    def __init__(self, canvas, x, y, size, game, img_name=None, text=None, tag=None, anchor=None,
                 font_obj=None, color=None):
        self.text = text
        self.tag = tag
        self.anchor = anchor
        self.font = font_obj
        super().__init__(canvas, x, y, size, game, img_name, color)

    def place_on_canvas(self, x, y):
        if self.img_name:
            return self.canvas.create_image(self.x, self.y, image=self.image, tag=self.tag, anchor=self.anchor)
        else:
            return self.canvas.create_text(self.x, self.y, anchor=self.anchor, text=self.text,
                                           fill=self.color, font=self.font)

    def change_text(self, text):
        self.canvas.itemconfigure(self.id, text=text)


class MovingGameObject(GameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, color=None, img_name=None):
        self.angle = angle
        self.speed = speed
        self.state = 'alive'
        super().__init__(canvas, x, y, size, game, img_name, color)

        # self.id = self.place_on_canvas(self.x, self.y)

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
