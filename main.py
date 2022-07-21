from trafficSimulator import Window
from two_way_intersection import two_way_intersection

# for debugging purposes, remove after completion
RESET_UPON_COLLISION = False  # False for debugging, True by default

sim = two_way_intersection()

# win = Window(sim, width=1200, height=900, zoom=7)  # Monitor
win = Window(sim, width=900, height=600, zoom=7)  # 1080p 14" laptop monitor with 150% scaling

while True:
    win.run()
    if win.quit:
        break
    elif RESET_UPON_COLLISION:
        win.sim = two_way_intersection()
