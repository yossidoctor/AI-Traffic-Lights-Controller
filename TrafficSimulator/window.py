import numpy as np
import pygame
from pygame import draw

# for debugging purposes, todo: remove after completion
DRAW_ROAD_IDS = False  # True for debugging, False by default
DRAW_VEHICLE_IDS = False  # True for debugging, False by default
FILL_POLYGONS = True  # False for debugging, True by default
DRAW_GRIDLINES = False  # True for debugging, False by default

EVENTS = {pygame.QUIT,
          pygame.MOUSEBUTTONDOWN,
          pygame.MOUSEMOTION,
          pygame.MOUSEBUTTONUP,
          pygame.KEYDOWN}


class Window:
    def __init__(self, width, height, zoom, sim=None):
        self.sim = sim
        self.width = width
        self.height = height
        self.zoom = zoom

        # Flags
        self.collision_detected = False
        self.closed = False

        # Init display
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.offset = (0, 0)
        self.mouse_last = (0, 0)
        self.mouse_down = False
        pygame.display.flip()
        pygame.display.update()

        # Init display font
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Lucida Console', 16)

        # Init clock for fixed FPS
        self.clock = pygame.time.Clock()

        # # Init background music player todo: un-comment
        # pygame.mixer.init()
        # pygame.mixer.music.load("slow_ride.mp3")
        # pygame.mixer.music.set_volume(0.3)
        # pygame.mixer.music.play(start=0, fade_ms=8000)

    def update_display(self, episode_data=None):
        self.draw(episode_data)
        pygame.display.update()

    def run(self, action):
        """
        Applies the action and runs a single simulation cycle (update and collision check)
        @param action: the action to apply to the traffic signals
        """
        if action:
            self.sim.update_signals()

        # Update simulation
        self.sim.update()

        # Detect collisions
        self.sim.detect_collisions()

        # Handle UI events
        self.handle_window_events()

    def handle_window_events(self):
        """
        Handles UI events such as dragging the content, zooming in and out
        """
        events = filter(lambda e: e.type in EVENTS, pygame.event.get())
        for event in events:
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
            # for debugging purposes, todo: remove after completion
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # Zoom in on the intersection when pressing 1
                    self.zoom = 23
                if event.key == pygame.K_2:
                    # Zoom out of the intersection when pressing 2
                    self.zoom = 6
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
        return (int(-self.offset[0] + (x - self.width / 2) / self.zoom),
                int(-self.offset[1] + (y - self.height / 2) / self.zoom))

    def draw_polygon(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255)):
        """Draws a rectangle center at *pos* with size *size* rotated anti-clockwise by *angle*."""

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

        # draw.polygon(self.screen, color, vertices)
        # for debugging purposes, todo: remove after completion
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
        draw.line(self.screen, color, self.convert((0, y_start)), self.convert((0, y_end)), width=2)
        draw.line(self.screen, color, self.convert((x_start, 0)), self.convert((x_end, 0)), width=2)

    def draw_grid(self, unit=50, color=(150, 150, 150)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit) + 1
        m_y = int(y_end / unit) + 1

        for i in range(n_x, m_x):
            draw.line(self.screen, color, self.convert((unit * i, y_start)), self.convert((unit * i, y_end)))
        for i in range(n_y, m_y):
            draw.line(self.screen, color, self.convert((x_start, unit * i)), self.convert((x_end, unit * i)))

    def draw_roads(self):
        for i, road in enumerate(self.sim.roads):
            # Draw road background
            screen_x, screen_y = self.draw_polygon(road.start,
                                                   (road.length, 3.7),
                                                   cos=road.angle_cos,
                                                   sin=road.angle_sin,
                                                   color=(180, 180, 220),
                                                   centered=False)

            if DRAW_ROAD_IDS:
                # for debugging purposes, todo: remove after completion
                text_road_index = self.text_font.render(f'{i}', True, (0, 0, 0))
                self.screen.blit(text_road_index, (screen_x, screen_y))

            # Draw road arrow
            if road.length > 5:
                for j in np.arange(-0.5 * road.length, 0.5 * road.length, 10):
                    pos = (road.start[0] + (road.length / 2 + j + 3) * road.angle_cos,
                           road.start[1] + (road.length / 2 + j + 3) * road.angle_sin)

                    self.draw_arrow(pos, (-1.25, 0.2), cos=road.angle_cos, sin=road.angle_sin)

    def draw_vehicle(self, vehicle):
        """
        Updates the vehicle position attribute and draws it on the display
        @param vehicle: the Vehicle object to draw
        """
        road = self.sim.roads[vehicle.path[vehicle.current_road_index]]
        l, h = vehicle.length, 2
        sin, cos = road.angle_sin, road.angle_cos

        x = road.start[0] + cos * vehicle.x
        y = road.start[1] + sin * vehicle.x

        vehicle.position = x, y
        vehicle_color = (0, 0, 0) if vehicle.is_ems else (0, 0, 255)

        screen_x, screen_y = self.draw_polygon((x, y), (l, h), cos=cos, sin=sin, centered=True, color=vehicle_color)

        if DRAW_VEHICLE_IDS:
            # for debugging purposes, todo: remove after completion
            text_road_index = self.text_font.render(f'{vehicle.index}', True, (255, 255, 255), (0, 0, 0))
            self.screen.blit(text_road_index, (screen_x, screen_y))

        if vehicle.is_ems:
            if self.sim.t - vehicle.last_ems_update_time >= 1:
                # Update the EMS color every simulation second
                vehicle.change_ems_color()
                vehicle.last_ems_update_time = self.sim.t
            self.draw_polygon((x, y), (l / 8, h * 0.85), cos=cos, sin=sin, centered=False, color=vehicle.ems_color)

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

    def draw_status(self, episode_data=None):
        def render(text, color=(0, 0, 0), background=None):
            return self.text_font.render(text, True, color, background)

        time_render = render(f'Time: {pygame.time.get_ticks() / 1000:.0f}s')
        simulation_time_render = render(f'Simulation Time: {self.sim.t:.2f}')
        vehicles_generated_render = render(f'Generated: {self.sim.n_vehicles_generated}')
        vehicles_on_map_render = render(f'On map: {self.sim.n_vehicles_on_map}')
        average_wait_time_render = render(f'Average wait time: {self.sim.average_wait_time:.2f}')
        average_ems_wait_time_render = render(f'Average EMS wait time: {self.sim.average_ems_wait_time:.2f}')

        self.screen.blit(time_render, (10, 10))
        self.screen.blit(simulation_time_render, (10, 35))
        self.screen.blit(vehicles_generated_render, (10, 60))
        self.screen.blit(vehicles_on_map_render, (10, 80))
        self.screen.blit(average_wait_time_render, (10, 100))
        self.screen.blit(average_ems_wait_time_render, (10, 120))

        if episode_data:
            episode, n_episodes = episode_data
            episode_data_render = render(f'EPISODE: {episode}/{n_episodes}')
            self.screen.blit(episode_data_render, (10, 150))

    def draw(self, episode_data=None):
        self.screen.fill((240, 240, 240))
        if DRAW_GRIDLINES:
            # for debugging purposes, todo: remove after completion
            self.draw_grid(1, (220, 220, 220))
            self.draw_axes()
        self.draw_roads()
        self.draw_vehicles()
        self.draw_signals()
        self.draw_status(episode_data)
