from tkinter import *
from PIL import Image, ImageTk, ImageGrab


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
        new_fill = tuple(map(lambda x: x % 255,self.root.winfo_rgb(fill))) + (int(alpha * 255),)
        img = Image.new('RGBA', (1,1),new_fill)
        self.filter = ImageTk.PhotoImage(img)

        start_x, start_y = self.my_canvas.winfo_rootx(), self.my_canvas.winfo_rooty()
        pixels = ImageGrab.grab((start_x,start_y,start_x+self.canvas_dimension,start_y+self.canvas_dimension))
        
            
        for x in range(self.canvas_dimension):
            for y in range(self.canvas_dimension):
                print(f"rgb data: {pixels.getpixel((x,y))}")        
                             
        #TODO make it so that the background doesn't get faded
        #self.my_canvas.create_image(self.canvas_dimension/2,self.canvas_dimension/2,image=self.filter,tags='filter')
