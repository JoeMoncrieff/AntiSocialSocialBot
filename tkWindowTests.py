from tkinter import *
curr_colour = 'red'
import time as t
import sounddevice as sd
import numpy as np

sx,sy,ex,ey = 5,5,205,205

root = Tk()

my_canvas = Canvas(root, width=210, height=210)
my_oval = my_canvas.create_oval(sx, sy, ex, ey, fill=curr_colour, outline=curr_colour)

my_canvas.pack()

elapsed = 0
def audio_callback(indata, frames, time, status):

    global elapsed
    if elapsed == 0.0:
        elapsed = time.currentTime
    """This is called (from a separate thread) for each audio block."""
    #print('callback called')
    if status:
        print(status, file=sys.stderr)

    # Fancy indexing with mapping creates a (necessary!) copy:
    avrg = float(np.sum(np.abs(indata)))/float(np.size(indata))
    print(avrg)

    if avrg > 0.002:
        my_canvas.delete('all')
        curr_colour = 'green'
        my_canvas.create_oval(sx, sy, ex, ey, fill=curr_colour, outline=curr_colour)
        print('Made new oval green')
        my_canvas.update()
        elapsed = time.currentTime
    elif time.currentTime - elapsed >= 0.5:
        my_canvas.delete('all')
        curr_colour = 'red'
        my_canvas.create_oval(sx, sy, ex, ey, fill=curr_colour, outline=curr_colour)
        print('Made new oval red')
        my_canvas.update()




stream = sd.InputStream(
        device=0,
        channels=1,
        samplerate=44100.0,
        callback=audio_callback)





def swap(colour):
    if colour == 'red':
        colour = 'blue'
    else:
        colour = 'red'

    return colour

with stream:
    root.mainloop()
