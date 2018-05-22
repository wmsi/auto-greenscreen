#!/usr/bin/python
"""
Asher Merrill, WMSI

See grnscrn.py for more details.
"""

# Some colors to use:
blue = (0, 0, 255)
red = (255, 0, 0)
grey = (169, 169, 169)
black = (0, 0, 0)
white = (255, 255, 255)

############################
# CHANGE THE THRESHOLD HERE:
# This is the range that the HSV values can be.
# It is for the degrees of hue, in an 8-bit value.
threshold = 20

############################
# CHANGE THE PIN HERE:
controlPin = 16

############################
# CHANGE THE IMG SIZE HERE:
width = 800
height = 480

# Default reference points:
def_ref_points = [(200, 100),
                  (width-200, 100),
                  (200, height-100),
                  (width-200, height-100)]
