import sys
import time as t
from tkinter import *
import sounddevice as sd
import numpy as np
from PIL import Image, ImageTk
from window import Window


# TODO: Maybe consider a file to pull from although this might be simpler.
windows_thresholds = [0.03,0.12,0.35]
mac_thresholds = [0.002,0.02,0.04 ]

# Change this depending on device
current_thresholds = windows_thresholds.copy()


""" 
TODO:
* investigate "Input overflow" Errors

* Add art customisation (Maybe Hats? maybe on obs? check feasibility)

"""

canvas_dimension = 350

sx, sy = int(canvas_dimension/2), int(canvas_dimension/2)

win = Window(canvas_dimension)

# Helper function to resize images
def img_resize(img, canv_dim=canvas_dimension):
    return ImageTk.PhotoImage(img.resize((canv_dim, canv_dim)))


mouth_arr = []
mc = Image.open("Photos/Layers/MouthiClosed.png")
mos = Image.open("Photos/Layers/MouthiOpenSlight.png")
mo = Image.open("Photos/Layers/MouthiOpen.png")
mw = Image.open("Photos/Layers/MouthiOpenWider.png")
ms = Image.open("Photos/Layers/MouthiSmile.png")

# Resizing here to adjust for larger canvas

mouth_arr.append(mc)
mouth_arr.append(mos)
mouth_arr.append(mo)
mouth_arr.append(mw)
mouth_arr.append(ms)

mouth_arr = list(map(img_resize,mouth_arr))

eye_arr = []

ec = Image.open("Photos/Layers/EyesiClosed.png")
eh = Image.open("Photos/Layers/EyesiHalfOpen.png")
eo = Image.open("Photos/Layers/EyesiOpen.png")
es = Image.open("Photos/Layers/EyesiLaughter.png")

es = img_resize(es)

eye_arr.append(eo)
eye_arr.append(eh)
eye_arr.append(ec)

eye_arr = list(map(img_resize,eye_arr))

fig_arr = []

fc1 = np.load(f"Photos/Filters/padding.npy")
fc1 = Image.fromarray(fc1, mode='RGBA')
fc1 = ImageTk.PhotoImage(image = fc1,size = (canvas_dimension,canvas_dimension))

fc = Image.open("Photos/Layers/FigureiColour.png")
fo = Image.open("Photos/Layers/FigureiOutline.png")
bd = Image.open("Photos/Layers/BoxiDetails.png")
bs = Image.open("Photos/Layers/BoxiSign.png")
fc2 = Image.open("Photos/Layers/FigureiColour2.png")

#TODO make this an input switch

regular = False
if regular: 
    fig_arr.append(fc)
else: 
    fig_arr.append(fc2)
fig_arr.append(fo)
fig_arr.append(bd)


#TODO: Move Box sign to (Future) Accessories section. 
#fig_arr.append(bs)


fig_arr = list(map(img_resize,fig_arr))

#Initial build of character model
for img in fig_arr:
    win.my_canvas.create_image(sx, sy, image=img, tags="figure")


#Adding open eyes here
win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")
win.my_canvas.create_image(sx, sy, image=mouth_arr[1], tags="mouth")

elapsed = 0.0
current_state = -1
eyes_elapsed = 0.0
# eye states 0: open --> 1:slightly closed  --> 2:closed --> 3:slightly closed --> 0: open
eye_state = 0
background_voice_elapsed = 0


# Start Audio Callback =============================
def audio_callback(indata, frames, time, status):

    global elapsed
    global current_state

    #Eye Trackers
    global eyes_elapsed
    global eye_state
    
    #Background tracker
    global background_voice_elapsed


    """ 
    Current state is here because we have a
    conundrum where we want to go up intensity (of expressions) (Quiet --> Loud)
    immediately but down in intensity kind of slowly (Loud ---> Quiet) 
    """
    curr_time = t.time()
    if elapsed == 0.0:
        elapsed = curr_time

    if eyes_elapsed == 0.0:
        eyes_elapsed = curr_time

    if background_voice_elapsed == 0:
        background_voice_elapsed = curr_time
    """This is called (from a separate thread) for each audio block."""
    
    #TODO: Input overflow printed from here
    if status:
        print(status, file=sys.stderr)

    # Fancy indexing with mapping creates a (necessary!) copy:
    avrg = float(np.sum(np.abs(indata)))/float(np.size(indata))
    

    # TODO: amplify voice here :)
    if not regular and win.voice_background_base:
        win.amplify_background(avrg)
        background_voice_elapsed = curr_time

    
    
    if current_thresholds[0] < avrg < current_thresholds[1] and (curr_time - elapsed >= 0.5 or current_state <= 1):
        if len(win.my_canvas.find_withtag("filter")) != 0 and regular:
            win.my_canvas.delete("filter")

        if current_state != 1:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[1], tags="mouth")
            if current_state == 3:
                win.my_canvas.delete('eyes')
                win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        elapsed = curr_time
        current_state = 1

    elif current_thresholds[2] > avrg > current_thresholds[1] and (curr_time - elapsed >= 0.4 or current_state <= 2):
        if len(win.my_canvas.find_withtag("filter")) != 0 and regular:
            win.my_canvas.delete("filter")

        if current_state != 2:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[2], tags="mouth")
            if current_state == 3:
                win.my_canvas.delete('eyes')
                win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        elapsed = curr_time
        current_state = 2

    elif avrg >= current_thresholds[2]:
        if len(win.my_canvas.find_withtag("filter")) != 0 and regular:
            win.my_canvas.delete("filter")

        if current_state != 3:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[4], tags="mouth")
            win.my_canvas.delete('eyes')
            win.my_canvas.create_image(sx, sy, image=es, tags="eyes")

        eyes_elapsed = curr_time
        elapsed = curr_time
        current_state = 3


    # If no sound for more than half a second then we return to this face
    elif curr_time - elapsed >= 0.3:
        if current_state != 0:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[0], tags="mouth")
            if current_state == 3:
                win.my_canvas.delete('eyes')
                win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")
        
        current_state = 0
    
    #Grey out character for inactivity here.
    if curr_time - elapsed >= 2:
        if len(win.my_canvas.find_withtag("filter")) == 0 and regular:
            if not win.filter:
                win.filter = win.generate_filter("gray",0.3,"filter")
            win.create_filter()
        
        #Init here after everything loaded
        if len(win.my_canvas.find_withtag("background")) == 0 and not regular:
            win.generate_background_base()

    # Eye Stuff here
    time_diff_eyes = curr_time - eyes_elapsed
    if (time_diff_eyes >= 5 and eye_state == 0) or eye_state > 0:
        eye_state = eye_blink(eye_state, time_diff_eyes, win.my_canvas)

     

# End Audio Callback =============================


#helper function for the blink.
def eye_blink(eye_state_, time_diff, canvas):
    global eyes_elapsed

    if eye_state_ > 0:
        if time_diff > 0.12:
            new_eye_state = (eye_state_ + 1) % len(eye_arr)
            # print(time_diff)
            canvas.delete('eyes')
            canvas.create_image(sx, sy, image=eye_arr[new_eye_state], tags="eyes")
            eyes_elapsed = t.time()
            return new_eye_state
        else:
            return eye_state_
    else:
        canvas.delete('eyes')
        canvas.create_image(sx, sy, image=eye_arr[1], tags="eyes")
        eyes_elapsed = t.time()
        return 1


#General device notes:

"""
You can run `python3 -m sounddevice to find what channel the input device you actually
want to use is on.
"""

# Windows Settings
stream = sd.InputStream(
        device=1,
        channels=1,
        samplerate=44100.0,
        callback=audio_callback)


""" Mac Settings
stream = sd.InputStream(
        device=0,
        channels=1,
        samplerate=44100.0,
        callback=audio_callback)
"""

with stream:
    win.root.mainloop()
