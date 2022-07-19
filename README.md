# wordblitz-plotter
A plotter that plays Wordblitz using computer vision 

https://user-images.githubusercontent.com/100698182/179841319-f4e044b0-a468-4c2b-8bd4-b32b3cb4e9cf.mp4

## How it works
1. The machine takes a picture of the work area using a Raspberry Pi camera module.
1. ArUco markers on the sides are detected using OpenCV and used to estimate the position of the phone.
1. Using Tesseract, the letters are recognized and fed to [a solver I wrote a while ago](https://github.com/GhettoBastler/boggle-bot/)
1. The solutions are converted to Gcode and sent to the plotter which uses a state of the art "pen-wrapped-in-aluminium-foil-stylus" to trace the paths on the phone.

![machine](https://user-images.githubusercontent.com/100698182/179844339-7bee0739-aaad-44cb-baba-c147ed0a02bf.jpg)
![camera](https://user-images.githubusercontent.com/100698182/179844344-736af411-5751-4686-9a67-403fdccd30f6.jpg)
![stylus](https://user-images.githubusercontent.com/100698182/179844348-30c40a00-457b-477e-93ef-7138dd19f02f.jpg)

**TODO:** Write a proper readme file.
