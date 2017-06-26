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
from greenscreenFn import *

############################
# CHANGE THE THRESHOLD HERE:
# This is the range that the HSV values can be.
# It is for the degrees of hue, in an 8-bit value.
threshold = 20

"""
The main function, this controls displaying the current camera feed and when to initiliaze certain
actions, one of which uses recordImage().
"""
def main():
    # Some GPIO initilization:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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
    
    # A numerating value for the images:
    i = 0
    
    while True:
        # Take the picture...
        imagen = webcam.get_image()

        # Display the image...
        screen.blit(imagen, (0,0))

        # Tell the person how to take a picture...
        display_msg = "Press the button to take pictures!"
        text2 = font.render(display_msg, True, (0,0,255))
        screen.blit(text2, (220, 220))
        # Update the display so stuff actually shows...
        pygame.display.update()

        # Big pushbutton to take picture:
        input_state = GPIO.input(16)
        if input_state == False:
            # Capture an image, as they pressed the button...
            # (pathSave is the only returned value, telling us where the image was saved.)
            recordImageReturned = recordImage(i, threshold, webcam, screen, font)
            
            # Numerate our numerator:
            i += 1
            
            # We have to process what recordImage returned, so let's look at it:
            if recordImageReturned == None:
                # We should display a screen or something telling them that we couldn't detect the greenscreen...
                imagen = webcam.get_image()
                screen.blit(imagen, (0,0))
                display_msg = "Couldn't detect your greenscreen!"
                text2 = font.render(display_msg, True, (255, 0, 0))
                screen.blit(text2, (220, 220))
                # Update the display so stuff actually shows...
                pygame.display.update()
                time.sleep(3)
            else:
                # Update our values because we know they're correct:
                pathFinal, pathPNG = recordImageReturned
                
                # Give them an option and update the screen:
                screen.fill((169, 169, 169))
                imagen = pygame.image.load(pathPNG)
                screen.blit(imagen, (0,0))
                delete_option = "Press button again to delete?"
                text4 = font.render(delete_option, True, (255,255,255))
                screen.blit(text4, (220, 220))
                pygame.display.update()
					
                # Start timing so we can make sure we wait long enough for a response:
                cur_time = time.time()
					
                # Now see if they want to delete it...
                isDeleted = False
                while (time.time() - cur_time < 5) and (isDeleted == False):
                    input_state2 = GPIO.input(16)
                    if input_state2 == False:
                        isDeleted = True
                        print "Deleting image from", pathFinal
                        screen.fill((169, 169, 169))
                        screen.blit(imagen, (0,0))
                        message = "Deleting image..."
                        message = font.render(message, True, (255,255,255))
                        screen.blit(message, (220, 220))
                        pygame.display.update()
                        try:
                            os.remove(pathFinal)
                        except:
                            print "There was an error removing the image from", pathFinal, ". Please try to remove it yourself."
                        time.sleep(1)

        # Exit documentation program and take to homescreen when BCM pin 13 is low:
        input_state3 = GPIO.input(13)
        if input_state3 == False:
        
            # Go ahead and thank them...
            screen.fill((0,0,0))
            thank_you = "Thanks for your pictures! Don't forget to upload new photos from thumb drive!"
            text3 = font.render(thank_you, True, (255,255,255))
            text3rect = text3.get_rect()
            text3rect.centerx = screen.get_rect().centerx
            text3rect.centery = screen.get_rect().centery
            screen.blit(text3, text3rect)
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
