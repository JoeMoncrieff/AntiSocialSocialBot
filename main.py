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
* Merge Mac and Windows Files / Check for any breakpoints
* investigate "Input overflow" Errors
    --> Seems to be an issue mainly with the blinkng part (I think)
    --> Maybe a Mac only problem? 
* set up a file to establish microphone breakpoints.
* Add '(Helpful)' comments

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

fc = Image.open("Photos/Layers/FigureiColour.png")
fo = Image.open("Photos/Layers/FigureiOutline.png")
bd = Image.open("Photos/Layers/BoxiDetails.png")
bs = Image.open("Photos/Layers/BoxiSign.png")

fig_arr.append(fc)
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



# Start Audio Callback =============================
def audio_callback(indata, frames, time, status):

    global elapsed
    global current_state

    #Eye Trackers
    global eyes_elapsed
    global eye_state


    """ 
    Current state is here because we have a
    conundrum where we want to go up intensity (of expressions) (Quiet --> Loud)
    immediately but down in intensity kind of slowly (Loud ---> Quiet) 
    """

    if elapsed == 0.0:
        elapsed = t.time()

    if eyes_elapsed == 0.0:
        eyes_elapsed = t.time()
    """This is called (from a separate thread) for each audio block."""
    
    #TODO: Input overflow printed from here
    if status:
        print(status, file=sys.stderr)

    # Fancy indexing with mapping creates a (necessary!) copy:
    avrg = float(np.sum(np.abs(indata)))/float(np.size(indata))
    
    # debug for threshold values
    # print(avrg)
    # print(t.time())
    
    if current_thresholds[0] < avrg < current_thresholds[1] and (t.time() - elapsed >= 0.5 or current_state <= 1):
        if len(win.my_canvas.find_withtag("filter")) != 0:
            win.my_canvas.delete("filter")

        if current_state != 1:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[1], tags="mouth")
            if current_state == 3:
                win.my_canvas.delete('eyes')
                win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        elapsed = t.time()
        current_state = 1

    elif current_thresholds[2] > avrg > current_thresholds[1] and (t.time() - elapsed >= 0.4 or current_state <= 2):
        if len(win.my_canvas.find_withtag("filter")) != 0:
            win.my_canvas.delete("filter")

        if current_state != 2:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[2], tags="mouth")
            if current_state == 3:
                win.my_canvas.delete('eyes')
                win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        elapsed = t.time()
        current_state = 2

    elif avrg >= current_thresholds[2]:
        if len(win.my_canvas.find_withtag("filter")) != 0:
            win.my_canvas.delete("filter")

        if current_state != 3:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[4], tags="mouth")
            win.my_canvas.delete('eyes')
            win.my_canvas.create_image(sx, sy, image=es, tags="eyes")

        eyes_elapsed = t.time()
        elapsed = t.time()
        current_state = 3


    # If no sound for more than half a second then we return to this face
    elif t.time() - elapsed >= 0.3:
        if current_state == 3:
            win.my_canvas.delete('eyes')
            win.my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        if current_state != 0:
            win.my_canvas.delete('mouth')
            win.my_canvas.create_image(sx, sy, image=mouth_arr[0], tags="mouth")

        
        current_state = 0
    
    #TODO: - Implement grey out so that background is unaffected
    if t.time() - elapsed >= 2:
        if len(win.my_canvas.find_withtag("filter")) == 0:
            win.generate_filter("gray",0.3)
            win.create_filter()

    # Eye Stuff here
    time_diff_eyes = t.time() - eyes_elapsed
    if (time_diff_eyes >= 5 and eye_state == 0) or eye_state > 0:
        eye_state = eye_blink(eye_state, time_diff_eyes, win.my_canvas)

    win.redraw()

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
