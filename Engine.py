#Andree Toledo 18439
#Lab 2 Shaders

from gl import Render


render = Render()
PLANET = "PLANET"

render.load("sphere.obj", translate=(400, 400, 0), scale=(250, 250, 350), shape=PLANET)
render.finish(filename="output.bmp")