"""
Paula Camila Gonzalez Ortega
18398
"""
from gl import Render, V3

posX = 250
posY = 250
width = 800
height = 600

#bitmap = Render(width, height) #los ultimos tres son los colores son los del background

r = Render(1200, 1200)
#r.triangle(V3(10, 70, 1),  V3(50, 160, 1), V3(70, 80, 1))
#r.triangle(V3(180, 50, 1), V3(150, 1, 1),  V3(70, 180, 1))
#r.triangle(V3(180, 150, 1), V3(120, 160, 1), V3(130, 180, 1))

##bitmap.glViewPort(posX, posX, width-500 , height-500)
##bitmap.glClearColor(0, 0, 0) #background color
#bitmap.glClear()
#bitmap.glColor(1, 1, 1) #estos colores son los que se usaran en Vertex
r.load('./face.obj', (600, 500, 1), (15, 15, 15))


r.finish('cara.bmp')