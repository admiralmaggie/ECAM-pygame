import pygame
from pygame import gfxdraw
import math
import random
import os
import time
import http
from threading import Thread

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)

#FONT = 'fonts//B612Mono-Regular.ttf'
FONT = 'fonts//B612-Regular.ttf'
POLYGON_NO = 20


class Gauge:
    x = 0
    y = 0
    r = 0
    title = ""
    parent_surface = None
    gauge_x = 0
    gauge_y = 0
    surface = None
    needle_color = None
    dial_color = None
    max_dial_angle = 0
    angle = 0
    needle_thickness = 0
    needle_length = 0
    arc_thickness = 0
    text_fontsize = 0
    tick_fontsize = 0
    tick_max = 0
    tick_min = 0
    ticks = 0

    def __init__(self, surface, gauge_x, gauge_y, r, max_dial_angle, title, ticks, tick_min, tick_max,
                 angle=0, dial_color=WHITE, needle_color=GREEN):
        self.gauge_x = gauge_x
        self.gauge_y = gauge_y
        self.r = r
        self.title = title
        self.parent_surface = surface
        self.max_dial_angle = max_dial_angle
        self.needle_color = needle_color
        self.dial_color = dial_color
        self.angle = angle
        self.ticks = ticks
        self.tick_min = tick_min
        self.tick_max = tick_max
        self.surface = pygame.Surface((r*3, r*3))
        self.x = round(self.r + self.r*.25)
        self.y = round(self.r + self.r*.25)

        self.needle_thickness = round(self.r*.03)
        self.needle_length = round(self.r*.16)
        self.arc_thickness = round(self.r*.05)
        self.text_fontsize = round(self.r*.05)
        self.tick_fontsize = round(self.r*.165)
        self.update(angle)

    def update(self, angle):
        self.angle = angle
        self.surface.fill(BLACK)

        GFX.draw_arc(self.surface, self.x, self.y, self.r, self.arc_thickness, 0,
                     -self.max_dial_angle * (math.pi / 180), self.dial_color)

        for tick in range(0, self.ticks+1):
            tick_angle = round((self.max_dial_angle / self.ticks) * tick) + 90

            tick_text = str(round(tick * (self.tick_max-self.tick_min)/self.ticks, 1) + self.tick_min)
            head, _sep, tail = tick_text.rpartition(".0")
            tick_text = head + tail

            self._draw_gauge_ticks(self.surface, self.x, self.y, self.r, self.needle_length,
                                   round(self.needle_thickness / 2), tick_angle, self.dial_color)
            self._draw_tick_text(self.surface, self.x, self.y, self.r,
                                 tick_angle, tick_text, self.tick_fontsize, WHITE)

        self._draw_gauge_needle(self.surface, self.x, self.y, self.r, self.needle_length,
                                self.needle_thickness, self.angle+90, self.needle_color)
        self._draw_framed_text(self.surface, round(self.x+self.r*.2), round(self.y+self.r*.5), round(self.r*1.5),
                             round(self.r*.8), self.text_fontsize, self.title,
                             str(self.angle), self.dial_color, self.needle_color,
                             round(self.r*.4), round(self.r*.7))

        self.parent_surface.blit(self.surface, [self.gauge_x, self.gauge_y])

    @staticmethod
    def _draw_gauge_needle(surface, x, y, radius, length, thick, angle, color):
        x1 = round(x + ((radius - length) * math.sin(math.pi * 2 * angle / 360)))
        y1 = round(y + ((radius - length) * math.cos(math.pi * 2 * angle / 360)))
        x2 = round(x + ((radius + length) * math.sin(math.pi * 2 * angle / 360)))
        y2 = round(y + ((radius + length) * math.cos(math.pi * 2 * angle / 360)))

        GFX.draw_line(surface, [x1, y1], [x2, y2], thick, color)

    @staticmethod
    def _draw_tick_text(surface, x, y, radius, angle, text, text_size, text_color):
        text_font = pygame.font.Font(FONT, text_size)
        text_surface = text_font.render(text, True, text_color)

        offset_x = radius - radius* .4
        offset_y = radius - radius * .33

        x = round(x + (offset_x * math.sin(math.pi * 2 * angle / 360)))
        y = round(y + (offset_y * math.cos(math.pi * 2 * angle / 360)))

        surface.blit(text_surface, (round(x-text_surface.get_rect().width/2),
                                    round(y-text_surface.get_rect().height/2)))

    @staticmethod
    def _draw_framed_text(surface, x, y, w, h, thick, title, text, color_title, text_color, title_size, text_size):
        pygame.gfxdraw.box(surface, [x, y, w, h], text_color)
        pygame.gfxdraw.box(surface, [round(x + thick / 2), round(y + thick / 2), w - thick, h - thick], BLACK)
        text_val_font = pygame.font.Font(FONT, text_size)
        text_title_font = pygame.font.Font(FONT, title_size)
        text_val_surface = text_val_font.render(text, True, text_color)
        text_title_surface = text_title_font.render(title, True, color_title)
        text_w, text_h = text_val_font.size(text)
        surface.blit(text_val_surface, (round(x+(w/2)-(text_w/2)), y))

        title_rect = (round(x + w / 2 - text_title_surface.get_rect().width / 2), round(y - y / 4))
        surface.blit(text_title_surface, title_rect)

    @staticmethod
    def _draw_gauge_ticks(surface, x, y, radius, length, thick, angle, color):
        x1 = round(x + ((radius - length) * math.sin(math.pi * 2 * angle / 360)))
        y1 = round(y + ((radius - length) * math.cos(math.pi * 2 * angle / 360)))
        x2 = round(x + (radius * math.sin(math.pi * 2 * angle / 360)))
        y2 = round(y + (radius * math.cos(math.pi * 2 * angle / 360)))

        GFX.draw_line(surface, [x1, y1], [x2, y2], thick, color)


class GFX:
    @staticmethod
    def draw_circle(surface, x, y, radius, color):
        pygame.gfxdraw.aacircle(surface, x, y, radius, color)
        pygame.gfxdraw.filled_circle(surface, x, y, radius, color)

    @staticmethod
    def draw_arc(surface, x, y, r, th, start, stop, color):
        points_outer = []
        points_inner = []
        n = round(r*abs(stop-start)/POLYGON_NO)
        if n < 2:
            n = 2
        for i in range(n):
            delta = i/(n-1)
            phi0 = start + (stop-start)*delta
            x0 = round(x+r*math.cos(phi0))
            y0 = round(y+r*math.sin(phi0))
            points_outer.append([x0,y0])
            phi1 = stop + (start-stop)*delta
            x1 = round(x+(r-th)*math.cos(phi1))
            y1 = round(y+(r-th)*math.sin(phi1))
            points_inner.append([x1,y1])
        points = points_outer + points_inner
        pygame.gfxdraw.aapolygon(surface, points, color)
        pygame.gfxdraw.filled_polygon(surface, points, color)

    @staticmethod
    def move_object(rotation, steps, position):
        x = math.cos(math.radians(rotation)) * steps + position[0]
        y = math.sin(math.radians(rotation)) * steps + position[1]
        return x, y

    @staticmethod
    def draw_line(surface, point1, point2, thickness, color):
        angle = math.degrees(math.atan2(point1[1] - point2[1], point1[0] - point2[0]))

        vertices = [GFX.move_object(angle - 90, thickness, point1),
                    GFX.move_object(angle + 90, thickness, point1),
                    GFX.move_object(angle + 90, thickness, point2),
                    GFX.move_object(angle - 90, thickness, point2)]

        pygame.gfxdraw.aapolygon(surface, vertices, color)
        pygame.gfxdraw.filled_polygon(surface, vertices, color)

def worker1():
    current = 0
    next_number = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                exit(0)

            if event.type == pygame.MOUSEBUTTONDOWN or \
                event.type == pygame.MOUSEBUTTONUP or \
                event.type == pygame.MOUSEMOTION or \
                event.type == pygame.MOUSEWHEEL or \
                event.type == pygame.FINGERDOWN or \
                event.type == pygame.FINGERUP or \
                event.type == pygame.FINGERMOTION:
                exit(0)

        if current == next_number:
            next_number = random.randrange(0, 270)
        if current < next_number:
            current += 1
        else:
            current -= 1

        gauge1.update(current)

        if os.name == 'nt':
            time.sleep(.005)

        pygame.display.flip()


pygame.init()
pygame.mouse.set_visible(False)
size = width, height = 800, 480
screen = pygame.display.set_mode(size)
pygame.font.init()

degree = 0
current = 0
next_number = 0

gauge1 = Gauge(surface=screen, gauge_x=0, gauge_y=0, r=180, max_dial_angle=270,
               title="SPEED", ticks=6, tick_min=100, tick_max=270)
# gauge2 = Gauge(screen, 200, 0, 50, 270, "VOLT", 6)
# gauge3 = Gauge(screen, 400, 0, 50, 270, "AMP", 7)
# gauge4 = Gauge(screen, 600, 0, 50, 270, "POWER", 8)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            exit(0)

    if current == next_number:
        next_number = random.randrange(100, 270)
    if current < next_number:
        current += 1
    else:
        current -= 1

    gauge1.update(current)
    # gauge2.update(current)
    # gauge3.update(current)
    # gauge4.update(current)

    if os.name == 'nt':
        time.sleep(.005)

    pygame.display.flip()
