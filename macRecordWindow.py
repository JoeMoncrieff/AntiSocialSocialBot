from tkinter import *
curr_colour = 'red'
import sounddevice as sd
import numpy as np
from PIL import Image, ImageTk

sx,sy,ex,ey = 176,176,200,200

root = Tk()

# Hide the root window drag bar and close button
#root.overrideredirect(True)
#root.overrideredirect(False)

# Make the root window always on top
root.wm_attributes("-topmost", True)
# Turn off the window shadow
root.wm_attributes("-transparent", True)

# Set the root window background color to a transparent color
root.config(bd=0,bg="systemTransparent")


my_canvas = Canvas(root, width=350, height=350, bg=root['bg'], bd=0)
my_canvas.pack()
#my_oval = my_canvas.create_oval(sx, sy, ex, ey, fill=curr_colour, outline=curr_colour)

photo_arr = []
fs = PhotoImage(file="Photos/facesilentrs.PNG")
fo = PhotoImage(file="Photos/faceopenrs.PNG")
fh = PhotoImage(file="Photos/facehappyrs.PNG")
fl = PhotoImage(file="Photos/faceloudrs.PNG")

photo_arr.append(fs) #Silent
photo_arr.append(fo) #Open
photo_arr.append(fh) #Happy
photo_arr.append(fl) #Loud




#Start Audio Callback =============================
elapsed = 0
current_state = -1
def audio_callback(indata, frames, time, status):

    global elapsed
    global label #For testing, To remove.


    global current_state
    #Current state is here because we have a
    # conundrum where we want to go up intensity
    # immediately but down in intensity kind of slowly

    if elapsed == 0.0:
        elapsed = time.currentTime
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)

    # Fancy indexing with mapping creates a (necessary!) copy:
    avrg = float(np.sum(np.abs(indata)))/float(np.size(indata))

    if 0.002 < avrg <0.02 and (time.currentTime - elapsed >= 0.5 or current_state<=1):

        my_canvas.delete('all')
        my_canvas.create_image(sx, sy, image=photo_arr[1])
        my_canvas.update()
        elapsed = time.currentTime
        current_state = 1

    elif 0.02 <= avrg <=0.04 and (time.currentTime - elapsed >= 0.3 or current_state<=1) :
        my_canvas.delete('all')
        my_canvas.create_image(sx, sy, image=photo_arr[1])
        my_canvas.update()
        elapsed = time.currentTime
        current_state = 1

    elif avrg >0.04 and (time.currentTime - elapsed >= 0.3 or current_state<=3):
        my_canvas.delete('all')
        my_canvas.create_image(sx, sy, image=photo_arr[3])
        my_canvas.update()
        elapsed = time.currentTime
        current_state = 3

    #If no sound for more than half a second then we return to this face
    elif time.currentTime - elapsed >= 0.3:
        pass
        my_canvas.delete('all')
        my_canvas.create_image(sx, sy, image=photo_arr[0])
        my_canvas.update()

#End Audio Callback =============================

stream = sd.InputStream(
        device=0,
        channels=1,
        samplerate=44100.0,
        callback=audio_callback)

with stream:
    root.mainloop()