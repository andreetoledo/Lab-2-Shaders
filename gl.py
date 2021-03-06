#Andree Toledo 18439
#Lab 2 Shaders


import struct
from obj import Obj
from collections import namedtuple

V2 = namedtuple("Vertex2", ["x", "y"])
V3 = namedtuple("Vertex3", ["x", "y", "z"])

def sum(v0, v1):
    """
        Input: 2 size 3 vectors
        Output: Size 3 vector with the per element sum
    """
    return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)


def sub(v0, v1):
    """
        Input: 2 size 3 vectors
        Output: Size 3 vector with the per element substraction
    """
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)


def mul(v0, k):
    """
        Input: 2 size 3 vectors
        Output: Size 3 vector with the per element multiplication
    """
    return V3(v0.x * k, v0.y * k, v0.z * k)


def dot(v0, v1):
    """
        Input: 2 size 3 vectors
        Output: Scalar with the dot product
    """
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z


def length(v0):
    """
        Input: 1 size 3 vector
        Output: Scalar with the length of the vector
    """
    return (v0.x ** 2 + v0.y ** 2 + v0.z ** 2) ** 0.5


def norm(v0):
    """
        Input: 1 size 3 vector
        Output: Size 3 vector with the normal of the vector
    """
    v0length = length(v0)

    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x / v0length, v0.y / v0length, v0.z / v0length)


def bbox(*vertices):
    xs = [vertex.x for vertex in vertices]
    ys = [vertex.y for vertex in vertices]

    xs.sort()
    ys.sort()

    xmin = xs[0]
    xmax = xs[-1]
    ymin = ys[0]
    ymax = ys[-1]

    return xmin, xmax, ymin, ymax


def cross(v1, v2):
    return V3(
        v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x,
    )


def barycentric(A, B, C, P):
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x), V3(B.y - A.y, C.y - A.y, A.y - P.y),
    )

    if abs(cz) < 1:
        return -1, -1, -1

    u = cx / cz
    v = cy / cz
    w = 1 - (cx + cy) / cz

    return w, v, u

def char(my_char):
    return struct.pack("=c", my_char.encode("ascii"))


def word(my_char):
    return struct.pack("=h", my_char)


def dword(my_char):
    return struct.pack("=l", my_char)


def normalize_color(colors_array):
    return [round(i * 255) for i in colors_array]
    
def normalizeColorArray(colors_array):
    return [round(i*255) for i in colors_array]

PLANET = "PLANET"
RING = "RING"

def color(r, g, b):
    return bytes([int(b * 255), int(g * 255), int(r * 255)])

class Render(object):
    # glInit dont needed, 'cause we have an __init__ func
    def __init__(self):
        self.framebuffer = []
        self.width = 800
        self.height = 800
        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_width = 800
        self.viewport_height = 800
        self.clear()

        self.zbuffer = [
            [-9999999 for x in range(self.width)] for y in range(self.height)
        ]
        # For shader use
        self.shape = None
        self.light = ()

    def point(self, x, y, color):
        self.framebuffer[y][x] = color

    def create_window(self, width, height):
        self.height = height
        self.width = width

    def viewport(self, x, y, width, height):
        # Setting viewport initial values
        self.viewport_x = x
        self.viewport_y = y
        self.viewport_height = height
        self.viewport_width = width

    def clear(self):
        BLACK = color(0, 0, 0)
        self.framebuffer = [
            [BLACK for x in range(self.width)] for y in range(self.height)
        ]

    def clear_color(self, r=1, g=1, b=1):
        # get normalized colors as array
        normalized = normalizeColorArray([r, g, b])
        clearColor = color(normalized[0], normalized[1], normalized[2])

        self.framebuffer = [
            [clearColor for x in range(self.width)] for y in range(self.height)
        ]

    def triangle(self, A, B, C, normals):
        xmin, xmax, ymin, ymax = bbox(A, B, C)

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    # point is outside
                    continue

                z = A.z * u + B.z * v + C.z * w

                r, g, b = self.shader(
                    x,
                    y,
                    barycentricCoords = (u, v, w),
                    normals=normals
                )

                shader_color = color(r, g, b)

                if z > self.zbuffer[x][y]:
                    self.point(x, y, shader_color)
                    self.zbuffer[x][y] = z

    def check_ellipse(self, x, y, a, b):
        return round((x ** 2) * (b ** 2)) + ((y ** 2) * (a ** 2)) <= round(a ** 2) * (
            b ** 2
        )

    def shader(self, x=0, y=0, barycentricCoords = (), normals=()):
        # Planet bounds:
        # Y: 240 - 560

        shader_color = 0, 0, 0
        current_shape = self.shape 
        u, v, w = barycentricCoords
        na, nb, nc = normals

        if current_shape == PLANET:
            if y < 280 or y > 520:
                shader_color = 156, 152, 164
            elif y < 320 or y > 480:
                shader_color = 146, 160, 180
            elif y < 360 or y > 420:
                shader_color = 105, 145, 170
            else:
                shader_color = 136, 190, 222
        # Ring bounds:
        # X - Hole: 200 - 600
        # Y - Hole: 380 - 420
        # So, if we use the equation of an ellipse, where a > b
        # the value must be a=200 and b=20
        elif current_shape == RING:
            # Filling from inside to outside
            x0, y0 = x - 400, y - 400
            a, b = 250, 25

            # First ellipse
            is_ellipse = self.check_ellipse(x0, y0, a, b)
            if is_ellipse:
                shader_color = 66, 76, 84
            else:
                # Second ellipse
                a += 50
                b += 5
                is_ellipse = self.check_ellipse(x0, y0, a, b)
                if is_ellipse:
                    shader_color = 94, 102, 116
                else:
                    # Third ellipse
                    a += 25
                    b += 5
                    is_ellipse = self.check_ellipse(x0, y0, a, b)
                    if is_ellipse:
                        shader_color = 0, 0, 0
                    else:
                        # Fourth ellipse
                        a += 75
                        b += 10
                        is_ellipse = self.check_ellipse(x0, y0, a, b)
                        if is_ellipse:
                            shader_color = 62, 72, 78

        b, g, r = shader_color

        b /= 255
        g /= 255
        r /= 255

        nx = na[0] * u + nb[0] * v + nc[0] * w
        ny = na[1] * u + nb[1] * v + nc[1] * w
        nz = na[2] * u + nb[2] * v + nc[2] * w

        normal = V3(nx, ny, nz)
        light = V3(0.700, 0.700, 0.750)

        intensity = dot(norm(normal), norm(light))

        b *= intensity
        g *= intensity
        r *= intensity

        if intensity > 0:
            return r, g, b
        else:
            return 0,0,0

    def load(self, filename="default.obj", translate=[0, 0], scale=[1, 1], shape=None):
        model = Obj(filename)
        self.shape = shape


        for face in model.faces:
            vcount = len(face)

            if vcount == 3:
                face1 = face[0][0] - 1
                face2 = face[1][0] - 1
                face3 = face[2][0] - 1

                v1 = model.vertices[face1]
                v2 = model.vertices[face2]
                v3 = model.vertices[face3]

                x1 = round((v1[0] * scale[0]) + translate[0])
                y1 = round((v1[1] * scale[1]) + translate[1])
                z1 = round((v1[2] * scale[2]) + translate[2])

                x2 = round((v2[0] * scale[0]) + translate[0])
                y2 = round((v2[1] * scale[1]) + translate[1])
                z2 = round((v2[2] * scale[2]) + translate[2])

                x3 = round((v3[0] * scale[0]) + translate[0])
                y3 = round((v3[1] * scale[1]) + translate[1])
                z3 = round((v3[2] * scale[2]) + translate[2])

                a = V3(x1, y1, z1)
                b = V3(x2, y2, z2)
                c = V3(x3, y3, z3)

                vn0 = model.normals[face1]
                vn1 = model.normals[face2]
                vn2 = model.normals[face3]

                self.triangle(a, b, c, normals=(vn0, vn1, vn2))

            else:
                face1 = face[0][0] - 1
                face2 = face[1][0] - 1
                face3 = face[2][0] - 1
                face4 = face[3][0] - 1

                v1 = model.vertices[face1]
                v2 = model.vertices[face2]
                v3 = model.vertices[face3]
                v4 = model.vertices[face4]

                x1 = round((v1[0] * scale[0]) + translate[0])
                y1 = round((v1[1] * scale[1]) + translate[1])
                z1 = round((v1[2] * scale[2]) + translate[2])

                x2 = round((v2[0] * scale[0]) + translate[0])
                y2 = round((v2[1] * scale[1]) + translate[1])
                z2 = round((v2[2] * scale[2]) + translate[2])

                x3 = round((v3[0] * scale[0]) + translate[0])
                y3 = round((v3[1] * scale[1]) + translate[1])
                z3 = round((v3[2] * scale[2]) + translate[2])

                x4 = round((v4[0] * scale[0]) + translate[0])
                y4 = round((v4[1] * scale[1]) + translate[1])
                z4 = round((v4[2] * scale[2]) + translate[2])

                a = V3(x1, y1, z1)
                b = V3(x2, y2, z2)
                c = V3(x3, y3, z3)
                d = V3(x4, y4, z4)

                vn0 = model.normals[face1]
                vn1 = model.normals[face2]
                vn2 = model.normals[face3]
                vn3 = model.normals[face4]

                self.triangle(a, b, c, normals=(vn0, vn1, vn2))
                self.triangle(a, c, d, normals=(vn0, vn2, vn3))

    def finish(self, filename="out.bmp"):
        # starts creating a new bmp file
        f = open(filename, "bw")

        f.write(char("B"))
        f.write(char("M"))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        # image header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        # Finishing placing points
        try:
            for x in range(self.height):
                for y in range(self.width):
                    f.write(self.framebuffer[x][y])
        except:
            print("Your obj file is too big. Try another scale/translate values")

        f.close()