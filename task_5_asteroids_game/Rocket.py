from GameObjects import MovingGameObject
from PIL import Image, ImageTk


class Rocket(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)
        image = Image.open(self.img_name)
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        self.redraw()

    def move(self):
        destroyed = []
        super().move()
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0] - 10, self.y + self.size[1] - 5)
        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord not in self.game.untouchables \
                    and coll_coord != self.game.spaceship.id\
                    and coll_coord not in set([rocket.id for rocket in self.game.spaceship.rockets]):
                self.canvas.delete(coll_coord)

                destroyed.append(coll_coord)
                self.canvas.delete(self.id)
                self.state = 'destroyed'
                self.game.up_score()
                break
        return destroyed

    def rotate(self):
        self.rotate_image()

    def rotate_image(self):
        image = Image.open(self.img_name)
        image = image.resize(self.size)
        self.image = ImageTk.PhotoImage(image.rotate(self.angle))
        self.redraw()

    def place_on_canvas(self, x, y):
        return self.canvas.create_image(self.x, self.y, image=self.image)
