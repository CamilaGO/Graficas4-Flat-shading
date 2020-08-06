import struct
import random
import numpy
from obj import Obj 
from collections import namedtuple

# implementacion de "vectores" para manejar menos variables en funciones y tener mejor orden de coordenadas
V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])

def sum(v0, v1):
  # suma dos vectores de 3 elementos 
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  # resta dos vectores de 3 elementos
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
  # multiplica un vector de 3 elementos por una constante
  return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):
  # reliza el producto punto de dos vectores de 3 elementos 
  # el resultado es un escalar
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v1, v2):
  return V3(
    v1.y * v2.z - v1.z * v2.y,
    v1.z * v2.x - v1.x * v2.z,
    v1.x * v2.y - v1.y * v2.x,
  )

def length(v0):
  # devuelve el tamaño (escalar) del vector
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
  #calcula la normal de un vector de 3 elementos
  v0length = length(v0)

  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices):
  # Se reciben *n vectores de 2 elementos para encontrar los x,y maximos y minimos
  # para poder hacer la boundingbox, es decir cubrir el poligono
  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]

  return (max(xs), max(ys), min(xs), min(ys))

def barycentric(A, B, C, P):
  # Este algoritmo de numeros baricentricos sirve para llena un poligono
  # Parametros: 3 vectores de 2 elementos y un punto
  # Return: 3 coordinadas baricentricas del punto segun el triangulo formado a partir de los vectores
  cx, cy, cz = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x), 
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(cz) < 1:
    return -1, -1, -1   # no es un triangulo de verdad, no devuelve nada afuera

  # [cx cy cz] == [u v 1]

  u = cx/cz
  v = cy/cz
  w = 1 - (cx + cy)/cz

  return w, v, u

def char(c):
  return struct.pack('=c', c.encode('ascii'))

def word(w):
  return struct.pack('=h', w)

def dword(d):
  return struct.pack('=l', d)

def color(r, g, b):
  return bytes([b, g, r])


BLACK = color(0,0,0)
WHITE = color(255,255,255)
RED = color(255, 0, 0)


# ===============================================================
# Render BMP file
# ===============================================================

class Render(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.current_color = WHITE
    self.glClear()
     #array del tamaño del buffer lleno de -infinitos

  def glClear(self):
    self.buffer = [
      [BLACK for x in range(self.width)] 
      for y in range(self.height)
    ]
    self.zbuffer = [
      [-float('inf') for x in range(self.width)] 
      for y in range(self.height)
    ]

  def finish(self, filename):
    f = open(filename, 'bw')

    # File header (14 bytes)
    f.write(char('B'))
    f.write(char('M'))
    f.write(dword(14 + 40 + self.width * self.height * 3))
    f.write(dword(0))
    f.write(dword(14 + 40))

    # Image header (40 bytes)
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

    # Pixel data (width x height x 3 pixels)
    for x in range(self.height):
      for y in range(self.width):
        f.write(self.buffer[x][y])

    f.close()

  def set_color(self, color):
    self.current_color = color

  def glColor(self, r=1, g=1, b=1):
    red = round(r*255)
    green = round(g*255)
    blue = round(g*255)
    self.current_color = color(red, green, blue)

  def point(self, x, y):
    try:
      self.buffer[y][x] = self.current_color
    except:
      # si esta "out of index"
      pass
    
  def glLine(self, x0, y0, x1, y1):
    # Funciones para aplicar la ecuacion de la recta y dibujar lineas con valores mayores de -1 a 1
    x1, y1 = x0, y0
    x2, y2 = x1, y1

    dy = abs(y2 - y1)
    dx = abs(x2 - x1)
    steep = dy > dx

    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dy = abs(y2 - y1)
    dx = abs(x2 - x1)

    offset = 0
    threshold = dx

    y = y1
    for x in range(x1, x2 + 1):
        if steep:
            self.point(y, x)
        else:
            self.point(x, y)
        
        offset += dy * 2
        if offset >= threshold:
            y += 1 if y1 < y2 else -1
            threshold += dx * 2


  def triangle(self, A, B, C):
    xmax, ymax, xmin, ymin = bbox(A, B, C)

    for x in range(xmin, xmax + 1):
      for y in range(ymin, ymax + 1):
        P = V2(x, y)
        w, v, u = barycentric(A, B, C, P)
        if w < 0 or v < 0 or u < 0:  # 0 es valido y estan el la orilla
          #el punto esta afuera y no se dibuja
          continue
          #se calcula la profunidad en z de cada punto
        z = A.z * w + B.z * u + C.z * v
        try:
          if z > self.zbuffer[x][y]:
            self.point(x,y)
            self.zbuffer[x][y] = z
        except:
          pass
    
  def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
    model = Obj(filename)

    light = V3(0, 0, 1)
    
    for face in model.faces:
      vcount = len(face)

      if vcount == 3:
        f1 = face[0][0] - 1
        f2 = face[1][0] - 1
        f3 = face[2][0] - 1

        v1 = V3(model.vertices[f1][0], model.vertices[f1][1], model.vertices[f1][2])
        v2 = V3(model.vertices[f2][0], model.vertices[f2][1], model.vertices[f2][2])
        v3 = V3(model.vertices[f3][0], model.vertices[f3][1], model.vertices[f3][2])

        x1 = round((v1.x * scale[0]) + translate[0])
        y1 = round((v1.y * scale[1]) + translate[1])
        z1 = round((v1.z * scale[2]) + translate[2])

        x2 = round((v2.x * scale[0]) + translate[0])
        y2 = round((v2.y * scale[1]) + translate[1])
        z2 = round((v2.z * scale[2]) + translate[2])

        x3 = round((v3.x * scale[0]) + translate[0])
        y3 = round((v3.y * scale[1]) + translate[1])
        z3 = round((v3.z * scale[2]) + translate[2])

        A = V3(x1, y1, z1)
        B = V3(x2, y2, z2)
        C = V3(x3, y3, z3)

        normal = norm(cross(sub(B, A), sub(C, A)))
        intensity = dot(normal, light)
        grey = round(255 * intensity)
        if grey < 0:
          continue 

        self.current_color = color(grey, grey, grey)

        self.triangle(A, B, C)

      else:
        f1 = face[0][0] - 1
        f2 = face[1][0] - 1
        f3 = face[2][0] - 1
        f4 = face[3][0] - 1   

        v1 = V3(model.vertices[f1][0], model.vertices[f1][1], model.vertices[f1][2])
        v2 = V3(model.vertices[f2][0], model.vertices[f2][1], model.vertices[f2][2])
        v3 = V3(model.vertices[f3][0], model.vertices[f3][1], model.vertices[f3][2])
        v4 = V3(model.vertices[f4][0], model.vertices[f4][1], model.vertices[f4][2])

        x1 = round((v1.x * scale[0]) + translate[0])
        y1 = round((v1.y * scale[1]) + translate[1])
        z1 = round((v1.z * scale[2]) + translate[2])

        x2 = round((v2.x * scale[0]) + translate[0])
        y2 = round((v2.y * scale[1]) + translate[1])
        z2 = round((v2.z * scale[2]) + translate[2])

        x3 = round((v3.x * scale[0]) + translate[0])
        y3 = round((v3.y * scale[1]) + translate[1])
        z3 = round((v3.z * scale[2]) + translate[2])

        x4 = round((v4.x * scale[0]) + translate[0])
        y4 = round((v4.y * scale[1]) + translate[1])
        z4 = round((v4.z * scale[2]) + translate[2])

        A = V3(x1, y1, z1)
        B = V3(x2, y2, z2)
        C = V3(x3, y3, z3)
        D = V3(x4, y4, z4)
        
        normal = norm(cross(sub(B, A), sub(C, A)))  # no necesitamos dos normales!!
        intensity = dot(normal, light)
        grey = round(255 * intensity)
        if grey < 0:
          continue # dont paint this face

        self.current_color = color(grey, grey, grey)
        self.triangle(A, B, C) 

        self.triangle(A, D, C)


  