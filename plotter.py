#! /usr/bin/env python

import time
import serial


class Plotter:
    """
    Class that allows control of the plotter"""

    def __init__(self, port, baudrate, commands_dict, away):
        self.commands = commands_dict
        self.away = away
        self._serial = serial.Serial(port, baudrate)
        self._serial.write(b'\r\n\r\n')
        time.sleep(2)  # Wait for grbl to initialize
        self._serial.flushInput()

    def _stream(self, gcode):
        """
        Send gcode to the machine"""
        try:
            for line in gcode.split(b'\n'):
                stripped = line.strip()
                self._serial.write(stripped + b'\n')
                grbl_out = self._serial.readline()
                # print(f'Recieved: {grbl_out}')

            return True

        except KeyboardInterrupt:
            return False

    def set_position(self, coords=(0, 0)):
        """
        Set the current (X, Y) position (Z is set to 0)"""

        x, y = coords
        gcode = self.commands['SET_POSITION'].format(x=x, y=y)
        return self._stream(gcode.encode('utf-8'))

    def move_to(self, coords=(0, 0), fast=False):
        """
        Move plotter head to coords"""
        x, y = coords
        if fast:
            gcode = self.commands['FAST_MOVE_TO'].format(x=x, y=y)
        else:
            gcode = self.commands['MOVE_TO'].format(x=x, y=y)
        return self._stream(gcode.encode('utf-8'))

    def pen_up(self):
        """
        Lift the pen"""
        gcode = self.commands['PEN_UP']
        return self._stream(gcode.encode('utf-8'))

    def pen_down(self):
        """
        Lower the pen"""
        gcode = self.commands['PEN_DOWN']
        return self._stream(gcode.encode('utf-8'))

    def trace(self, path):
        """
        Move through a series of points."""

        start = path[0]
        if not self.pen_up():
            return False

        if not self.move_to(start, fast=True):
            return False

        if not self.pen_down():
            return False

        for coords in path[1:]:
            if not self.move_to(coords):
                return False

        return True

    def move_away(self):
        """
        Move out of the ROI"""
        self.pen_up()
        self.move_to(self.away, fast=True)
        self.pen_down()

    def __exit__(self):
        self._serial.close()
