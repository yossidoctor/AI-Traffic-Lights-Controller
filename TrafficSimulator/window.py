import numpy as np
import pygame
from pygame.draw import polygon

from TrafficSimulator import Simulation

# For debugging purposes, todo comment-out before project submission
DRAW_VEHICLE_IDS = False
DRAW_ROAD_IDS = False
# DRAW_GRIDLINES = True
FILL_POLYGONS = True


class Window:
    def __init__(self, sim: Simulation = None):
        self.sim: Simulation = sim
        # self.width = 1400
        # self.height = 900
        self.width = 900
        self.height = 700

        self.fps = 60
        self.zoom = 5
        self.offset = (0, 0)

        self.mouse_last = (0, 0)
        self.mouse_down = False

        self.closed = False

        self.screen = None
        self._text_font = None

    def init_screen(self):
        # Create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()
        
        # Fixed fps
        clock = pygame.time.Clock()

        # To draw text
        pygame.font.init()
        self._text_font = pygame.font.SysFont('Lucida Console', 16)

    def update_screen(self):
        if self.screen:  # sanity check
            self.draw_simulation()
            pygame.display.update()
            clock.tick(self.fps)
            
            for event in pygame.event.get():
            # Quit program if window is closed
            if event.type == pygame.QUIT:
                self.closed = True
            # Handle mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # If mouse button down
                if event.button == pygame.BUTTON_LEFT:
                    # Left click
                    x, y = pygame.mouse.get_pos()
                    x0, y0 = self.offset
                    self.mouse_last = (x - x0 * self.zoom, y - y0 * self.zoom)
                    self.mouse_down = True
                if event.button == pygame.BUTTON_WHEELUP:
                    # Mouse wheel up
                    self.zoom *= (self.zoom ** 2 + self.zoom / 4 + 1) / (self.zoom ** 2 + 1)
                if event.button == pygame.BUTTON_WHEELDOWN:
                    # Mouse wheel down
                    self.zoom *= (self.zoom ** 2 + 1) / (self.zoom ** 2 + self.zoom / 4 + 1)
            elif event.type == pygame.MOUSEMOTION:
                # Drag content
                if self.mouse_down:
                    x1, y1 = self.mouse_last
                    x2, y2 = pygame.mouse.get_pos()
                    self.offset = ((x2 - x1) / self.zoom, (y2 - y1) / self.zoom)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False

    def _loop(self, steps):
        for _ in range(steps):
            self.sim.update()
            if self.screen and _ % 2:  # Update the display every other sim update
                self.update_screen()
            if self.closed or self.sim.completed:
                return

    def run(self, action) -> None:
        """
        Applies the action and runs a single simulation update cycle.
        Stops prematurely if the window is closed, the simulation completed or a collision detected
        :param action: an action from the environment action space
        """
        if action:
            self.sim.update_signals()
            if self.screen:
                self.update_screen()
            if self.closed or self.sim.completed:
                return

            self._loop(self.fps * 3)
            if self.closed or self.sim.completed:
                return

            self.sim.update_signals()
            if self.screen:
                self.update_screen()
            if self.closed or self.sim.completed:
                return

        self._loop(self.fps * 3)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (int(self.width / 2 + (x + self.offset[0]) * self.zoom),
                int(self.height / 2 + (y + self.offset[1]) * self.zoom))

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (int(-self.offset[0] + (x - self.width / 2) / self.zoom),
                int(-self.offset[1] + (y - self.height / 2) / self.zoom))

    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True,
                    color=(0, 0, 255)):
        """Draws a rectangle center at *pos* with size *size* rotated anti-clockwise by *angle*."""

        def vertex(e1, e2):
            return (x + (e1 * l * cos + e2 * h * sin) / 2,
                    y + (e1 * l * sin - e2 * h * cos) / 2)

        x, y = pos
        l, h = size
        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        if centered:
            points = self.convert([vertex(*e) for e in [(-1, -1), (-1, 1), (1, 1), (1, -1)]])
        else:
            points = self.convert([vertex(*e) for e in [(0, -1), (0, 1), (2, 1), (2, -1)]])
        # polygon(self.screen, color, points)
        # For debugging purposes, todo comment-out before project submission
        width = 0 if FILL_POLYGONS else 2
        x1, x2 = points[0][0], points[2][0]
        y1, y2 = points[0][1], points[2][1]
        screen_x = x1 + (x2 - x1) / 2
        screen_y = y1 + (y2 - y1) / 2
        polygon(self.screen, color, points, width)
        return screen_x, screen_y

    def draw_arrow(self, pos, size, angle=None, cos=None, sin=None, color=(150, 150, 190)):
        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        self.rotated_box(pos,
                         size,
                         cos=(cos - sin) / np.sqrt(2),
                         sin=(cos + sin) / np.sqrt(2),
                         color=color,
                         centered=False)
        self.rotated_box(pos,
                         size,
                         cos=(cos + sin) / np.sqrt(2),
                         sin=(sin - cos) / np.sqrt(2),
                         color=color,
                         centered=False)

    # def draw_axes(self, color=(100, 100, 100)):
    #     x_start, y_start = self.inverse_convert(0, 0)
    #     x_end, y_end = self.inverse_convert(self.width, self.height)
    #     line(self.screen, self.convert((0, y_start)), self.convert((0, y_end)), color)
    #     line(self.screen, self.convert((x_start, 0)), self.convert((x_end, 0)), color)
    #
    # def draw_grid(self, unit=50, color=(150, 150, 150)):
    #     x_start, y_start = self.inverse_convert(0, 0)
    #     x_end, y_end = self.inverse_convert(self.width, self.height)
    #     n_x = int(x_start / unit)
    #     n_y = int(y_start / unit)
    #     m_x = int(x_end / unit) + 1
    #     m_y = int(y_end / unit) + 1
    #     for i in range(n_x, m_x):
    #         line(self.screen, self.convert((unit * i, y_start)), self.convert((unit * i, y_end)), color)
    #     for i in range(n_y, m_y):
    #         line(self.screen, self.convert((x_start, unit * i)), self.convert((x_end, unit * i)), color)

    def draw_roads(self):
        for road in self.sim.roads:
            # Draw road background
            screen_x, screen_y = self.rotated_box(
                road.start,
                (road.length, 3.7),
                cos=road.angle_cos,
                sin=road.angle_sin,
                color=(180, 180, 220),
                centered=False
            )

            if DRAW_ROAD_IDS:
                # For debugging purposes, todo comment-out before project submission
                text_road_index = self._text_font.render(f'{road.index}', True, (0, 0, 0))
                self.screen.blit(text_road_index, (screen_x, screen_y))

            # Draw road arrow
            if road.length > 5:
                for i in np.arange(-0.5 * road.length, 0.5 * road.length, 10):
                    pos = (road.start[0] + (road.length / 2 + i + 3) * road.angle_cos,
                           road.start[1] + (road.length / 2 + i + 3) * road.angle_sin)
                    self.draw_arrow(pos, (-1.25, 0.2), cos=road.angle_cos, sin=road.angle_sin)

    def draw_vehicle(self, vehicle, road):
        l, h = vehicle.length, vehicle.width
        sin, cos = road.angle_sin, road.angle_cos
        x = road.start[0] + cos * vehicle.x
        y = road.start[1] + sin * vehicle.x
        # self.rotated_box((x, y), (l, h), cos=cos, sin=sin, centered=True)
        screen_x, screen_y = self.rotated_box((x, y), (l, h), cos=cos, sin=sin, centered=True)
        if DRAW_VEHICLE_IDS:
            # For debugging purposes, todo comment-out before project submission
            text_road_index = self._text_font.render(f'{vehicle.index}', True, (255, 255, 255),
                                                     (0, 0, 0))
            self.screen.blit(text_road_index, (screen_x, screen_y))

    def draw_vehicles(self):
        for i in self.sim.non_empty_roads:
            road = self.sim.roads[i]
            for vehicle in road.vehicles:
                self.draw_vehicle(vehicle, road)

    def draw_signals(self) -> None:
        for signal in self.sim.traffic_signals:
            for i in range(len(signal.roads)):
                if signal.current_cycle == (False, False):
                    color = (255, 255, 0) if signal.cycle[signal.current_cycle_index - 1][i] else (
                        255, 0, 0)
                else:
                    color = (0, 255, 0) if signal.current_cycle[i] else (255, 0, 0)
                for road in signal.roads[i]:
                    a = 0
                    position = ((1 - a) * road.end[0] + a * road.start[0],
                                (1 - a) * road.end[1] + a * road.start[1])
                    self.rotated_box(position,
                                     (1, 3),
                                     cos=road.angle_cos, sin=road.angle_sin,
                                     color=color)

    def draw_status(self):
        def render(text, color=(0, 0, 0), background=None):
            return self._text_font.render(text, True, color, background)

        t = render(f't: {self.sim.t:.2f}')
        # fps = render(f'frames: {self.sim.frame_count}')
        self.screen.blit(t, (10, 20))
        # self.screen.blit(fps, (10, 40))
        # n_vehicles_generated = render(f'Generated: {self.sim.n_vehicles_generated}')
        # n_vehicles_on_map = render(f'On map: {self.sim.n_vehicles_on_map}')
        # self.screen.blit(n_vehicles_generated, (10, 60))
        # self.screen.blit(n_vehicles_on_map, (10, 80))

    def draw_simulation(self):
        # Fill background
        self.screen.fill((250, 250, 250))

        # # Major and minor grid and axes
        # if DRAW_GRIDLINES:
        #     # For debugging purposes, todo comment-out before project submission
        #     self.draw_grid(10, (220, 220, 220))
        #     self.draw_grid(100, (200, 200, 200))
        #     self.draw_axes()

        self.draw_roads()
        self.draw_vehicles()
        self.draw_signals()
        self.draw_status()
