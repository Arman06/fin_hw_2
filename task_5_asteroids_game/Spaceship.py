from GameObjects import MovingGameObject
from Const import *
from Rocket import Rocket
from PIL import Image, ImageTk
import math


class Spaceship(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, still_img_name, moving_img_name):
        self.moving = False
        self.rockets = set()
        self.dx = 0
        self.dy = 0
        self.acceleration = 0
        self.moving_img_name = moving_img_name
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=still_img_name)

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if abs(self.dx) < self.speed/5 and abs(self.dy) < self.speed/5:
            self.moving = False
        else:
            self.moving = True
        self.canvas.move(self.id, self.dx, self.dy)
        self.dx *= (1 - self.game.resistance)
        self.dy *= (1 - self.game.resistance)

    def move_forward(self):
        self.dx += math.cos(math.radians(self.angle)) * self.speed
        self.dy += -math.sin(math.radians(self.angle)) * self.speed

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
        self.redraw()
        destroyed = []
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0] / 3, self.y + self.size[1] / 3)

        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord not in self.game.untouchables\
                    and coll_coord not in set([rocket.id for rocket in self.rockets]):
                self.canvas.delete(coll_coord)
                destroyed.append(coll_coord)
                self.x = WIDTH // 2
                self.y = HEIGHT // 2
                self.redraw()
                # self.state = 'destroyed'
                self.game.lower_lives()
                break
        self.move()
        return destroyed

    def redraw(self):
        self.canvas.delete(self.id)
        self.id = self.place_on_canvas(self.x, self.y)

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

    def create_image(self, img_name):
        image = Image.open(self.game.get_path(img_name))
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        return self.canvas.create_image(self.x, self.y, image=self.image)

    def place_on_canvas(self, x, y):
        if self.moving:
            return self.create_image(self.moving_img_name)
        else:
            return self.create_image(self.img_name)

    def fire_laser(self):
        dx = math.cos(math.radians(self.angle)) * 50
        dy = -math.sin(math.radians(self.angle)) * 50
        self.rockets.add(Rocket(self.canvas, self.x + dx, self.y + dy, self.angle, 5, (40, 40), self.game,
                                img_name=self.game.get_path(self.game.images['missile'])))
