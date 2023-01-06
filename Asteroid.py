from GameObjects import MovingGameObject


class Asteroid(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game, img_name):
        super().__init__(canvas, x, y, angle, speed, size, game, img_name=img_name)

    def place_on_canvas(self, x, y):
        return self.canvas.create_image(self.x, self.y, image=self.image)
