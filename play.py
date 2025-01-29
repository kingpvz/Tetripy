import tkinter
from tkinter import messagebox
import random
import ctypes
import sys
import data.info as info
import os
ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )

w = tkinter.Tk()
w.title("Tetripy "+info.VERSION)
w.resizable(0,0)
def die():
    w.destroy()
    sys.exit()
w.protocol("WM_DELETE_WINDOW", die)
w.iconbitmap("data/favicon.ico")

c = tkinter.Canvas(w, width=610, height=607, bg="#fff")
c.pack()
divisionLine = c.create_line(410, 0, 410, 610, fill="#333", width=3)
ptsText = c.create_text(510, 30, text="Points: 0", fill="#333", font="Bahnschrift 18 bold")
totalptsText = c.create_text(510, 55, text="Total Points: 0", fill="#333", font="Bahnschrift 10")
speedText = c.create_text(510, 80, text="Speed: 1", fill="#333", font="Bahnschrift 14")

mode = 0
with open("config.txt", 'r') as f:
    for i in f.readlines():
        i = i.strip().split(":")
        if i[0] == "mode":
            if i[1] == "dark": mode = 1

def rotate(commands):
    lines = commands.split(' next ')
    grid = [line.split() for line in lines]
    rotated_grid = list(zip(*grid[::-1]))
    rotated_commands = []
    for row in rotated_grid:
        rotated_commands.append(" ".join(row))
    return ' next '.join(rotated_commands)

class Shape:
    global c
    def __init__(this,params):
        this.params = params
        this.shape = [[]]
        this.builder = {"row":0,"col":0}
        commands = params.split()
        for i in commands: this.command(i)
        this.size = len(this.shape[0]),len(this.shape)

    def command(this, x):
        if x=="put":
            this.shape[this.builder["col"]].append(True)
            this.builder["row"]+=1
        elif x=="skip":
            this.shape[this.builder["col"]].append(False)
            this.builder["row"]+=1
        elif x=="next":
            this.builder["row"]=0
            this.shape.append([])
            this.builder["col"]+=1

    def get(this): return this.shape

class Object:
    global c, columns, speed
    def __init__(this, shape, color, border, pos):
        this.moving = True
        this.switched = False
        this.shape = shape
        this.size = list(this.shape.size)
        this.position=[pos,0]
        this.block=[[]]
        this.datacont=(pos,color,border)
        this.build(this.shape)
        c.after(speed, this.fall)
        c.bind_all('a',this.left)
        c.bind_all('s',this.bottom)
        c.bind_all('d',this.right)
        c.bind_all('w',this.switch)
        c.bind_all('A',this.left)
        c.bind_all('S',this.bottom)
        c.bind_all('D',this.right)
        c.bind_all('W',this.switch)
        c.bind_all('<space>',this.switch)
        c.bind_all('<Left>',this.left)
        c.bind_all('<Down>',this.bottom)
        c.bind_all('<Right>',this.right)
        c.bind_all('<Up>',this.switch)
        c.tag_bind(button_left, '<ButtonPress-1>', this.left)
        c.tag_bind(text_left, '<ButtonPress-1>', this.left)
        c.tag_bind(button_down, '<ButtonPress-1>', this.bottom)
        c.tag_bind(text_down, '<ButtonPress-1>', this.bottom)
        c.tag_bind(button_right, '<ButtonPress-1>', this.right)
        c.tag_bind(text_right, '<ButtonPress-1>', this.right)
        c.tag_bind(button_switch, '<ButtonPress-1>', this.switch)
        c.tag_bind(text_switch, '<ButtonPress-1>', this.switch)

    def fall(this):
        this.position[1]+=1
        for i in this.block:
            for j in i:
                if j: c.move(j, 0, 20)
        if this.checkGrid("v"):
            c.after(speed, this.fall)
        else:
            this.moving = False
            r = this.updateGrid()
            if r: place()

    def left(this,e,cond=False):
        condition = (this.position[0]>0 and this.moving) if cond else this.checkGrid("<")
        if condition:
            this.position[0]-=1
            for i in this.block:
                for j in i:
                    if j: c.move(j, -20, 0)
                    
    def right(this,e,cond=False):
        condition = (this.position[0]<20-this.size[0] and this.moving) if cond else this.checkGrid(">")
        if condition:
            this.position[0]+=1
            for i in this.block:
                for j in i:
                    if j: c.move(j, 20, 0)

    def bottom(this,e):
        if this.checkGrid("vv"):
            this.position[1]+=1
            for i in this.block:
                for j in i:
                    if j: c.move(j, 0, 20)

    def switch(this,e):
        if not this.switched and (this.size[1]+this.position[1]<30 and this.position[1]>=this.size[0]-1):
            this.switched = True
            size=this.size
            position=this.position
            for i in this.block:
                for j in i:
                    if j: c.delete(j)
            this.block=[[]]
            this.shape = Shape(rotate(this.shape.params))
            this.size = list(this.shape.size)
            if this.size[0]!=size[0]:this.position[0]-=this.size[0]-size[0]
            if this.size[1]!=size[1]:this.position[1]-=this.size[1]-size[1]
            while this.position[0]<0:this.right(0,True)
            while this.position[0]>29-this.size[0]:this.left(0,True)
            this.build(this.shape, [this.position[0],this.position[1]])
            def reset(): this.switched = False
            c.after(50, reset)
            

    def build(this, shape, offset=[0,0]):
        pos,color,border=this.datacont
        builder=[5,5]
        if offset != [0,0]: pos=0
        col=0
        for i in range(shape.size[1]):
            for j in range(shape.size[0]):
                if shape.shape[i][j]: this.block[col].append(c.create_rectangle(pos*20+builder[0]+offset[0]*20,builder[1]+offset[1]*20,pos*20+builder[0]+20+offset[0]*20,builder[1]+20+offset[1]*20,fill=color,width=2,outline=border))
                else: this.block[col].append(None)
                builder[0]+=20
            builder[0]=5
            builder[1]+=20
            col+=1
            if i!=shape.size[1]-1: this.block.append([])

    def checkGrid(this, how):
        if how == "v":
            if not this.size[1]+this.position[1]<30: return False
            I=0
            for i in range(this.position[1], this.position[1]+this.size[1]):
                J=0
                for j in range(this.position[0], this.position[0]+this.size[0]):
                    if this.block[I][J]:
                        if grid[j][i+1]: return False
                    J+=1
                I+=1
            return True
                
        if how == "vv":
            if not this.size[1]+this.position[1]<29: return False
            I=0
            for i in range(this.position[1], this.position[1]+this.size[1]):
                J=0
                for j in range(this.position[0], this.position[0]+this.size[0]):
                    if this.block[I][J]:
                        if grid[j][i+1] or grid[j][i+2]: return False
                    J+=1
                I+=1
            return True
        
        if how == "<":
            if not (this.position[0]>0 and this.moving): return False
            I=0
            for i in range(this.position[1], this.position[1]+this.size[1]):
                J=0
                for j in range(this.position[0], this.position[0]+this.size[0]):
                    if this.block[I][J]:
                        if grid[j-1][i]: return False
                    J+=1
                I+=1
            this.fixBlockPosition("<")
            return True
            
        if how == ">":
            if not (this.position[0]<20-this.size[0] and this.moving): return False
            I=0
            for i in range(this.position[1], this.position[1]+this.size[1]):
                J=0
                for j in range(this.position[0], this.position[0]+this.size[0]):
                    if this.block[I][J]:
                        if grid[j+1][i]: return False
                    J+=1
                I+=1
            this.fixBlockPosition(">")
            return True
            
        return True

    
    blockPositionData = 0
    def fixBlockPosition(this,how):
        I=0
        for i in range(this.position[1], this.position[1]+this.size[1]):
                J=0
                for j in range(this.position[0], this.position[0]+this.size[0]):
                    if this.block[I][J]:
                        if how=="<": perm = j-1
                        else: perm = j+1
                        if type(i)==type(0): blockPositionData = i
                        else: i = blockPositionData
                        if i<29 and grid[perm][i+1]:
                            this.position[1]-=1
                            for i in this.block:
                                for j in i:
                                    if j: c.move(j, 0, -20)
                    J+=1
                I+=1

    def updateGrid(this):
        X,Y=this.position
        y=0
        for i in this.block:
            x=0
            for j in i:
                if j:
                    grid[X+x][Y+y]=j
                x+=1
            y+=1
        if any([grid[i][1] for i in range(20)]):
            gameOver()
            return False
        Z = this.checkRows()
        if len(this.checkRows())>0:
            for i in Z:
                gridDown(i)
        return True

    def checkRows(this):
        totals = []
        for i in range(30):
            passts = []
            for j in range(20):
                passts.append(grid[j][i])
            if all(passts): totals.append(i)
        return totals

def gridDown(x):
    global points
    for j in range(20):
        c.delete(grid[j][x])
        for i in range(x,0,-1):
            if i-1>=0:
                c.move(grid[j][i-1], 0, 20)
                grid[j][i] = grid[j][i-1]
            else:
                grid[j][i] = False
    points+=50
    c.itemconfig(ptsText, text="Points: "+confText(points))
    c.itemconfig(totalptsText, text="Total Points: "+str(points))

extratext = []     
def gameOver():
    global points
    for i in grid:
        for j in i:
            if j: c.itemconfig(j, fill="#aaa")
    if mode == 0: colorfill = "#000"
    else: colorfill = "#fff"
    extratext.append(c.create_text(205,280,text="Game Over!", fill=colorfill, font="Bahnschrift 22 bold"))
    extratext.append(c.create_text(205,310,text="Final Score: "+str(points), fill=colorfill, font="Bahnschrift 12"))

def confText(x):
    if x<1000: return str(x)
    elif x<100000: return str(round(x/1000,2))+"k"
    elif x<1000000: return str(round(x/1000,1))+"k"
    else: return str(round(x/1000000,2))+"M"
            
 
shapes = {
    "sq":Shape("put put next put put"),
    "lineh":Shape("put put put put"),
    "t1":Shape("skip put skip next put put put"),
    "t2":Shape("put put put next skip put skip"),
    "t3":Shape("put skip next put put next put skip"),
    "t4":Shape("skip put next put put next skip put"),
    "l1":Shape("put skip skip next put put put"),
    "l2":Shape("skip skip put next put put put"),
    "l3":Shape("put put next put skip next put skip"),
    "l4":Shape("put put next skip put next skip put"),
    "l5":Shape("put skip next put skip next put put"),
    "l6":Shape("skip put next skip put next put put"),
    "l7":Shape("put put put next skip skip put"),
    "l8":Shape("put put put next put skip skip"),
    "s1":Shape("put put skip next skip put put"),
    "s2":Shape("skip put put next put put skip"),
    "s3":Shape("put skip next put put next skip put"),
    "s4":Shape("skip put next put put next put skip"),
    "linev":Shape("put next put next put next put")
    }

grid = [[False for j in range(30)] for i in range(20)]

colors = [("blue","#7777FF"),("red","#FF7777"),("#00AA00","#55CC55"),("#FF8800","#FF9977"),("black","#777777"),
          ("#DD0099","#EE77AA"),("yellow","#AAAA77")]

points = -1
speed = 402
relativeSpeed = 0.9

button_left = c.create_rectangle(422, 550, 472, 600, fill="#aaa", outline="#333")
text_left = c.create_text(447, 572, fill="#000", text="<", font="Consolas 40 bold")
button_down = c.create_rectangle(486, 550, 536, 600, fill="#aaa", outline="#333")
text_down = c.create_text(507, 576, fill="#000", text="<", font="Consolas 40 bold", angle="90")
button_right = c.create_rectangle(550, 550, 600, 600, fill="#aaa", outline="#333")
text_right = c.create_text(575, 572, fill="#000", text=">", font="Consolas 40 bold")
button_switch = c.create_rectangle(486, 486, 536, 536, fill="#aaa", outline="#333")
text_switch = c.create_text(510, 511, fill="#000", text="↺", font="Consolas 30 bold")

button_darklight = c.create_rectangle(422, 120, 600, 145, fill="#ccc", outline="#333")
text_darklight = c.create_text(511, 132, fill="#000", text="Dark/Light Mode", font="Bahnschrift 12")
button_controls = c.create_rectangle(422, 150, 600, 175, fill="#ccc", outline="#333")
text_controls = c.create_text(511, 162, fill="#000", text="Controls", font="Bahnschrift 12")
button_credits = c.create_rectangle(422, 180, 600, 205, fill="#ccc", outline="#333")
text_credits = c.create_text(511, 192, fill="#000", text="Credits", font="Bahnschrift 12")
button_restart = c.create_rectangle(422, 210, 600, 235, fill="#ccc", outline="#333")
text_restart = c.create_text(511, 222, fill="#000", text="Restart", font="Bahnschrift 12")

def restart(e):
    w.destroy()
    os.startfile("play.py")

def updateConfig():
    global mode
    with open("config.txt", 'w') as f:
            f.write("mode:"+("light" if mode==0 else "dark"))

def darklight(e, change=True):
    global mode
    if change:
        if mode == 0: mode = 1
        else: mode = 0
        updateConfig()
            
    if mode == 0:
        c.configure(bg="#fff")
        c.itemconfig(divisionLine, fill="#333")
        c.itemconfig(ptsText, fill="#333")
        c.itemconfig(totalptsText, fill="#333")
        c.itemconfig(speedText, fill="#333")
        c.itemconfig(button_left, outline="#333", fill="#aaa")
        c.itemconfig(button_down, outline="#333", fill="#aaa")
        c.itemconfig(button_right, outline="#333", fill="#aaa")
        c.itemconfig(button_switch, outline="#333", fill="#aaa")
        c.itemconfig(button_darklight, outline="#333", fill="#ccc")
        c.itemconfig(button_controls, outline="#333", fill="#ccc")
        c.itemconfig(button_credits, outline="#333", fill="#ccc")
        c.itemconfig(button_restart, outline="#333", fill="#ccc")
        c.itemconfig(text_left, fill="#000")
        c.itemconfig(text_right, fill="#000")
        c.itemconfig(text_down, fill="#000")
        c.itemconfig(text_switch, fill="#000")
        c.itemconfig(text_darklight, fill="#000")
        c.itemconfig(text_controls, fill="#000")
        c.itemconfig(text_credits, fill="#000")
        c.itemconfig(text_restart, fill="#000")
        if len(extratext)>0:
            c.itemconfig(extratext[0], fill="#000")
            c.itemconfig(extratext[1], fill="#000")
    else:
        c.configure(bg="#333")
        c.itemconfig(divisionLine, fill="#fff")
        c.itemconfig(ptsText, fill="#fff")
        c.itemconfig(totalptsText, fill="#fff")
        c.itemconfig(speedText, fill="#fff")
        c.itemconfig(button_left, outline="#fff", fill="#222")
        c.itemconfig(button_down, outline="#fff", fill="#222")
        c.itemconfig(button_right, outline="#fff", fill="#222")
        c.itemconfig(button_switch, outline="#fff", fill="#222")
        c.itemconfig(button_darklight, outline="#fff", fill="#555")
        c.itemconfig(button_controls, outline="#fff", fill="#555")
        c.itemconfig(button_credits, outline="#fff", fill="#555")
        c.itemconfig(button_restart, outline="#fff", fill="#555")
        c.itemconfig(text_left, fill="#fff")
        c.itemconfig(text_right, fill="#fff")
        c.itemconfig(text_down, fill="#fff")
        c.itemconfig(text_switch, fill="#fff")
        c.itemconfig(text_darklight, fill="#fff")
        c.itemconfig(text_controls, fill="#fff")
        c.itemconfig(text_credits, fill="#fff")
        c.itemconfig(text_restart, fill="#fff")
        if len(extratext)>0:
            c.itemconfig(extratext[0], fill="#fff")
            c.itemconfig(extratext[1], fill="#fff")

def controls(e):
    messagebox.showinfo("Controls", info.CONTROLS)

def creditss(e):
    messagebox.showinfo("Credits", info.CREDITS)

c.tag_bind(button_darklight, '<ButtonPress-1>', darklight)
c.tag_bind(text_darklight, '<ButtonPress-1>', darklight)
c.tag_bind(button_controls, '<ButtonPress-1>', controls)
c.tag_bind(text_controls, '<ButtonPress-1>', controls)
c.tag_bind(button_credits, '<ButtonPress-1>', creditss)
c.tag_bind(text_credits, '<ButtonPress-1>', creditss)
c.tag_bind(button_restart, '<ButtonPress-1>', restart)
c.tag_bind(text_restart, '<ButtonPress-1>', restart)

def updateSpeed():
    global speed, relativeSpeed
    if speed>300: speed-=2; relativeSpeed+=0.1
    elif speed>200: speed-=2; relativeSpeed+=0.2
    elif speed>150: speed-=1; relativeSpeed+=0.3
    elif speed>100: speed-=1; relativeSpeed+=0.37
    else: relativeSpeed = 50
    c.itemconfig(speedText, text="Speed: "+str(round(relativeSpeed, 1)))

def place():
    global points, currentObject
    points+=1
    updateSpeed()
    c.itemconfig(ptsText, text="Points: "+confText(points))
    c.itemconfig(totalptsText, text="Total Points: "+str(points))
    color = random.choice(colors)
    shape = random.choice(list(shapes.values()))
    x = Object(shape, color[0], color[1], random.randint(0,20-shape.size[0]))

place()
if mode == 1: darklight(0, False)
w.mainloop()
input()
