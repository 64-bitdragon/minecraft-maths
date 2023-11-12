import numpy as np
import math
import amulet
from amulet.api.block import Block
from datetime import datetime
from distutils.dir_util import copy_tree
import open3d as o3d

"""Path to existing minecraft world, don't put a / on the end!"""
level_path = "C:/Users/Home/AppData/Roaming/.minecraft/saves/New World"
game_version = ("java", (1, 20, 0))

"""
    When set to true, the inside of the triangles will be filled
    Otherwise, only the outlines will be rendered
"""
fill_triangles = True

# Makes a copy of the existing level, appending the current time to the end of the name
time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
copy_tree(level_path, level_path + time)

# Then opens it as an Amulet level
minecraft_level = amulet.load_level(level_path + time)
minecraft_level.level_wrapper.level_name += time


class Parametric:
    def __init__(self, x_lambda, y_lambda, z_lambda):
        self.x_lambda = x_lambda
        self.y_lambda = y_lambda
        self.z_lambda = z_lambda

    def interpolate(self, interpolation):
        t_range = np.linspace(-2 * math.pi, 2 * math.pi, interpolation)
        return [
            [math.floor(self.x_lambda(t)),
             math.floor(self.y_lambda(t)),
             math.floor(self.z_lambda(t))] for t in t_range]


class MeshRenderer:
    def render_triangle(self, a, b, c):
        block = Block("minecraft", "obsidian", )
        self.render_line(a, b, block)
        self.render_line(b, c, block)
        self.render_line(a, c, block)

    def render_area(self, a, b, c):
        block = Block("minecraft", "glowstone", )

        for x, y, z in self.interpolate_line(b, c):
            self.render_line(a, [x, y, z], block)

        for x, y, z in self.interpolate_line(a, c):
            self.render_line(b, [x, y, z], block)

        for x, y, z in self.interpolate_line(a, b):
            self.render_line(c, [x, y, z], block)

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

    def render_line(self, p1, p2, block):
        for x, y, z in self.interpolate_line(p1, p2):
            minecraft_level.set_version_block(
                int(x),
                int(y),
                int(z),
                "minecraft:overworld",
                game_version,
                block)


parametric = Parametric(
        lambda t: 100 * math.sin(8 * t),
        lambda t: 50 * math.sin(t) - 10,
        lambda t: 100 * math.cos(9 * t))

# generate our point cloud from our parametric equation
point_cloud = np.asarray(parametric.interpolate(150))
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(point_cloud)

# sort out the vertex normals
pcd.estimate_normals()
pcd.orient_normals_towards_camera_location(pcd.get_center())
pcd.normals = o3d.utility.Vector3dVector( - np.asarray(pcd.normals))

# surface reconstruction using Poisson reconstruction
mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=3, scale=1.2)

# render
renderer = MeshRenderer()

vertices = np.asarray(mesh.vertices)
if fill_triangles:
    for triangle in np.asarray(mesh.triangles):
        tv = vertices[triangle]
        renderer.render_area(tv[0], tv[1], tv[2])

for triangle in np.asarray(mesh.triangles):
    tv = vertices[triangle]
    renderer.render_triangle(tv[0], tv[1], tv[2])

# save
minecraft_level.save()
minecraft_level.close()
