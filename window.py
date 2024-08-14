from tkinter import *
from PIL import Image, ImageTk, ImageGrab
import os
import numpy


class Window:
    def __init__(self,canvas_dimension):
        
        self.canvas_dimension = canvas_dimension
        
        #Initialising the root
        self.root = Tk()
        self.root.wm_attributes("-topmost", True)
        self.root.config(bd=0, bg="cyan",padx=0,pady=0)
        self.root.geometry(f'{self.canvas_dimension}x{self.canvas_dimension}+100+100')
        
        #Setting up the canvas
        self.my_canvas = Canvas(self.root, width=canvas_dimension, height=canvas_dimension, highlightthickness=0, bg=self.root['bg'], bd=0)
        self.my_canvas.pack()

        self.filter = None

    def redraw(self):
        self.root.update_idletasks()
        self.root.update()


    def create_filter(self):
        self.my_canvas.create_image(self.canvas_dimension/2,self.canvas_dimension/2,image=self.filter,tags='filter')           
       
    def generate_filter(self,fill,alpha):
        if not self.filter:
            new_fill = tuple(map(lambda x: x % 255,self.root.winfo_rgb(fill))) + (int(alpha * 255),)

            self.redraw()

            start_x, start_y = self.my_canvas.winfo_rootx() + self.my_canvas.winfo_x() ,self.my_canvas.winfo_rooty()+ self.my_canvas.winfo_y()
            print(f"start_x: {start_x}, start_y {start_y}")
            pixels = ImageGrab.grab((start_x,start_y,start_x+self.canvas_dimension,start_y+self.canvas_dimension))
            
            new_bitmap = [[(255,255,255,0)] * self.canvas_dimension for i in range(self.canvas_dimension)]
            print(f"len(bitmap): {len(new_bitmap)} len(bitmap[0]): {len(new_bitmap[0])}")
            print(f"pixels.height: {pixels.height} pixels.width {pixels.width}")
            
        
            for x in range(self.canvas_dimension):
                for y in range(self.canvas_dimension):
                    if pixels.getpixel((x,y)) != (0,255,255):
                        new_bitmap[y][x] = new_fill
            
            numpy.save("Photos/Filters/filter.npy", numpy.array(new_bitmap,dtype=numpy.uint8))
            array = numpy.load("Photos/Filters/filter.npy")
            image1 = Image.fromarray(array, mode='RGBA')
            print(f"image1.height: {image1.height} image1.width {image1.width}")

            self.filter = ImageTk.PhotoImage(image = image1, size=(self.canvas_dimension,self.canvas_dimension))
               
        

