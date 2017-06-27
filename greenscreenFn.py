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
import time
from PIL import Image
from PIL import ImageFilter
from shutil import copy

"""
The main image capture and processing function.

This function takes an image, saves it in tmp, re-imports it into PIL so it can be processed;
removes colors that fall within the specified range and replaces them with transperancy,
and then saves it as a .PNG again to a certain path.

This function returns only the location where it saved the final image AND where it saved the .PNG (/tmp/image.png).
"""
def recordImage(i, threshold, webcam, screen, font):
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
    screen.blit(imagen, (0,0))
    message = "Saving and processing image, please wait..."
    message = font.render(message, True, (72, 118, 255))
    screen.blit(message, (220, 220))
    pygame.display.update()
    
    # Now we can open the image with PIL, and convert it to RGBA AND HSV:
    ###
    # For testing purposes, you can uncomment the below to manually point to an image.
    # pathJPG = raw_input("Please enter the path and image name of the desired image to be procesed:")
    imgRGBA = Image.open(pathJPG)
    imgRGBA = imgRGBA.convert("RGBA")
    imgHSV = imgRGBA.convert("HSV")
    
    # Let's use our HSVMean() function to identify the approximate color of the green screen:
    hsvData = HSVMean(imgHSV)
    
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
        pathSave = "/home/pi/Photos/"
        imageName = "%(1)s_%(2)s_%(3)s.png" % {"1": hi,"2": ti,"3" : i}
        pathFinal = pathSave + imageName
        print "Copying image from", pathPNG, "to", pathFinal
        copy(pathPNG, pathFinal)
        # The below should be in a try block in case it fails:
        # We have to find the USB device, so:
        try:
            pathUSB = "/media/pi/" + os.listdir("/media/pi")[0] + "/" + imageName
            print "Copying image from", pathPNG, "to", pathUSB
            copy(pathPNG, pathUSB)
        except:
            print "There was an issue copying to USB."

        # Numerate our numerator so we can create unique file names...
        i = i+1
            
        # Return exactly what/where we saved the file, so the user can delete it if they want...
        return pathFinal, pathPNG, pathUSB
        
    # Return because we have nothing left to do...
    return None

    
"""
A function that finds 4 corner-ish pixels of an image, see if they're about green, and then if they are,
averages them to find the approximate color of the green screen.

This fucntion takes a PIL HSV image (surface).
"""
def HSVMean(PilHsvImage):
    # Let's see how big the image is and make sure it's big enough...
    width, height = PilHsvImage.size
    if (width < 101) or (height < 101):
        return None
        
    # Identify how we're indexing the far corners:1
    negWidth = width - 100
    negHeight = height - 100
    pix1 = PilHsvImage.getpixel((100, 100))
    pix2 = PilHsvImage.getpixel((negWidth, 100))
    pix3 = PilHsvImage.getpixel((100, negHeight))
    pix4 = PilHsvImage.getpixel((negWidth, negHeight))
    
    # Let's make a list of the data so it's easier to use:
    pixList = [pix1, pix2, pix3, pix4]
    
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
        H = H / 4
        S = S / 4
        V = V / 4
    except:
        return None
    
    # And now we can return:
    return H, S, V
