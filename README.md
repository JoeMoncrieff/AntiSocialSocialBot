# Anti-Social-Social-Bot

## Summary

It's a but hard to communicate the functionality through words so I'm hoping the gif below clarifies this explanation. Essentially this is code that produces an image which dynamically changes depending on the volume of the input device (microphone). The idea is that it acts as a visualizer to someone talking and the aim is to overlay it over streams or videos without the need for editing. The cyan background produced by the Tkinter window is easily chroma-keyed out in OBS for example.  

!["AntiSocialGif"](/Photos/ReadmeRes/AntisocialGif.gif)

The idea behind the anti-social-social-bot was that I was watching a twitch stream and got a little bit jealous of "PNGtuber" that the streamer had when his camera died. In my 2:00am mood I took one look at this and went "I can do that". The aim was to achieve the following:

* **"Live code:"** i.e code that reacts in the moment to a continuous dynamic input, in this case, sound. And also it helps you write efficient code or mke sacrifices since it has to be fast.

* **Displayable:** I wanted something I could show to my friends that was engaging if you didn't know how to code (isn't output to a terminal).

* **Usability:** I wanted something I could use in daily life.

## Lessons Learned

There's alot I've learned in the course of this project. I learned the basics of a couple useful Python libraries; the main ones in this project were:

1. **Tkinter & Pillow:** The graphical interface which displays the character and additional image types that Pillow provides.

2. **Sounddevice:** The library that handles the microphone input.

3. **Numpy:** Numpy helps with alot of fast data manipulation which turned out to be critical for this project.

4. **OpenCV:** OpenCV plays a small but critical role for a part of the functionality

### Tkinter and Garbage Collection --> Image Flicker

If you make an image and don't save it to a variable garbage collection will take your lovely image and throw it in the trash. this means the second you overwrite an image and try to draw it it will automatically remove the image that was already on the canvas. this leads to the image "flickering" which is visually unappealing.

### Numpy and OpenCV --> Vectorisation

In general it's better if code executes fast. In this project that's also really true. Vectorization using numpy and OpenCv helps meet those speed requirements I'm looking for.