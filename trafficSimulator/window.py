import numpy as np
import pygame
from pygame import draw, QUIT, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP, KEYDOWN

# for debugging purposes, remove after completion
DRAW_ROAD_IDS = False  # True for debugging, False by default
FILL_POLYGONS = True  # False for debugging, True by default
DRAW_GRID = False  # True for debugging, False by default
ZOOM_IN_UPON_COLLISION = False  # True for debugging, False by default

EVENTS = {QUIT, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP, KEYDOWN}


class Window:
    def __init__(self, sim, width, height, zoom):
        self.sim = sim
        self.width = width
        self.height = height
        self.zoom = zoom
        self.quit = False
        self.last_ems_update_time = 0

        # for debugging purposes, remove after completion
        self.offset = (0, 0)
        self.mouse_last = (0, 0)
        self.mouse_down = False

        # Create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()

        # Fixed fps
        self.clock = pygame.time.Clock()

        # To draw text
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Lucida Console', 16)

        # # Play background music
        # pygame.mixer.init()
        # pygame.mixer.music.load("Slow_Ride.mp3")
        # pygame.mixer.music.set_volume(0.5)
        # pygame.mixer.music.play(start=0, fade_ms=6500)

    def run(self):
        """ Creates a window and runs the simulation """

        while True:
            # Update simulation
            self.sim.update()

            # Detect collisions
            if self.sim.vehicles_on_map > 1:
                detected = self.sim.detect_collisions()
                if detected:
                    print(f"COLLISION")
                    return

            # Draw simulation
            self.draw()

            # Update window
            pygame.display.update()
            self.clock.tick(60)

            # Handle all events
            events = filter(lambda e: e.type in EVENTS, pygame.event.get())
            for event in events:
                # Quit program if window is closed
                if event.type == pygame.QUIT:
                    self.quit = True
                    return
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

                # for debugging purposes, remove after completion
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        # Zoom in on the intersection when pressing 1
                        self.zoom = 23
                    if event.key == pygame.K_2:
                        # Zoom out of the intersection when pressing 2
                        self.zoom = 7
                    if event.key == pygame.K_3:
                        # Slow down the simulation when pressing 3
                        self.sim.dt = min(self.sim.dt * 2, 0.5)
                    if event.key == pygame.K_4:
                        # Speed up the simulation when pressing 4
                        self.sim.dt = max(self.sim.dt / 2, 0.0001)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates
        :rtype: a list of 4 tuples (x, y) or a tuple (x, y)
        """
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        # return (int(self.width / 2 + x * self.zoom),
        #         int(self.height / 2 + y * self.zoom))
        return (int(self.width / 2 + (x + self.offset[0]) * self.zoom),
                int(self.height / 2 + (y + self.offset[1]) * self.zoom))

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates
        :rtype: a list of 4 tuples (x, y) or a tuple (x, y)
        """
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        # return (int((x - self.width / 2) / self.zoom),
        #         int((y - self.height / 2) / self.zoom))
        return (int(-self.offset[0] + (x - self.width / 2) / self.zoom),
                int(-self.offset[1] + (y - self.height / 2) / self.zoom))

    def draw_polygon(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255)) -> tuple:
        """Draws a rectangle center at *pos* with size *size* rotated anti-clockwise by *angle*.
        :returns screen coordinates (x, y)"""

        x, y = pos
        l, h = size

        if angle:
            cos, sin = np.cos(angle), np.sin(angle)

        def vertex(e1, e2):
            return (x + (e1 * l * cos + e2 * h * sin) / 2,
                    y + (e1 * l * sin - e2 * h * cos) / 2)

        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(-1, -1), (-1, 1), (1, 1), (1, -1)]])
        else:
            vertices = self.convert([vertex(*e)
                                     for e in [(0, -1), (0, 1), (2, 1), (2, -1)]])

        # for debugging purposes, remove after completion
        width = 0 if FILL_POLYGONS else 2
        x1, x2 = vertices[0][0], vertices[2][0]
        y1, y2 = vertices[0][1], vertices[2][1]
        screen_x = x1 + (x2 - x1) / 2
        screen_y = y1 + (y2 - y1) / 2

        draw.polygon(self.screen, color, vertices, width)
        return screen_x, screen_y

    def draw_arrow(self, pos, size, angle=None, cos=None, sin=None, color=(150, 150, 190)):
        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        self.draw_polygon(pos,
                          size,
                          cos=(cos - sin) / np.sqrt(2),
                          sin=(cos + sin) / np.sqrt(2),
                          color=color,
                          centered=False)
        self.draw_polygon(pos,
                          size,
                          cos=(cos + sin) / np.sqrt(2),
                          sin=(sin - cos) / np.sqrt(2),
                          color=color,
                          centered=False)

    def draw_axes(self, color=(100, 100, 100)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)
        draw.line(self.screen,
                  color,
                  self.convert((0, y_start)),
                  self.convert((0, y_end)))
        draw.line(self.screen,
                  color,
                  self.convert((x_start, 0)),
                  self.convert((x_end, 0)))

    def draw_grid(self, unit=50, color=(150, 150, 150)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit) + 1
        m_y = int(y_end / unit) + 1

        for i in range(n_x, m_x):
            draw.line(self.screen,
                      color,
                      self.convert((unit * i, y_start)),
                      self.convert((unit * i, y_end)))
        for i in range(n_y, m_y):
            draw.line(self.screen,
                      color,
                      self.convert((x_start, unit * i)),
                      self.convert((x_end, unit * i)))

    def draw_roads(self):
        for i, road in enumerate(self.sim.roads):
            # Draw road background
            screen_x, screen_y = self.draw_polygon(road.start,
                                                   (road.length, 3.7),
                                                   cos=road.angle_cos,
                                                   sin=road.angle_sin,
                                                   color=(180, 180, 220),
                                                   centered=False)

            # for debugging purposes, remove after completion
            if DRAW_ROAD_IDS:
                text_road_index = self.text_font.render(f'{i}', True, (0, 0, 0))
                self.screen.blit(text_road_index, (screen_x, screen_y))

            # Draw road arrow
            if road.length > 5:
                for j in np.arange(-0.5 * road.length, 0.5 * road.length, 10):
                    pos = (road.start[0] + (road.length / 2 + j + 3) * road.angle_cos,
                           road.start[1] + (road.length / 2 + j + 3) * road.angle_sin)

                    self.draw_arrow(pos, (-1.25, 0.2), cos=road.angle_cos, sin=road.angle_sin)

    def draw_vehicle(self, vehicle):
        road = self.sim.roads[vehicle.path[vehicle.current_road_index]]
        l, h = vehicle.length, 2
        sin, cos = road.angle_sin, road.angle_cos

        x = road.start[0] + cos * vehicle.x
        y = road.start[1] + sin * vehicle.x

        vehicle.position = x, y

        self.draw_polygon((x, y), (l, h), cos=cos, sin=sin, centered=True, color=vehicle.color)

        if vehicle.ems and not vehicle.crashed:
            if self.sim.t - self.last_ems_update_time >= 1:
                vehicle.change_ems_color()
                self.last_ems_update_time = self.sim.t
            self.draw_polygon((x, y), (l / 8, h * 0.75), cos=cos, sin=sin, centered=False, color=vehicle.ems_color)
            self.sim.frame_count += 1

    def draw_vehicles(self):
        for vehicle in self.sim.get_vehicles():
            self.draw_vehicle(vehicle)

    def draw_signals(self):
        for signal in self.sim.traffic_signals:
            for i, roads in enumerate(signal.roads):
                color = (0, 255, 0) if signal.current_cycle[i] else (255, 0, 0)
                for road in roads:
                    a = 0
                    position = ((1 - a) * road.end[0] + a * road.start[0],
                                (1 - a) * road.end[1] + a * road.start[1])
                    self.draw_polygon(position, (1, 3), cos=road.angle_cos, sin=road.angle_sin, color=color)

    def draw_status(self):
        def render(text, color=(0, 0, 0), background=None):
            return self.text_font.render(text, True, color, background)

        time = render(f'Time: {pygame.time.get_ticks() / 1000:.0f}s')
        simulation_time = render(f'Simulation Time: {self.sim.t:.2f}')

        # for debugging purposes, remove after completion
        vehicles_generated = render(f'Generated: {self.sim.vehicles_generated}')
        vehicles_on_map = render(f'On map: {self.sim.vehicles_on_map}')
        vehicles_reached_destination = render(f'Reached destination: {self.sim.vehicles_reached_destination}')
        average_journey_time = render(f'Average journey time: {self.sim.average_journey_time:.2f}')
        average_wait_time = render(f'Average wait time: {self.sim.average_wait_time:.2f}')

        self.screen.blit(time, (10, 10))
        self.screen.blit(simulation_time, (10, 35))

        # for debugging purposes, remove after completion
        self.screen.blit(vehicles_generated, (10, 60))
        self.screen.blit(vehicles_on_map, (10, 80))
        self.screen.blit(vehicles_reached_destination, (10, 100))
        self.screen.blit(average_journey_time, (10, 130))
        self.screen.blit(average_wait_time, (10, 150))

    def draw(self):
        self.screen.fill((240, 240, 240))

        if DRAW_GRID:
            # Minor gridlines
            self.draw_grid(10, (220, 220, 220))
            # Major gridlines
            self.draw_grid(100, (200, 200, 200))
            self.draw_axes()

        self.draw_roads()
        self.draw_vehicles()
        self.draw_signals()
        self.draw_status()
