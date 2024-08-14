from tkinter import *
from PIL import Image, ImageTk


class Window:
    def __init__(self,canvas_dimension):
        
        self.canvas_dimension = canvas_dimension
        
        #Initialising the root
        self.root = Tk()
        self.root.wm_attributes("-topmost", True)
        self.root.config(bd=0, bg="cyan")
        
        #Setting up the canvas
        self.my_canvas = Canvas(self.root, width=canvas_dimension, height=canvas_dimension, highlightthickness=0, bg=self.root['bg'], bd=0)
        self.my_canvas.pack()

        self.filter = None
    def redraw(self):
        self.root.update_idletasks()
        self.root.update()


    def create_filter(self,fill,alpha):
        new_fill = tuple(map(lambda x: x%255,self.root.winfo_rgb(fill))) + (int(alpha * 255),)
        img = Image.new('RGBA', (350,350),new_fill)
        self.filter = ImageTk.PhotoImage(img)

        #TODO: make it so that the background doesn't get faded
        self.my_canvas.create_image(self.canvas_dimension/2,self.canvas_dimension/2,image=self.filter,tags='filter')
        #self.my_canvas.create_rectangle(0,0,350,350,fill=fill)
