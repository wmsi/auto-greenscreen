#!/usr/bin/python
"""
Asher Merrill, WMSI

This script was designed to take a picture when a button is pressed on the Pi's
GPIO, and process that image to remove an approximately green background.  (This feature
is, of course, in development.)

This script was developed from DocStation2, a project worked on by many former member of the 
WMSI team.  It attempts to use their framework to capture and subsequently process the
captured image.

Because of the nature of their code, (lacking comments, generally hard to read,) the code
has been heavily modified to better document the logical progression of the code.

Hopefully it works!
"""

import pygame
import pygame.camera
import RPi.GPIO as GPIO
import time

import grnscrn_manipulator as control # Import our own stuff


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

def main():
    """
    Controls displaying the current camera feed and when to initiliaze certain
    actions, a number of which uses recordImage().
    """
    GPIO.setmode(GPIO.BCM) # Some GPIO initilization:
    GPIO.setup(controlPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    pygame.init() # Some pygame initilization...
    pygame.camera.init()
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    webcam = pygame.camera.Camera(pygame.camera.list_cameras()[0],
                                  (width, height))
    webcam.start()
    font = pygame.font.Font(None, 25) # A font to use...
    star_font = pygame.font.Font(None, 50) # Another font to use that's bigger...
    i = 0 # A numerating value for the images...

    # Execute the function to allow the user to select different points:
    ref_points = control.reference_points(screen, webcam, font,
                                                 star_font, controlPin)
    # If the user decided to use the default points:
    if ref_points == None:
        # Generate a list so we can still use the rest of the program:
        ref_points = [(200, 100), (width-200, 100),
                      (200, height-100), (width-100, height-100)]

    # The main loop to display images:
    while True:
        # Set background to black:
        screen.fill((0, 0, 0))

        # Take an image and display it:
        imagen = webcam.get_image()
        screen.blit(imagen, (0,0))
        # Tell the person how to take a picture...
        message = "Press the button to take pictures!"
        color = (0, 0, 255)
        control.disp_text(screen, font, message, color)
        # Print stars where the script will try to detect the corners:
        star = "*"
        color = (255, 0, 0)
        for s in ref_points:
            control.disp_text(screen, star_font, star, color, s)

        # Update the display so stuff actually shows...
        pygame.display.update()
        time.sleep(0.005)

        # Big pushbutton to take picture:
        if GPIO.input(controlPin) == False:
            # Pressed button so capture an image and numerate the numerator:
            img = control.img(i, threshold, webcam, screen, font, ref_points)
            i += 1 # Numerate numerator

            # Look at image:
            if img == None:
                # Can't detect green on screen:
                imagen = webcam.get_image()
                screen.blit(imagen, (0,0))
                message = "Couldn't detect your greenscreen!"
                color = (255, 0, 0)
                control.disp_text(screen, font, message, color)
                # Update the display so stuff actually shows...
                pygame.display.update()
                time.sleep(3)

            # The script was able to find the greenscreen:
            else:
                time_start = time.time()
                isDeleted = False
                while (time.time() - time_start < 5) and isDeleted == False:
                    screen.fill((169, 169, 169))
                    # Display the image just taken...
                    imagen = pygame.image.load(img[0])
                    screen.blit(imagen, (0, 0))
                    message = "Press button again to delete..."
                    color = (255, 255, 255)
                    control.disp_text(screen, font, message, color)

                    # Update the display:
                    pygame.display.update()
                    time.sleep(0.005)

                    # See if they hit the button:
                    if GPIO.input(controlPin) == False:
                        isDeleted = True
                        paths = []
                        for path in img[1:]:
                            if path is not None:
                                paths.append(path)
                        control.rm_img(screen, font, img[0], paths)
                        time.sleep(5)

        # Exit documentation program and take to homescreen when escape is hit:
        events = pygame.event.get()
        user_in = [k for k in events if k.type == 2 or k.type == 3]
        for k in user_in:
            if k.dict['key'] == 27:
                # Now that we know what keys were hit,
                # we can initiate an if statement:
                screen.fill((0, 0, 0))
                message = "Thanks for your pictures! Don't forget to upload n"\
                          "ew photos from thumb drive!"
                color = (255,255,255)
                control.disp_text(screen, font, message, color)
                pygame.display.update()
                time.sleep(0.005)

                # Wait 4 seconds and then terminate everything, release
                # resources and quit...
                time.sleep(4)
                webcam.stop()
                pygame.quit()
                break


if __name__ == '__main__': # Execute if not imported
    main()
