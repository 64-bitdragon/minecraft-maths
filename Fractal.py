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

# Makes a copy of the existing level, appending the current time to the end of the name
time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
copy_tree(level_path, level_path + time)

# Then opens it as an Amulet level
minecraft_level = amulet.load_level(level_path + time)
minecraft_level.level_wrapper.level_name += time


def render_cube(x, y, z, level):
    print(level)
    for a, b, c in interpolate_cobe(x, y, z, level):
        if level == 0:
            minecraft_level.set_version_block(
                a,
                b,
                c,
                "minecraft:overworld",
                game_version,
                Block("minecraft", 'stone', ))
        else:
            render_cube(a, b, c, level - 1)


def interpolate_cobe(x, y, z, level):
    level_exp = 3 ** level

    for j in [0, 2]:
        for k in [0, 2]:
            for i in range(3):
                yield x + i * level_exp, y + j * level_exp, z + k * level_exp

    for i in [0, 2]:
        yield x + i * level_exp, y, z + 1 * level_exp
        yield x + i * level_exp, y + 2 * level_exp, z + 1 * level_exp
        yield x + i * level_exp, y + 1 * level_exp, z
        yield x + i * level_exp, y + 1 * level_exp, z + 2 * level_exp


render_cube(0, -60, 0, 3)

minecraft_level.save()
minecraft_level.close()