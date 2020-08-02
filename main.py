"""
Paula Camila Gonzalez Ortega
18398
"""
from gl import Render

posX = 250
posY = 250
width = 800
height = 600

bitmap = Render(width, height) #los ultimos tres son los colores son los del background

##bitmap.glViewPort(posX, posX, width-500 , height-500)
##bitmap.glClearColor(0, 0, 0) #background color
bitmap.glClear()
bitmap.glColor(1, 1, 1) #estos colores son los que se usaran en Vertex
bitmap.load('./face.obj', (25, 5, 0), (15, 15,15))


bitmap.finish('fillf.bmp')