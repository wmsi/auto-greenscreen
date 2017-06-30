#!/usr/bin/python
"""
!!!!!!!!!!!!!!!!!!!!!!!!!
THIS SCRIPT IS PYTHON 2.7
!!!!!!!!!!!!!!!!!!!!!!!!!

Asher Merrill, WMSI, 20 June 2017
Version 1.Git

See greenscreenMain.py for more details.
"""

import os
import pygame
import pygame.camera
import datetime
from PIL import Image
from PIL import ImageFilter
from shutil import copy
import RPi.GPIO as GPIO
import time

"""
The main image capture and processing function.

This function takes an image, saves it in tmp, re-imports it into PIL so it can be processed;
removes colors that fall within the specified range and replaces them with transperancy,
and then saves it as a .PNG again to a certain path.

This function returns only the location where it saved the final image AND where it saved the .PNG (/tmp/image.png).
"""
def getImage(i, threshold, webcam, surface, font, refPoints):
    # Date-time strings for naming:
    hi = str(datetime.datetime.now().date())
    hi = hi.replace(".", "_")
    hi = hi.replace(" ", "_")
    hi = hi.replace(":", "_")
    
    ti = str(datetime.datetime.now().time())
    ti = ti.replace(".", "_")
    ti = ti.replace(" ", "_")
    ti = ti.replace(":", "")
    ti = ti[0:4]

    # Capture and then save our image, so we can open it with PIL:
    imagen = webcam.get_image()
    
    # These are the paths to save the images in:
    pathPNG = "/tmp/image.png"
    pathJPG = "/tmp/image.jpg"
    
    # Now tell the user we're saving the image:
    print "Saving tmp. image in", pathJPG
    pygame.image.save(imagen, pathJPG)

    # Display the images we just took...
    surface.blit(imagen, (0,0))
    message = "Saving and processing image, please wait..."
    message = font.render(message, True, (72, 118, 255))
    messagerect = message.get_rect()
    messagerect.centerx = surface.get_rect().centerx
    messagerect.centery = surface.get_rect().centery
    surface.blit(message, messagerect)
    pygame.display.update()
    
    # Now we can open the image with PIL, and convert it to RGBA AND HSV:
    ###
    # For testing purposes, you can uncomment the below to manually point to an image.
    # pathJPG = raw_input("Please enter the path and image name of the desired image to be procesed:")
    imgRGBA = Image.open(pathJPG)
    imgRGBA = imgRGBA.convert("RGBA")
    imgHSV = imgRGBA.convert("HSV")
    
    # Let's use our getColorMean() function to identify the approximate color of the green screen:
    hsvData = getColorMean(imgHSV, refPoints)
    
    # Check the type to make sure the function worked:
    if hsvData == None:
        print "The program could not detect your green screen or your image is too small!"
    else:
        H, S, V = hsvData
        ###
        # The rest of this code was taken from a delightfully helpful blogger at
        # http://salgat.blogspot.com/2015/04/using-pythons-pil-library-to-remove.html
        # It will remove (set alpha to 0) pixels that fall within certian color parameters...
        pixdata = imgRGBA.load()
        for y in xrange(imgRGBA.size[1]):
            for x in xrange(imgRGBA.size[0]):  
                r, g, b, a = imgRGBA.getpixel((x, y))
                h, s, v = imgHSV.getpixel((x, y))        
                if (H - threshold <= h <= H + threshold):
                    #and (S - threshold <= s <= s + threshold) and (V - threshold <= v <= V + threshold):
                    pixdata[x, y] = (255, 255, 255, 0)  
                #Remove anti-aliasing outline of body.  
                if r == 0 and g == 0 and b == 0:  
                    pixdata[x, y] = (255, 255, 255, 0)  
        imgOut = imgRGBA.filter(ImageFilter.GaussianBlur(radius=1))
        print "Saving tmp. image in", pathPNG
        imgOut.save(pathPNG, "PNG")

        # It seems that we're struggling to save the file elegantly, so let's just copy it from /tmp:
        # (pathSave is the location that we're going to save the file:)
        imageName = "%(1)s_%(2)s_%(3)s.png" % {"1": hi,"2": ti,"3" : i}
        # Start defining some of the other names:
        pathLocal = "/home/pi/Pictures/" + imageName
        print "Copying image from", pathPNG, "to", pathLocal
        copy(pathPNG, pathLocal)
        # The below should be in a try block in case it fails:
        # We have to find the USB device, so:
        try:
            pathUSB = "/media/pi/" + os.listdir("/media/pi")[0] + "/" + imageName
            print "Copying image from", pathPNG, "to", pathUSB
            copy(pathPNG, pathUSB)
        except:
            print "There was an issue copying to USB."
            return pathPNG, pathLocal, None
            
        # Return exactly what/where we saved the file, so the user can delete it if they want...
        return pathPNG, pathLocal, pathUSB
        
    # Return because we have nothing left to do...
    return None

    
"""
A function that finds 4 corner-ish pixels of an image, see if they're about green, and then if they are,
averages them to find the approximate color of the green screen.

This fucntion takes a PIL HSV image (surface) and a list of points to use as reference:
"""
def getColorMean(PilHsvImage, refPoints):
    # Let's see how big the image is and make sure it's big enough...
    width, height = PilHsvImage.size
    if (width < 101) or (height < 101):
        return None

    # Create a list to store the pixel data and a numerator to properly take the avg:
    pixList = []
    numerator = 0
        
    # Identify how we're indexing the far corners:
    for point in refPoints:
        pixList.append(PilHsvImage.getpixel(point))
        numerator += 1
    
    # For loop to iterate through each chosen pixel, as above:
    H = 0
    S = 0
    V = 0
    
    for pixel in xrange(len(pixList)):
        H += pixList[pixel][0]
        S += pixList[pixel][1]
        V += pixList[pixel][2]
                    
    # Now we can compute the mean of the valid HSV values:
    # use Try for the case in which each corner is invalid...
    try:
        H = H / numerator
        S = S / numerator
        V = V / numerator
    except:
        return None
    
    # And now we can return:
    return H, S, V

"""
A function to allow the user to choose greenspace.

Takes a Pygame webcam, (what is imagen in the Main file,) a star font, and a Pygame screen
object.  Returns 4 tuples of pixels that are 'known' to be green in a list.

This function was born primarily out of the main function in greenscreenMain.py,
so if you don't get how it works, look there first.

NOTE: PiGPIO must already be initialized!
"""
def getReferencePoints(surface, webcam, font, starFont, controlPin):
    # A control variable to see if we should close; initialize to False as we
    # want to start the loop, but assume it's going to be the last time they run it.
    # (See how this is used at the end of the while loops.)
    shouldClose = False
    while shouldClose == False:
        # Tuples of star locations will be stored in this list:
        starLocations = []
        while len(starLocations) < 4:
            # Take an image and display it in the upper right hand corner:
            imagen = webcam.get_image()
            surface.blit(imagen, (0, 0))
            
            # Tell the user what to do:
            message = "Choose 4 points that are green for reference, or press button to cancel."
            color = (0, 0, 255)
            setText(surface, font, message, color)
            
            # If the user has yet chosen stars, go ahead and display them:
            if len(starLocations) > 0:
                for starPoint in starLocations:
                    setText(surface, starFont, '*', (255, 0, 0), starPoint)
                    
            # Update the display:
            pygame.display.update()
            
            # Now we can get events and see if anything has happened:
            events = pygame.event.get()
            for event in events:
                # If the user has DEclicked: (mouse button up,):
                if event.type == 5:
                    starLocations.append(event.dict['pos'])
                    break
                
            # See if the button was hit, (again, it's a low-active pin, so False means it was triggered):
            if GPIO.input(controlPin) == False:
                return None
            
            time.sleep(0.005)
        
        # Now we should show the user the points they chose.
        
        # Change value of the control var because we assume the user wants to close:
        shouldClose = True
        
        # Initiate a time keeping var:
        time_start = time.time()
        while (time.time() - time_start < 5) and shouldClose == True:
            # Take an image and display it in the upper right hand corner:
            imagen = webcam.get_image()
            surface.blit(imagen, (0, 0))
            message = "Verify chosen points; press button to reselect."
            color = (0, 0, 255)
            setText(surface, font, message, color)
            
            # Display each point:
            for starPoint in starLocations:
                setText(surface, starFont, '*', (255, 0, 0), starPoint)
            
            # Update the display:
            pygame.display.update()
            
            # Check if they hit the button:
            if GPIO.input(controlPin) == False:
                shouldClose = False
                
            time.sleep(0.005)
    
    # The while loop terminated because shouldClose == True:
    return starLocations
        
        
    
"""
A function that prints a message in some color at the center of the screen.
It then returns the screen object.

Takes a surface to print on, a font to render in, a message (str) to render,
and an RGB tuple value for the color.  Can also accept a location value, which
will place the object at that location.

Types:
    surface is a pygame.display.Display type
    font is a pygame.font.Font type
    message is a str.
    color is a tuple (R, G, B)
    location is a tuple (x, y)
"""
def setText(surface, font, message, color, location = None):
    # If they haven't provided a location, we'll assume they want it centered:
    if location == None:
        messageRendered = font.render(message, True, color)
        messageLoc = messageRendered.get_rect()
        messageLoc.centerx = surface.get_rect().centerx
        messageLoc.centery = surface.get_rect().centery
        surface.blit(messageRendered, messageLoc)
        return
    # They have provided a location, so we'll go ahead and place the object there:
    else:
        messageRendered = font.render(message, True, color)
        messageLoc = messageRendered.get_rect()
        messageLoc.centerx = location[0]
        messageLoc.centery = location[1]
        surface.blit(messageRendered, messageLoc)
        surface.blit(messageRendered, messageLoc)
        return

"""
A function to delete files from given directories.

Takes a surface, the path to the official, source-rendered image, (what getImage returns)
and a list of strings indicating where the images are saved.
"""
def delImage(surface, font, pathOfficial, listOfPathOthers):
    imagen = pygame.image.load(pathOfficial)
    surface.blit(imagen, (0, 0))
    message = "Deleting image..."
    color = (255, 255, 255)
    # We want to use the default value of font, so we have to do this:
    setText(surface, font, message, color)
    for file in pathOthers:
        try:
            os.remove(file)
        except:
            print "There was an error removing the file at", file
    return
        
    