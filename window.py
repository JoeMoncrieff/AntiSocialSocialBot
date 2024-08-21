from tkinter import *
from PIL import Image, ImageTk, ImageGrab
import cv2
import numpy as np
import time

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
        self.voice_background = None
        self.voice_background_base = None
        self.voice_background_base_bin = -1

    def redraw(self):
        self.root.update_idletasks()
        self.root.update()

    def create_filter(self):
        self.my_canvas.create_image(self.canvas_dimension/2,self.canvas_dimension/2,image=self.filter,tags='filter')           
       
    def generate_filter(self,fill,alpha,file_name):
        
        new_fill = np.array(tuple(map(lambda x: int((x/(32896*2))*255),self.root.winfo_rgb(fill))) + (int(alpha * 255),)).astype(np.uint8)

        start_x, start_y = self.my_canvas.winfo_rootx() + self.my_canvas.winfo_x() ,self.my_canvas.winfo_rooty()+ self.my_canvas.winfo_y()

        pixels = ImageGrab.grab((start_x,start_y,start_x+self.canvas_dimension,start_y+self.canvas_dimension))

        #Padding tocreate an rgbA array
        pixels = np.pad(np.asarray(pixels).reshape((self.canvas_dimension,self.canvas_dimension,3)), ((0,0),(0,0),(0,1)), "constant")

        mask = (pixels[...,0] == 0) & (pixels[...,1] == 255) & (pixels[...,2] == 255) & (pixels[...,3] == 0)

        new_bitmap = np.where(mask[...,None], [255,255,255,0], new_fill).astype(np.uint8)

              
        np.save(f"Photos/Filters/{file_name}.npy", np.array(new_bitmap,dtype=np.uint8))
        array = np.load(f"Photos/Filters/{file_name}.npy")
        image1 = Image.fromarray(array, mode='RGBA')

        return ImageTk.PhotoImage(image = image1, size=(self.canvas_dimension,self.canvas_dimension))
               
    def generate_background_base(self):
        if not self.voice_background_base:
            self.voice_background_base = self.generate_filter("white",1.0,"background_base")

    def amplify_background(self,avrg):
        # scaling_function = base_border + (some_factor) * avrg 
        scaling_function = int(20 + (60*avrg))
        
        if isinstance(self.voice_background_base_bin,int):
            arr = np.load(f"Photos/Filters/background_base.npy")
            self.voice_background_base_bin = np.where(arr[..., 3] == 0, 0, 1).astype(np.uint8)
        
        kernel_open = np.ones((5,5), np.uint8)
        kernel = np.ones((scaling_function,scaling_function),np.uint8)
        
        opening = self.voice_background_base_bin
        opening[300:350,0:350] = cv2.morphologyEx(self.voice_background_base_bin[300:350,0:350], cv2.MORPH_OPEN, kernel_open)
        dilated_img = cv2.dilate(opening,kernel,iterations =1)
        
        rgba_img = np.zeros((*dilated_img.shape, 4), dtype=np.uint8)
        rgba_img[..., 0:3] = (255, 225, 255)  # RGB values stay constant
        rgba_img[..., 3] = dilated_img * 255  # Alpha channel
        #Cut out base image here so it doesn't overlap with the character
        rgba_img[..., 3] = rgba_img[...,3] - self.voice_background_base_bin * 255

        image1 = Image.fromarray(rgba_img, mode='RGBA')
        image1 = ImageTk.PhotoImage(image = image1,size = (self.canvas_dimension,self.canvas_dimension))
        
        thing_to_delete = self.my_canvas.find_withtag("background")
        
        self.my_canvas.create_image(self.canvas_dimension/2,self.canvas_dimension/2,image=image1,tags='background')
        map(self.my_canvas.delete,thing_to_delete)
        self.voice_background = image1
