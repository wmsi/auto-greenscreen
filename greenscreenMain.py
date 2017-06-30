#!/usr/bin/python
"""
!!!!!!!!!!!!!!!!!!!!!!!!!
THIS SCRIPT IS PYTHON 2.7
!!!!!!!!!!!!!!!!!!!!!!!!!

Asher Merrill, WMSI, 20 June 2017
Version 1.Git

This script was designed to take a picture when a button is pressed on the Pi's
GPIO, and process that image to remove an approximately green background.  (This feature
is, of course, in development.)

This script was developed from DocStation2, a project worked on by many former member of the 
WMSI team.  It attempts to use their framework to capture and subsequently process the
captured image.

Because of the nature of their code, (lacking comments, generally hard to read,) the code
has been heavily modified to better document the logical progression of the code.

Hopefully it works! :D
"""

import sys
import os
import pygame
import pygame.camera
import time
import RPi.GPIO as GPIO

# Import our own stuff:
import greenscreenFn

############################
# CHANGE THE THRESHOLD HERE:
# This is the range that the HSV values can be.
# It is for the degrees of hue, in an 8-bit value.
threshold = 20

############################
# CHANGE THE PIN HERE:
controlPin = 16

"""
The main function, this controls displaying the current camera feed and when to initiliaze certain
actions, one of which uses recordImage().
"""
def main():
    # Some GPIO initilization:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(controlPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    # Some pygame initilization...
    pygame.init()
    pygame.camera.init()
    # Create fullscreen display
    screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)

    # Find, open and start cam...
    cam_list = pygame.camera.list_cameras()
    webcam = pygame.camera.Camera(cam_list[0], (800,480))
    webcam.start()

    # A font to use:
    font = pygame.font.Font(None, 25)
    # Another font to use that's a bit bigger:
    stars = pygame.font.Font(None, 50)
    
    # A numerating value for the images:
    i = 0
    
    # Execute the function to allow the user to select different points:
    refPoints = greenscreenFn.getReferencePoints(screen, webcam, font, stars, controlPin)
    # If the user decided to use the default points:
    if refPoints == None:
        # Generate a list so we can still use the rest of the program:
        refPoints = [(200, 100), (600, 100), (200, 380), (600, 380)]
    refPoint1 = refPoints[0]
    refPoint2 = refPoints[1]
    refPoint3 = refPoints[2]
    refPoint4 = refPoints[3]

    # The main loop to display images:
    while True:
        # Take the picture...
        imagen = webcam.get_image()

        # Display the image...
        screen.blit(imagen, (0,0))
        # And set background to black:
        screen.fill((0, 0, 0))

        # Tell the person how to take a picture...
        message = "Press the button to take pictures!"
        color = (0, 0, 255)
        greenscreenFn.setText(screen, font, message, color)
        
        # Print stars where the script will try to detect the corners:
        star = "*"
        color = (255, 0, 0)
        greenscreenFn.setText(screen, stars, star, color, refPoint1)
        greenscreenFn.setText(screen, stars, star, color, refPoint2)
        greenscreenFn.setText(screen, stars, star, color, refPoint3)
        greenscreenFn.setText(screen, stars, star, color, refPoint4)
        
        # Update the display so stuff actually shows...
        pygame.display.update()

        # Big pushbutton to take picture:
        if GPIO.input(controlPin) == False:
            # Capture an image, as they pressed the button...
            # (pathSave is the only returned value, telling us where the image was saved.)
            recordImageReturned = greenscreenFn.getImage(i, threshold, webcam, screen, font, refPoints)
            
            # Numerate our numerator:
            i += 1
            
            # We have to process what recordImage returned, so let's look at it:
            if recordImageReturned == None:
                # We should display a screen or something telling them that we couldn't detect the greenscreen...
                imagen = webcam.get_image()
                screen.blit(imagen, (0,0))
                message = "Couldn't detect your greenscreen!"
                color = (255, 0, 0)
                greenscreenFn.setText(screen, font, message, color)
                # Update the display so stuff actually shows...
                pygame.display.update()
                time.sleep(3)
            else:
                # Update our values because we know they're correct:
                pathFinal, pathPNG, pathUSB = recordImageReturned
                
                # Give them an option and update the screen; we'll display a grey
                # background so they know what's transparent now:
                screen.fill((169, 169, 169))
                imagen = pygame.image.load(pathPNG)
                screen.blit(imagen, (0,0))
                message = "Press button again to delete?"
                color = (255,255,255)
                greenscreenFn.setText(screen, font, message, color)
                pygame.display.update()
					
                # Start timing so we can make sure we wait long enough for a response:
                cur_time = time.time()
					
                # Now see if they want to delete it...
                isDeleted = False
                while (time.time() - cur_time < 5) and (isDeleted == False):
                    if GPIO.input(controlPin) == False:
                        # Change our control variable:
                        isDeleted = True
                        # Tell them what's going on and do it:
                        print "Deleting image from", pathFinal, 'and', pathUSB
                        screen.fill((169, 169, 169))
                        screen.blit(imagen, (0,0))
                        message = "Deleting image..."
                        color = (255,255,255)
                        greenscreenFn.setText(screen, font, message, color)
                        pygame.display.update()
                        try:
                            os.remove(pathFinal)
                            os.remove(pathUSB)
                        except:
                            print "There was an error removing the image from", pathFinal, "or", pathUSB, " Please try to remove it yourself."
                        time.sleep(1)

        # Exit documentation program and take to homescreen when escape is hit:
        events = pygame.event.get()
        keyboardInteractions = []
        for key in events:
            if key.type == 2 or key.type == 3:
                keyboardInteractions.append(key)

        for keyHit in keyboardInteractions:
            if keyHit.dict['key'] == 27:        
                # Now that we know what keys were hit, we can initiate an if statement:
                # Go ahead and thank them...
                screen.fill((0, 0, 0))
                message = "Thanks for your pictures! Don't forget to upload new photos from thumb drive!"
                color = (255,255,255)
                greenscreenFn.setText(screen, font, message, color)
                pygame.display.update()
    
                # Wait 4 seconds and then terminate everything, release resources and quit...
                time.sleep(4)
                webcam.stop()
                pygame.quit()
                sys.exit()
        
        # Sleep the program for a couple milliseconds so we're not running as fast as possible:
        time.sleep(0.005)
    
    # We've somehow exited the loop, so we can exit:
    return

# The main program:
main()
