from GameObjects import MovingGameObject


class Laser(MovingGameObject):
    def __init__(self, canvas, x, y, angle, speed, size, game):
        super().__init__(canvas, x, y, angle, speed, size, game, color='red')

    def move(self):
        destroyed = []
        super().move()
        coll_coords = self.canvas.find_overlapping(self.x, self.y, self.x + self.size[0] - 2, self.y + self.size[1] - 2)

        for coll_coord in coll_coords:
            if coll_coord != self.id and coll_coord not in self.game.untouchables \
                    and coll_coord != self.game.spaceship.id:
                self.canvas.delete(coll_coord)
                destroyed.append(coll_coord)
                self.canvas.delete(self.id)
                self.state = 'destroyed'
                self.game.up_score()
                break
        return destroyed
