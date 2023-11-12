import transformations as transformations
import numpy as np
import math
import amulet
from amulet.api.block import Block
from datetime import datetime
from distutils.dir_util import copy_tree

"""Path to existing minecraft world, don't put a / on the end!"""
level_path = "C:/Users/Home/AppData/Roaming/.minecraft/saves/New World"
game_version = ("java", (1, 20, 0))

length = 8
blocks = ['obsidian',
          'obsidian',
          'amethyst_block',
          'amethyst_block',
          'blue_ice',
          'blue_ice',
          'glowstone']

# Makes a copy of the existing level, appending the current time to the end of the name
time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
copy_tree(level_path, level_path + time)

# Then opens it as an Amulet level
minecraft_level = amulet.load_level(level_path + time)
minecraft_level.level_wrapper.level_name += time


class Line:
    def __init__(self, start, end, block):
        self.start = start.copy()
        self.end = end.copy()
        self.block = block
        self.interior_block = Block("minecraft", 'obsidian', )

        # have to make the position vector affine
        self.start.append(1)
        self.end.append(1)

        self.matrix = transformations.identity_matrix()

    def interpolate_line(self, a, b):
        x1, y1, z1, x2, y2, z2 = round(a[0]), round(a[1]), round(a[2]), round(b[0]), round(b[1]), round(b[2])
        yield x1, y1, z1

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        dz = abs(z2 - z1)
        if x2 > x1:
            xs = 1
        else:
            xs = -1
        if y2 > y1:
            ys = 1
        else:
            ys = -1
        if z2 > z1:
            zs = 1
        else:
            zs = -1

        # Driving axis is X-axis"
        if dx >= dy and dx >= dz:
            p1 = 2 * dy - dx
            p2 = 2 * dz - dx
            while x1 != x2:
                x1 += xs
                if p1 >= 0:
                    y1 += ys
                    p1 -= 2 * dx
                if p2 >= 0:
                    z1 += zs
                    p2 -= 2 * dx
                p1 += 2 * dy
                p2 += 2 * dz
                yield x1, y1, z1

        # Driving axis is Y-axis"
        elif dy >= dx and dy >= dz:
            p1 = 2 * dx - dy
            p2 = 2 * dz - dy
            while y1 != y2:
                y1 += ys
                if p1 >= 0:
                    x1 += xs
                    p1 -= 2 * dy
                if p2 >= 0:
                    z1 += zs
                    p2 -= 2 * dy
                p1 += 2 * dx
                p2 += 2 * dz
                yield x1, y1, z1

        # Driving axis is Z-axis"
        else:
            p1 = 2 * dy - dz
            p2 = 2 * dx - dz
            while z1 != z2:
                z1 += zs
                if p1 >= 0:
                    y1 += ys
                    p1 -= 2 * dz
                if p2 >= 0:
                    x1 += xs
                    p2 -= 2 * dz
                p1 += 2 * dy
                p2 += 2 * dx
                yield x1, y1, z1

    def render(self):
        temp_start = np.dot(self.start, self.matrix)
        temp_end = np.dot(self.end, self.matrix)

        # render the interior
        for x, y, z in self.interpolate_line(temp_start, temp_end):
            minecraft_level.set_version_block(
                round(x),
                round(y),
                round(z),
                "minecraft:overworld",
                game_version,
                self.interior_block)

        # render the ends
        for temp in [temp_start, temp_end]:
            minecraft_level.set_version_block(
                round(temp[0]),
                round(temp[1]),
                round(temp[2]),
                "minecraft:overworld",
                game_version,
                self.block)

    def transform(self, matrix):
        self.matrix = np.dot(self.matrix, matrix.T)


circumference = round(math.pi * length * 2)
outer_rotation = transformations.identity_matrix()

for i in range(circumference):
    block = blocks[i % len(blocks)]
    translate = transformations.identity_matrix()
    inner_rotation = transformations.identity_matrix()
    inner_rotation_3 = transformations.identity_matrix()
    inner_rotation_2 = transformations.identity_matrix()

    for j in range(1000):
        line = Line([0, -60, 0], [length, -60, 0], Block("minecraft", block, ))
        line.transform(translate)
        line.transform(outer_rotation)
        line.transform(inner_rotation)
        line.transform(inner_rotation_2)
        line.transform(inner_rotation_3)

        line.render()

        translate = np.dot(translate, transformations.translation_matrix([0, 1, 0]))

        inner_rotation = np.dot(inner_rotation, transformations.rotation_matrix(1 / length, [0, 1, 0]))
        inner_rotation_2 = np.dot(
            inner_rotation_2,
            transformations.rotation_matrix(
                1 / length,
                [0, 1, 0],
                [length, 0, 0]))
        inner_rotation_3 = np.dot(
            inner_rotation_3,
            transformations.rotation_matrix(
                0.05 / length,
                [1, 0, 0],
                [3 * length, 0, 0]))

    outer_rotation = np.dot(outer_rotation, transformations.rotation_matrix(1 / length, [0, 1, 0]))

minecraft_level.save()
minecraft_level.close()
