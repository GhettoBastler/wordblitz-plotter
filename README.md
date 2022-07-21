# wordblitz-plotter
A robot that automatically plays Wordblitz on a phone.

https://user-images.githubusercontent.com/100698182/179841319-f4e044b0-a468-4c2b-8bd4-b32b3cb4e9cf.mp4

## Introduction

<p align="center">
  <img src="https://user-images.githubusercontent.com/100698182/180197872-625778df-a367-4542-869f-f60c43ff89ab.jpg" width="500" />
</p>

[Wordblitz](https://wordblitz.com/) is basically a mobile version of Boggle : two players score points by finding words in a 4x4 grid of letters. Since I am bad at it, I wrote [a program to cheat](https://github.com/GhettoBastler/boggle-bot). But I was still losing, because entering the solutions manually was too slow. So I built a machine to do that for me.


![machine_camera](https://user-images.githubusercontent.com/100698182/180181265-8275f6e8-7f89-4d6e-80dd-a42e131ca751.jpg)

*Yes, I could have made a program that plays the game on a computer, but where is the fun in that ?*


## How it works

The system is comprised of two main parts :
- A plotter that moves a stylus around
- A Raspberry Pi 3 with a camera module that takes pictures of the phone, processes them and sends commands to the plotter

### The plotter

![plotter](https://user-images.githubusercontent.com/100698182/180181744-654e8e25-2980-4b95-8388-92b6dff64361.jpg)
The base structure is made of laser-cut MDF. The steel rods where scrapped from some old printers, and the bearings came from an abandonned project at my local makerspace. I had to buy the belt, pulleys and motors. The controller is an Arduino Uno running [a modified version of grbl](https://github.com/cprezzi/grbl-servo).

![markers](https://user-images.githubusercontent.com/100698182/180183231-4e759b73-79d2-40d7-849f-bee37c68079e.jpg)
To estimate the position of the work area, 19 [ArUco markers](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html) are taped its sides. Having several markers allows OpenCV to accurately locate the table even when some of them aren't visible.

<p align="center">
  <img src="https://user-images.githubusercontent.com/100698182/179844348-30c40a00-457b-477e-93ef-7138dd19f02f.jpg" width="800" />
</p>
The stylus is actually a Q-tip stuck at the end of a pen, wrapped in aluminium foil. It is connected to piece of sheet metal placed underneath some black poster board. This provides enough change in capacitance to simulate touch on the phone's screen.


### The software

![steps](https://user-images.githubusercontent.com/100698182/180219002-2f9c574f-99cd-40b9-a1c7-17bc504ed8e7.jpg)


In a nutshell, `wordblitz.py` does the following:

1. Take a picture and estimate the camera position using the markers on the sides of the work area.
1. Warp and crop the image using the computed position to recreate a view of the table from above.
1. Extract the letters from the grid using OpenCV and Tesseract-OCR.
1. Find the solutions and compute the corresponding paths.
1. Stream G-code to the plotter to trace these paths on the phone.

It uses instances of the following classes:

- **ROIExtractor**: takes the picture, detects the markers and warps the image to extract the region of interest at the center of the work area.
- **Translator**: converts pixel coordinates on an image to a position in millimeters for the plotter.
- **Plotter**: provides functions to move the plotter around.

These are stored in `vision.py`, `translate.py` and `plotter.py` respectively. `machine.py` create instances of these classes based on the content of `parameters.yaml`.


## Installation

*To be honest, I don't really expect anyone to replicate this. Still, the details provided here might be of use to anywone wanting to reuse parts of it.*


Since this is a headless setup, I used the Raspberry Pi OS Lite. I had to use the 32-bit version over the 64-bit so I could use the legacy camera stack.

Here are the steps to install the program on the Pi :

1. Upgrade the packages:
```
sudo apt-get update && sudo apt-get upgrade
```

2. Install git and tesseract-ocr:

```
sudo apt-get install git tesseract-ocr
```

3. Install Python dependencies:

```
sudo apt-get install python3-opencv python3-numpy python3-picamera python3-pil python3-yaml python3-serial python3-tesserocr
```

4. Enable legacy camera support:

```
sudo raspi-config
```

Then select **Interface Options**, **Legacy Camera** and **Yes**.
select **Finish** and reboot the system.

5. Once the Pi has rebooted, clone this repository

```
git clone https://github.com/GhettoBastler/wordblitz-plotter
```

6. Enter the directory and extract the word tree

```
cd wordblitz-plotter
unzip tree.zip
rm tree.zip
```

*Note: `tree.json` was generated from a set of French words. To use this program in your own language, you will have to [generate your own dictionary](https://github.com/GhettoBastler/boggle-bot/#usage)*


## Configuration

All of the machine parameters are stored in `parameters.yaml`. This file is comprised of four sections :


### Translator

The only parameter *px_per_mm* is the resolution of the "flat" image used for recognizing the grid and the letters.

### Camera

This section contains three parameters:
- *resolution*: the size of the image captured by the camera (width and height) in pixels
- *matrix*: the intrinsic parameters of the camera as a 3x3 matrix
- *dist_coeffs*: the distortion coeffecients of the camera
The camera matrix and distortion coefficients are specific to a particular camera. See [this tutorial](https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html) for more details.

### Board

This sections stores informations about the ArUco markers.

<p align="center">
  <img src="https://user-images.githubusercontent.com/100698182/180105758-77da276e-2898-4647-be63-e1c17e4bdbf3.jpg" width="800" />
</p>

- *dict_name*: the name of the marker dictionary in OpenCV. See [here](https://docs.opencv.org/4.x/d9/d6a/group__aruco.html#gac84398a9ed9dd01306592dd616c2c975) for all available options
- *object_points*: The X-Y-Z coordinates (in millimeters) of the four corners of each markers of the board
- *size*: The width an height of the board in millimeters
- *roi_bounds*: The bounds of the center of the work area (as minX, minY, maxX and maxY)

### Plotter

These are used to communicate with the plotter:
- *port*: the port serial port to use
- *baudrate*: the baudrate used to communicate with the plotter
- *commands*: a list of G-code instructions that are sent to the machine
- *away*: where to move the plotter so it doesn't obstruct the board when taking a picture (X and Y coordinates)

## Usage

**The program assumes that the plotter is out of the way at start up**. You have to put it in this position manually beforehand. Not doing so may move the plotter out of bounds.

Connect to the Raspberry Pi using SSH and run `python wordblitz.py`. The program will display a message when it is ready.

Start a game of Wordblitz on the phone and put it on the work surface.
<p align="center">
  <img src="https://user-images.githubusercontent.com/100698182/180195921-25bb5668-e2ab-411e-92f2-041167970660.jpg" width="500" />
</p>
Because of the way OpenCV detects rectangles, the phone have to be slightly tilted so that the bottom right corner sits lower than the three others.

At the end of the countdown, press Enter to run the machine.

## Conclusion

![mosaic](https://user-images.githubusercontent.com/100698182/180190135-51e2f6fd-0f10-49b8-a929-fba944beecb6.jpg)

This was my first attempt at making *something that moves based on what it "sees"*, and I am very happy with how it turned out. The whole project might be silly, but I learned a lot about design, fabrication, computer vision and electronics in the process.

There are some issues and limitations that I didn't address:

- The double/triple points cells are not recognized
- Tesseract have trouble recognizing some letters (uppercase "i" mostly)
- If the phone is not tilted the right way, the extracted image of the grid gets rotated 90 degrees and the OCR fails
- The program vaguely tries to minimize pen-up movement, but doesn't search for the optimal path

Eventually, I would like to use this as a platform to experiment with other computer vision projects. But I've been working on this for two months now, and there are other things I would like to try and make. So this might take a while!

## Licensing

This project is licensed under the terms of the GNU GPLv3 license.
