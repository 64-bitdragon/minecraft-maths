import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import math
import amulet
from amulet.api.block import Block
from datetime import datetime
from distutils.dir_util import copy_tree
from functools import cmp_to_key

"""Path to existing minecraft world, don't put a / on the end!"""
level_path = "C:/Users/Home/AppData/Roaming/.minecraft/saves/New World"
game_version = ("java", (1, 20, 0))


def create_world():
    time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    copy_tree(level_path, level_path + time)
    minecraft_level = amulet.load_level(level_path + time)
    minecraft_level.level_wrapper.level_name += time

    return minecraft_level

class Parametric:
    def __init__(self, x_lambda, y_lambda, z_lambda, interpolation):
        self.x_lambda = x_lambda
        self.y_lambda = y_lambda
        self.z_lambda = z_lambda
        self.interpolation = interpolation

    def interpolate(self):
        t_range = np.linspace(-2 * math.pi, 2 * math.pi, self.interpolation)
        return [
            [math.floor(self.x_lambda(t)),
             math.floor(self.y_lambda(t)),
             math.floor(self.z_lambda(t))] for t in t_range]

    def render_minecraft(self):
        minecraft_level = create_world()

        t_range = np.linspace(-2 * math.pi, 2 * math.pi, self.interpolation)
        for t in t_range:
            block = Block("minecraft", "obsidian", )

            minecraft_level.set_version_block(
                math.floor(self.x_lambda(t)),
                math.floor(self.y_lambda(t)),
                math.floor(self.z_lambda(t)),
                "minecraft:overworld",
                game_version,
                block)

        minecraft_level.save()
        minecraft_level.close()

    def render_matplotlib(self):
        ax = plt.figure().add_subplot(projection='3d')

        t_range = np.linspace(-2 * math.pi, 2 * math.pi, 150)
        ax.plot(
            [self.x_lambda(t) for t in t_range],
            [self.z_lambda(t) for t in t_range], # y and z are flipped here so y is up
            [self.y_lambda(t) for t in t_range])
        plt.show()

    def render_matplotlib_animated(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        xdata, ydata, zdata = [], [], []
        ln, = ax.plot(xdata, ydata, zdata)

        def init():
            ax.set_xlim(-8, 8)
            ax.set_ylim(-9, 9)
            ax.set_zlim(-2 * math.pi, 2 * math.pi)
            return ln,

        def update(frame):
            xdata.append(self.x_lambda(frame))
            ydata.append(self.y_lambda(frame))
            zdata.append(self.z_lambda(frame))
            ln.set_data_3d(xdata, ydata, zdata)
            return ln,

        t_range = np.linspace(-2 * math.pi, 2 * math.pi, 1000)

        ani = FuncAnimation(fig, update, frames=t_range,
                            init_func=init, blit=True,
                            interval=1)
        plt.show()


Parametric(
    lambda t: 100 * math.sin(8 * t),
    lambda t: 50 * math.sin(t) - 10,
    lambda t: 100 * math.cos(9 * t),
    150).render_minecraft()
