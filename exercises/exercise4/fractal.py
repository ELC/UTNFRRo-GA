import turtle
import colorsys
import os
from math import cos, sin, radians

import svgwrite
from svg_turtle import SvgTurtle

def create_l_system(iters, axiom, rules):
    start_string = axiom
    if iters == 0:
        return axiom
    end_string = ""
    for _ in range(iters):
        end_string = "".join(rules[i] if i in rules else i for i in start_string)
        start_string = end_string

    return end_string


def draw_l_system(t, instructions, angle, distance, color):
    steps = len([i for i in instructions if i in "FB"])
    step = 1 / steps
    i = 0
    for cmd in instructions:
        if cmd in "FB" and color:
            r, g, b = colorsys.hsv_to_rgb(i, 1.0, 1.0)
            i += step
            t.color(r, g, b)
        if cmd == 'F':
            t.forward(distance)
        elif cmd == 'B':
            t.backward(distance)
        elif cmd == '+':
            t.right(angle)
        elif cmd == '-':
            t.left(angle)

def draw_background(t):
    """ Draw a background rectangle. """
    ts = t.getscreen()
    canvas = ts.getcanvas()
    height = ts.getcanvas()._canvas.winfo_height()
    width = ts.getcanvas()._canvas.winfo_width()

    turtleheading = t.heading()
    turtlespeed = t.speed()
    penposn = t.position()
    penstate = t.pen()

    t.penup()
    t.speed(0)  # fastest
    t.goto(-width/2-2, -height/2+3)
    t.fillcolor(turtle.Screen().bgcolor())
    t.begin_fill()
    t.setheading(0)
    t.forward(width)
    t.setheading(90)
    t.forward(height)
    t.setheading(180)
    t.forward(width)
    t.setheading(270)
    t.forward(height)
    t.end_fill()

    t.penup()
    t.setposition(*penposn)
    t.pen(penstate)
    t.setheading(turtleheading)
    t.speed(turtlespeed)


def calc_length_height(instructions, angle, correction_angle):
    current_angle = correction_angle
    x_offset = 0
    y_offset = 0
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    for inst in instructions:
        if inst == "F":
            x_offset += cos(radians(current_angle))
            y_offset += sin(radians(current_angle))
        elif inst == "B":
            x_offset -= cos(radians(current_angle))
            y_offset -= sin(radians(current_angle))
        elif inst == "+":
            current_angle -= angle
        elif inst == "-":
            current_angle += angle
        max_x = max(max_x, x_offset)
        min_x = min(min_x, x_offset)
        max_y = max(max_y, y_offset)
        min_y = min(min_y, y_offset)
    
    width = abs(max_x) + abs(min_x)
    height = abs(max_y) + abs(min_y)


    return width, height, abs(min_x), abs(min_y)


def save_svg(inst, angle, length, color, filename, iterations,
             width, height, x_offset, y_offset, offset_angle, size):

    drawing = svgwrite.Drawing(f"{filename}/{filename}_{str(iterations).zfill(2)}.svg", size=(f"{width}px", f"{height}px"))
    drawing.add(drawing.rect(fill='black', size=("100%", "100%")))
    t = SvgTurtle(drawing)
    turtle.Turtle._screen = t.screen
    turtle.Turtle._pen = t

    t.up()    
    t.backward(-x_offset)
    t.left(90)
    t.backward(-y_offset)
    t.left(offset_angle)
    t.down()
    t.speed(0)
    t.pensize(size)

    draw_l_system(t, inst, angle, length, color)

    t.hideturtle()

    drawing.save()
    
def save_ps(t, filename, width, height, iterations):

    cv = t.getscreen().getcanvas()
    cv.postscript(file=f"{filename}/{filename}_{iterations}.ps", colormode='color')

    try: # Needs Image Magick Convert and GhostScript
        command = f"convert -density 1000 -resize {int(width+0.5)}x{int(height+0.5)} -flatten -background black -units pixelsperinch {filename}/{filename}_{iterations}.ps {filename}/{filename}_{iterations}.png"
        print(command)
        os.system(command)
    except:
        pass
    

def main(iterations, axiom, rules, angle, length=None, color=True, size=None, correction_angle=0,
        y_offset=None, x_offset=None, offset_angle=None, inverted=False, flip_h=False, flip_v=False,
        filename=None, width=None, height=None, margin=None, aspect_ratio=None, fast=False):

    inst = create_l_system(iterations, axiom, rules)

    width_, height_, min_x, min_y = calc_length_height(inst, angle, correction_angle)

    if width_ == 0 and height_ == 0:
        return

    if aspect_ratio is None:
        if 0 in [width_, height_]:
            aspect_ratio = 1
        else:
            aspect_ratio = width_ / height_

    if width is None and height:
        width = height / aspect_ratio

    if height is None and width:
        height = width / aspect_ratio
    
    if margin is None:
        margin = 35

    if offset_angle is None:
        offset_angle = -90

    if length is None:
        if width_ > height_:
            length = (width - 2 * margin) / width_
        else:
            length = (height - 2 * margin) / height_
    
    if width_ * length > width:
        length = (width - 2 * margin) / width_
    elif height_ * length > height:
        length = (height - 2 * margin) / height_
    
    if x_offset is None:
        if width_ >= height_  and (width - width_) <= width_ - 2 * margin :
            x_offset = -(width / 2 - margin) + min_x * length
        else:
            x_offset = -(width / 2) + (width - width_ * length) / 2 + min_x * length
    
    if y_offset is None:
        if height_ >= width_ and (height - height_) <= height_ - 2 * margin :
            y_offset = -(height / 2 - margin) + min_y * length
        else:
            y_offset = -(height / 2) + (height - height_ * length) / 2 + min_y * length

    if inverted:
        inst = inst.replace('+', '$')
        inst = inst.replace('-', '+')
        inst = inst.replace('$', '-')
        inst = inst.replace('F', '$')
        inst = inst.replace('B', 'F')
        inst = inst.replace('$', 'B')
    
    if flip_h:
        inst = inst.replace('F', '$')
        inst = inst.replace('B', 'F')
        inst = inst.replace('$', 'B')
        y_offset = - y_offset

    if flip_v:
        inst = inst.replace('+', '$')
        inst = inst.replace('-', '+')
        inst = inst.replace('$', '-')
        y_offset = - y_offset

    print(f"Width: {width_} - Height:{height_ }")

    print(length)
    print(x_offset, y_offset)

    if size is None:
        if length < 3:
            size = 1
        elif length < 12:
            size = 2
        elif length < 25:
            size = 3
        else:            
            size = 5
    
    if not filename is None:
        filename = filename.lower().replace(" ","-")
        if not os.path.exists(filename):
            os.makedirs(filename)

    if fast:
        save_svg(inst, angle, length, color, filename, iterations,
             width, height, x_offset, y_offset, offset_angle, size)
        return

    t = turtle.Turtle()
    wn = turtle.Screen()
    wn.setup(width, height)

    if color:
        wn.bgcolor('black')

    if not filename is None:
        draw_background(t)

    t.up()    
    t.backward(-x_offset)
    t.left(90)
    t.backward(-y_offset)
    t.left(offset_angle)
    t.down()
    t.speed(0)
    t.pensize(size)
    draw_l_system(t, inst, angle, length, color)
    t.hideturtle()
    
    if not filename is None:

        save_ps(t, filename, width, height, iterations)

    wn.exitonclick()

def create_gifs(filename, width):
    command = f"cd {filename} && convert -loop 0 -delay 6 -morph 15 *.svg {filename}_{width}x{width}_15fps.gif"
    print(command)
    os.system(command)
    # command = f"cd {filename} && convert -loop 0 -delay 3 -morph 30 *.svg {filename}_{width}x{width}_30fps.gif"
    # print(command)
    # os.system(command)
    # command = f"cd {filename} && convert -loop 0 -delay 2 -morph 60 *.svg {filename}_{width}x{width}_60fps.gif"
    # print(command)
    # os.system(command)


# Global parameters

width = 320

# 32-segment curve
title = "32-segment curve"
axiom = "F+F+F+F"
rules = {"F":"-F+F-F-F+F+FF-F+F+FF+F-F-FF+FF-FF+F+F-FF-F-F+FF-F-F+F+F-F+"}
iterations = 4 # TOP: 3
angle = 90

for iterations in range( 3 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width) 

# box fractal
title = "box fractal"
axiom = "F-F-F-F"
rules = {"F":"F-F+F+F-F"}
iterations = 4 # TOP: 6
angle = 90

for iterations in range( 6 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, width=width, filename=title, fast=True)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Dragon curve
title = "Dragon curve center"
axiom = "FX"
rules = {"X":"X+YF+", "Y":"-FX-Y"}
iterations = 8 # TOP: 16
angle = 90

for iterations in range(16 + 1):
    offset_angle = -90 + 45 * iterations
    correction_angle = 45 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
            width=width, height=width, filename=title, fast=True) 

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Dragon curve 
title = "TwinDragon curve center"
axiom = "FX+FX"
rules = {"X":"X+YF+", "Y":"-FX-Y"}
iterations = 6 # TOP: 16
angle = 90

for iterations in range(16 + 1):
    offset_angle = -90 + 45 * iterations
    correction_angle = 45 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
            width=width, height=width, filename=title, fast=True) 

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Dragon curve
title = "ThreeDragon curve center"
axiom = "FX+FX+FX"
rules = {"X":"X+YF+", "Y":"-FX-Y"}
iterations = 7 # TOP: 15
angle = 90

for iterations in range(15 + 1):
    offset_angle = -90 + 45 * iterations
    correction_angle = 45 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
        width=width, height=width, filename=title, fast=True) 

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# TerDragon curve center
title = "TerDragon curve center"
axiom = "F"
rules = {"F":"F-F+F"}
iterations = 5 # TOP: 10
angle = 120

for iterations in range(10 + 1):
    offset_angle = 90 - 30 * iterations
    correction_angle = 180 - 30 * iterations


    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
        width=width, height=width, filename=title, fast=True) 

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Lévy C curve
title = "Lévy C curve"
axiom = "F"
rules = {"F":"+F--F+"}
iterations = 10 # TOP: 16
angle = 45

for iterations in range(16 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, height=width,  filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Hilbert curve
title = "Hilbert curve"
axiom = "L"
rules = {"L":"+RF-LFL-FR+", "R":"-LF+RFR+FL-"}
iterations = 8 # TOP: 9
angle = 90
y_offset = -190
angle_offset = 90

for iterations in range( 9 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, inverted=True,
        offset_angle=angle_offset, y_offset=y_offset, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)        

# Hilbert curve II
title = "Hilbert curve II"
axiom = "X"
rules = {"X":"XFYFX+F+YFXFY-F-XFYFX", "Y":"YFXFY-F-XFYFX+F+YFXFY"}
iterations = 4 # TOP: 6
angle = 90
y_offset = -190
angle_offset = 0

for iterations in range( 6 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, 
        offset_angle=angle_offset, y_offset=y_offset, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# 2 8 26 80 242 728

# Koch snowflake
title = "Koch snowflake"
axiom = "F--F--F"
rules = {"F":"F+F--F+F"}
iterations = 4 # TOP: 7
angle = 60

for iterations in range( 7 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# 1 3 9 27 81 243 729

# Peano curve
title = "Peano curve"
axiom = "F"
rules = {"F":"F+F-F-F-F+F+F+F-F"}
iterations = 2 # TOP: 5
angle = 90

for iterations in range( 5 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# 1 3 9 27 81 243 729

# Peano-Gosper curve
title = "Peano-Gosper curve center"
axiom = "FX"
rules = {"X":"X+YF++YF-FX--FXFX-YF+", "Y":"-FX+YFYF++YF+FX--FX-Y"}
iterations = 4 # TOP: 6
angle = 60

for iterations in range( 6 + 1):
    offset_angle = -90 + 15 * iterations
    correction_angle = 15 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
        aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# ? 2.5 7 20 55 150

# quadratic Koch island
title = "quadratic Koch island center"
axiom = "F+F+F+F"
rules = {"F":"F-F+F+FFF-F-F+F"}
iterations = 2 # TOP: 4
angle = 90

for iterations in range( 4 + 1):
    offset_angle = -105 + 15 * iterations
    correction_angle = -15 + 15 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
        aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# 1 7 31 127

# Sierpiński arrowhead 
title = "Sierpiński arrowhead"
axiom = "YF"
rules = {"X":"YF+XF+Y", "Y":"XF-YF-X"}
iterations = 1 # TOP: 10
angle = 60

for iterations in range(10 + 1):
    flip_v = True
    correction_angle = 0 if iterations % 2 == 0 else -60
    offset_angle = -90 if iterations % 2 == 0 else -30
        
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, flip_v=True, 
        correction_angle=correction_angle, offset_angle=offset_angle, width=width, height=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Sierpiński curve
title = "Sierpiński curve"
axiom = "F+XF+F+XF"
rules = {"X":"XF-F+F-XF+F+XF-F+F-X"}
iterations = 4 # TOP: 8
angle = 90

for iterations in range( 8 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Siepiński sieve
title = "Siepiński sieve"
axiom = "FXF--FF--FF"
rules = {"F":"FF", "X":"--FXF++FXF++FXF--"}
iterations = 7 # TOP: 8
angle = 60

for iterations in range( 8 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Quadratic Snowflake
title = "Quadratic Snowflake"
axiom = "F--F"
rules = {"F":"F-F+F+F-F"}
iterations = 4 # TOP: 6
angle = 90
angle_offset = -90

for iterations in range( 6 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, height=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Board
title = "Board"
axiom = "F+F+F+F"
rules = {"F":"FF+F+F+F+FF"}
iterations = 3 # TOP: 5
angle = 90

for iterations in range( 5 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Cross
title = "Cross center"
axiom = "F+F+F+F"
rules = {"F":"F+FF++F+F"}
iterations = 3 # TOP: 6
angle = 90

for iterations in range( 6 + 1):
    offset_angle = -120 + 30 * iterations
    correction_angle = -30 + 30 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
        aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Cross 2 
title = "Cross 2"
axiom = "F+F+F+F"
rules = {"F":"F+F-F+F+F"}
iterations = 3 # TOP: 6
angle = 90

for iterations in range( 6 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Pentaplexity
title = "Pentaplexity"
axiom = "F++F++F++F++F"
rules = {"F":"F++F++F+++++F-F++F"}
iterations = 1 # TOP: 5
angle = 36

for iterations in range( 5 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Tiles 
title = "Tiles"
axiom = "F+F+F+F"
rules = {"F":"FF+F-F+F+FF"}
iterations = 3 # TOP: 4
angle = 90

for iterations in range( 4 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Rings
title = "Rings"
axiom = "F+F+F+F"
rules = {"F":"FF+F+F+F+F+F-F"}
iterations = 2 # TOP: 4
angle = 90

for iterations in range( 4 + 1):
    offset_angle = -90 + 15 * iterations
    correction_angle = 15 * iterations

    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Krishna Anklets
title = "Krishna Anklets"
axiom = " -X--X"
rules = {"X":"XFX--XFX"}
iterations = 3 # TOP: 9
angle = 45

for iterations in range( 9 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Triangle TODO
title = "Triangle center"
axiom = "F+F+F"
rules = {"F":"F-F+F"}
iterations = 2 # TOP: 9
angle = 120

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

for iterations in range( 9 + 1):
    offset_angle = -90 - 30 * iterations
    correction_angle = -30 * iterations

    main(iterations, axiom, rules, angle, correction_angle=correction_angle, offset_angle=offset_angle, 
        aspect_ratio=1, fast=True, width=width, filename=title)

# Quadratic Gosper
title = "Quadratic Gosper"
axiom = "YF"
rules = {"X": "XFX-YF-YF+FX+FX-YF-YFFX+YF+FXFXYF-FX+YF+FXFX+YF-FXYF-YF-FX+FX+YFYF-", 
         "Y": "+FXFX-YF-YF+FX+FXYF+FX-YFYF-FX-YF+FXYFYF-FX-YFFX+FX+YF-YF-FX+FX+YFY"}
iterations = 2 # TOP: 3
angle = 90

for iterations in range( 3 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Crystal
title = "Crystal"
axiom = "F+F+F+F"
rules = {"F":"FF+F++F+F"}
iterations = 3 # TOP: 6
angle = 90

for iterations in range( 6 + 1):
    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True, filename=title)

filename = title.lower().replace(" ","-")
create_gifs(filename, width)

# Moore Curve
title = "Moore Curve"
axiom = "LFL-F-LFL"
rules = {"L":"+RF-LFL-FR+", "R":"-LF+RFR+FL-"}
iterations = 0 # TOP: 8
angle = 90
y_offset = 190
angle_offset = 0
margin = 35

for iterations in range( 8 + 1):
    # Original: -width / 2 + margin + (width - 2 * margin) / (2**(iterations+1) - 1) * (2**(iterations) - 1)
    x_offset = - (width - 2 * margin) / (2 * (2 ** (iterations + 1) - 1))
    if iterations == 0:
        x_offset = -190

    main(iterations, axiom, rules, angle, aspect_ratio=1, fast=True, width=width, flip_v=True,
        offset_angle=angle_offset, y_offset=y_offset, x_offset=x_offset, filename=title)
    
filename = title.lower().replace(" ","-")
create_gifs(filename, width)   