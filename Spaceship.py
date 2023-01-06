from GameObjects import MovingGameObject
from Const import *
from Laser import Laser
from PIL import Image, ImageTk
import math


class Spaceship(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)
        self.lasers = set()

    def update(self, toroidal=False, always_moving=True):
        if self.x < 0:
            self.x += WIDTH
            self.canvas.move(self.id, WIDTH, 0)
        elif self.x > WIDTH - 10:
            self.x -= WIDTH
            self.canvas.move(self.id, -WIDTH, 0)
        elif self.y < 0:
            self.y += HEIGHT
            self.canvas.move(self.id, 0, HEIGHT)
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
