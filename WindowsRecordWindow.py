import sys
import time as t
from tkinter import *
import sounddevice as sd
import numpy as np
from PIL import Image, ImageTk

curr_colour = 'red'
canvas_dimension = 350

sx, sy = int(canvas_dimension/2), int(canvas_dimension/2)

root = Tk()

# Hide the root window drag bar and close button
#root.overrideredirect(True)
#root.overrideredirect(False)

# Make the root window always on top
root.wm_attributes("-topmost", True)


root.wm_attributes("-transparent", "cyan")
# Set the root window background color to a transparent color
root.config(bd=0, bg="cyan")


mouth_arr = []
mc = Image.open("Photos/Layers/MouthiClosed.png")
mos = Image.open("Photos/Layers/MouthiOpenSlight.png")
mo = Image.open("Photos/Layers/MouthiOpen.png")
mw = Image.open("Photos/Layers/MouthiOpenWider.png")
ms = Image.open("Photos/Layers/MouthiSmile.png")

# Resizing here to adjust for larger canvas
mc = ImageTk.PhotoImage(mc.resize((canvas_dimension, canvas_dimension)))
mos = ImageTk.PhotoImage(mos.resize((canvas_dimension, canvas_dimension)))
mo = ImageTk.PhotoImage(mo.resize((canvas_dimension, canvas_dimension)))
mw = ImageTk.PhotoImage(mw.resize((canvas_dimension, canvas_dimension)))
ms = ImageTk.PhotoImage(ms.resize((canvas_dimension, canvas_dimension)))


'''
mc = PhotoImage(file="Photos/Layers/MouthiClosed.png")
mos = PhotoImage(file="Photos/Layers/MouthiOpenSlight.png")
mo = PhotoImage(file="Photos/Layers/MouthiOpen.png")
mw = PhotoImage(file="Photos/Layers/MouthiOpenWider.png")
ms = PhotoImage(file="Photos/Layers/MouthiSmile.png")
'''

mouth_arr.append(mc)
mouth_arr.append(mos)
mouth_arr.append(mo)
mouth_arr.append(mw)
mouth_arr.append(ms)

eye_arr = []

ec = Image.open("Photos/Layers/EyesiClosed.png")
eh = Image.open("Photos/Layers/EyesiHalfOpen.png")
eo = Image.open("Photos/Layers/EyesiOpen.png")
es = Image.open("Photos/Layers/EyesiLaughter.png")

ec = ImageTk.PhotoImage(ec.resize((canvas_dimension, canvas_dimension), Image.ANTIALIAS))
eh = ImageTk.PhotoImage(eh.resize((canvas_dimension, canvas_dimension), Image.ANTIALIAS))
eo = ImageTk.PhotoImage(eo.resize((canvas_dimension, canvas_dimension), Image.ANTIALIAS))
es = ImageTk.PhotoImage(es.resize((canvas_dimension, canvas_dimension), Image.ANTIALIAS))

'''
ec = PhotoImage(file="Photos/Layers/EyesiClosed.png")
eh = PhotoImage(file="Photos/Layers/EyesiHalfOpen.png")
eo = PhotoImage(file="Photos/Layers/EyesiOpen.png")
es = PhotoImage(file="Photos/Layers/EyesiLaughter.png")
'''

eye_arr.append(eo)
eye_arr.append(eh)
eye_arr.append(ec)


fig_arr = []
'''
fc = PhotoImage(file="Photos/Layers/FigureiColour.png")
fo = PhotoImage(file="Photos/Layers/FigureiOutline.png")
bd = PhotoImage(file="Photos/Layers/BoxiDetails.png")
bs = PhotoImage(file="Photos/layers/BoxiSign.png")
'''

fc = Image.open("Photos/Layers/FigureiColour.png")
fo = Image.open("Photos/Layers/FigureiOutline.png")
bd = Image.open("Photos/Layers/BoxiDetails.png")
bs = Image.open("Photos/layers/BoxiSign.png")

fc = ImageTk.PhotoImage(fc.resize((canvas_dimension, canvas_dimension)))
fo = ImageTk.PhotoImage(fo.resize((canvas_dimension, canvas_dimension)))
bd = ImageTk.PhotoImage(bd.resize((canvas_dimension, canvas_dimension)))
bs = ImageTk.PhotoImage(bs.resize((canvas_dimension, canvas_dimension)))


fig_arr.append(fc)
fig_arr.append(fo)
fig_arr.append(bd)
#fig_arr.append(bs)


# Setting up main body image here
my_canvas = Canvas(root, width=canvas_dimension, height=canvas_dimension, highlightthickness=0, bg=root['bg'], bd=0)
my_canvas.pack()
for img in fig_arr:
    my_canvas.create_image(sx, sy, image=img, tags="figure")
#Adding open eyes here for now
my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")
my_canvas.create_image(sx, sy, image=mouth_arr[1], tags="mouth")

# Start Audio Callback =============================
elapsed = 0.0
current_state = -1
eyes_elapsed = 0.0
# eye states 0: open --> 1:slightly closed  --> 2:closed --> 3:slightly closed --> 0: open
eye_state = 0

def audio_callback(indata, frames, time, status):

    global elapsed
    global label # For testing, To remove.
    global current_state

    #Eye Trackers
    global eyes_elapsed
    global eye_state


    # Current state is here because we have a
    # conundrum where we want to go up intensity
    # immediately but down in intensity kind of slowly

    if elapsed == 0.0:
        elapsed = t.time()

    if eyes_elapsed == 0.0:
        eyes_elapsed = t.time()
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)

    # Fancy indexing with mapping creates a (necessary!) copy:
    avrg = float(np.sum(np.abs(indata)))/float(np.size(indata))
    print(avrg)
    # print(t.time())

    if 0.03 < avrg < 0.12 and (t.time() - elapsed >= 0.5 or current_state <= 1):
        if current_state == 3:
            my_canvas.delete('eyes')
            my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        if current_state != 1:
            my_canvas.delete('mouth')
            my_canvas.create_image(sx, sy, image=mouth_arr[1], tags="mouth")
        elapsed = t.time()
        current_state = 1

    elif 0.35 > avrg > 0.12 and (t.time() - elapsed >= 0.4 or current_state <= 2):
        if current_state == 3:
            my_canvas.delete('eyes')
            my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        if current_state != 2:
            my_canvas.delete('mouth')
            my_canvas.create_image(sx, sy, image=mouth_arr[2], tags="mouth")
        elapsed = t.time()
        current_state = 2

    elif avrg >= 0.35:
        if current_state != 3:
            my_canvas.delete('mouth')
            my_canvas.create_image(sx, sy, image=mouth_arr[4], tags="mouth")
            my_canvas.delete('eyes')
            my_canvas.create_image(sx, sy, image=es, tags="eyes")

        eyes_elapsed = t.time()
        elapsed = t.time()
        current_state = 3

    # If no sound for more than half a second then we return to this face
    elif t.time() - elapsed >= 0.3:
        if current_state == 3:
            my_canvas.delete('eyes')
            my_canvas.create_image(sx, sy, image=eye_arr[0], tags="eyes")

        if current_state != 0:
            my_canvas.delete('mouth')
            my_canvas.create_image(sx, sy, image=mouth_arr[0], tags="mouth")
        current_state = 0

    # Eye Stuff here
    time_diff_eyes = t.time() - eyes_elapsed
    if (time_diff_eyes >= 5 and eye_state == 0) or eye_state > 0:
        eye_state = eye_blink(eye_state, time_diff_eyes, my_canvas)

    my_canvas.update()

# End Audio Callback =============================


def eye_blink(eye_state_, time_diff, canvas):
    global eyes_elapsed

    if eye_state_ > 0:
        if time_diff > 0.12:
            new_eye_state = (eye_state_ + 1) % len(eye_arr)
            print(time_diff)
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



stream = sd.InputStream(
        device=1,
        channels=1,
        samplerate=44100.0,
        callback=audio_callback)

with stream:
    root.mainloop()
