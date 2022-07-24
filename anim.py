import pygame as pg
from math import sqrt
from constants import *


class Animate:

    LINEAR = lambda x: x
    EASE_OUT_QUART = lambda x: 1 - pow(1 - x, 4)

    def EASE_IO_QUART(x):
        return 8 * pow(x, 4) if x < 0.5 else 1 - pow(-2 * x + 2, 4) / 2

    def __init__(self, main, dur=500, color=WHITE, fn=EASE_OUT_QUART):
        self.main = main
        self.color = color
        self.function = fn
        self.remove = False
        self.dur = dur
        self.start_time = pg.time.get_ticks()
        self.final_time = self.start_time + dur
        self.type = None
        self.sub_animations = None

    def line(self, p1, p2, width=8):
        self.type = "line"
        self.finished = False
        self.width = width
        self.p1 = pg.Vector2(p1)
        self.p2 = pg.Vector2(p2)
        self.p = self.p2 - self.p1
        self.length = sqrt(self.p.x**2 + self.p.y**2)
        # self.length = self.p.magnitude()
        return self

    def circle(self, center=[WIDTH / 2, HEIGHT / 2], radius=38, width=8):
        self.type = "circle"
        self.finished = False
        self.width = width
        self.radius = radius
        self.r = radius
        self.center = pg.Vector2(center)
        self.rect = pg.Rect(
            (center - pg.Vector2(radius, radius)), (2 * radius, 2 * radius)
        )
        return self

    def cross(self, center=[WIDTH / 2, HEIGHT / 2], length=40, width=10):
        self.type = "cross"
        # fmt: off
        points = [
            pg.Vector2(-length, 0), pg.Vector2(length, 0),
            pg.Vector2(0, length), pg.Vector2(0, -length)
        ]
        # fmt: on
        for point in points:
            point.update(point.rotate(45) + pg.Vector2(center))

        self.sub_animations = [
            Animate(self.main, self.dur + i * 150, self.color, self.function).line(
                points[i], points[i + 1], width
            )
            for i in range(0, len(points), 2)
        ]
        return self

    def setup_remove(self, dur=500):
        self.finished = True
        self.remove = True
        self.dur = dur
        self.start_time = pg.time.get_ticks()
        self.final_time = self.start_time + self.dur
        if self.sub_animations is not None:
            for i in self.sub_animations:
                i.setup_remove(dur)

    def update(self, skip=False):

        # Call method recursively
        if self.type == "cross":
            for animation in self.sub_animations:
                animation.update()
            return

        # Calculate the animation
        if not self.finished or self.remove:
            if pg.time.get_ticks() < self.final_time and not skip:
                fraction = (pg.time.get_ticks() - self.start_time) / self.dur
                if fraction < 0.01:
                    fraction += 0.008

                if self.remove:
                    fraction = 1 - fraction

                if self.type == "line":
                    self.p.scale_to_length(self.length * self.function(fraction))
                elif self.type == "circle":
                    self.r = self.radius - self.width * self.function(fraction)
            else:
                if self.type == "line":
                    self.p = self.p2 - self.p1
                    if self.remove:
                        self.p = [0, 0]
                if self.type == "circle":
                    self.r = self.radius - self.width
                    if self.remove:
                        self.r = self.radius
                self.remove = False
                self.finished = True

        # Draw stuff
        if self.type == "line":
            pg.draw.line(
                self.main.win, self.color, self.p1, self.p + self.p1, self.width
            )
        elif self.type == "circle":
            pg.draw.circle(self.main.win, self.color, self.center, self.radius)
            pg.draw.circle(self.main.win, BLACK, self.center, self.r)