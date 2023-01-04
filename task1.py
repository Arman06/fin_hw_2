import tkinter as tk
import math


class OvalRotatingObject:
    def __init__(self, center_x, center_y, radius, distance_from_center, angle, speed, x, y,
                 window_obj, canvas_obj, clockwise=True, color='white'):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.distance_from_center = distance_from_center
        self.angle = angle
        self.speed = speed
        self.x = x
        self.y = y
        self.clockwise = clockwise
        self.color = color
        self.canvas_obj = canvas_obj
        self.window_obj = window_obj
        self.children_ovals = []
        self.id = self.canvas_obj.create_oval(*self.get_position(), fill=self.color)

    def add_orbiting_child(self, child):
        self.children_ovals.append(child)

    def get_position(self):
        self.x = self.center_x - self.distance_from_center * math.sin(math.radians((-1 if self.clockwise else 1) * self.angle))
        self.y = self.center_y - self.distance_from_center * math.cos(math.radians((-1 if self.clockwise else 1) * self.angle))
        return self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius

    def start_rotation(self):
        self.angle += self.speed
        self.canvas_obj.coords(self.id, *self.get_position())
        for child_oval in self.children_ovals:
            child_oval.center_x = self.x
            child_oval.center_y = self.y
            self.canvas_obj.coords(child_oval.id, *child_oval.get_position())
        self.window_obj.after(10, self.start_rotation)


def main():
    width = 600
    height = 600
    window = tk.Tk()
    window.title("Task 1")

    canvas = tk.Canvas(window, width=width, heigh=height)
    canvas.pack()

    big_chungus_ball = OvalRotatingObject(width // 2, height // 2, 200, 0, 0, 0, 0, 0, window, canvas)
    small_ball = OvalRotatingObject(big_chungus_ball.x, big_chungus_ball.y, 10, 200, 0, 1, 0, 0,
                                    window, canvas, clockwise=True, color='red')

    # small_ball_2 = OvalRotatingObject(small_ball.x, small_ball.y, 10, 100, 0, 2, 0, 0, window, canvas, color='blue')

    # small_ball.add_orbiting_child(small_ball_2)

    small_ball.start_rotation()

    # small_ball_2.start_rotation()

    window.mainloop()


main()
