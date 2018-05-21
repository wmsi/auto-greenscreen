#!/usr/bin/python
"""
Asher Merrill, WMSI

See grnscrn.py for more details.
"""

import datetime
import os
from shutil import copy
import time

from PIL import Image
from PIL import ImageFilter
import pygame
import pygame.camera
import RPi.GPIO as GPIO
import grnscrn_extractor as extract

def img(i, threshold, webcam, surface, font, ref_points):
    """
    Takes an image, saves it in tmp, re-imports it into PIL so it
    can be processed; removes colors that fall within the specified range and
    replaces them with transperancy, and then saves it as a .PNG again to a
    certain path.

    This function returns only the location where it saved the final image AND
    where it saved the .PNG (/tmp/image.png).
    """
    # Date-time strings for naming:
    day = str(datetime.datetime.now().date()).replace(".", "_").\
                                            replace(" ", "_").replace(":", "_")
    minute = str(datetime.datetime.now().time()).replace(".", "_").\
                                       replace(" ", "_").replace(":", "_")[0:4]


    # Capture and then save our image, so we can open it with PIL:
    imagen = webcam.get_image()

    # Alert to save, and save:
    path_PNG = "/tmp/image.png"
    path_JPG = "/tmp/image.jpg"
    print "Saving tmp. image in", path_JPG
    pygame.image.save(imagen, path_JPG)

    # Update screen:
    surface.blit(imagen, (0, 0))
    message = "Saving and processing image, please wait..."
    color = (255, 255, 255)
    disp_text(surface, font, message, color)
    pygame.display.update()

    # Open image with PIL, and convert it to RGBA AND HSV:
    jpg = Image.open(path_JPG).convert('RGBA')
    jpg_HSV = jpg.convert("HSV")

    # Identify color of greenscreen:
    green = mean_color(jpg_HSV, ref_points)

    # PROCESS IMAGE
    H, S, V = green
    pixdata = jpg.load()
    for y in xrange(jpg.size[1]):
        for x in xrange(jpg.size[0]):
            r, g, b, a = jpg.getpixel((x, y))
            h, s, v = jpg_HSV.getpixel((x, y))
            if (H - threshold <= h <= H + threshold):
                pixdata[x, y] = (255, 255, 255, 0)
            # Remove anti-aliasing outline of body.
            if r == 0 and g == 0 and b == 0:
                pixdata[x, y] = (255, 255, 255, 0)
    imgOut = jpg.filter(ImageFilter.GaussianBlur(radius=1))
    print "Saving tmp. image in", path_PNG
    imgOut.save(path_PNG, "PNG")

    # Copy image from /tmp/
    name = "%(1)s_%(2)s_%(3)s.png" % {"1": day, "2": minute, "3" : i}
    # Start defining some of the other names:
    pathLocal = os.path.join("/home/pi/Pictures/", name)
    print "Copying image from", path_PNG, "to", pathLocal
    copy(path_PNG, pathLocal)
    # The below should be in a try block in case it fails:
    # We have to find the USB device, so:
    try:
        path_USB = os.path.join("/media/pi/", os.listdir("/media/pi")[0], name)
        print "Copying image from", path_PNG, "to", path_USB
        copy(path_PNG, path_USB)
    except:
        print "There was an issue copying to USB."
        return path_PNG, pathLocal, None

    # Return exactly what/where we saved the file, so the user can delete
    # it if they want...
    return path_PNG, pathLocal, path_USB


def mean_color(PIL_HSV_image, ref_points):
    """
    Averages the HSV values of `n` points in an image and returns their
    average.
    """
    # Check and make sure everything we're doing is valid:
    width, height = PIL_HSV_image.size
    if (width < 101) or (height < 101):
        raise ValueError('The image being processed is too small!')
    elif not ref_points:
        raise ValueError('Cannot have 0 reference points!')

    # Find the average HSV values for the 4 (or n) points:
    pix_list = [PIL_HSV_image.getpixel(p) for p in ref_points]
    H = sum([i[0] for i in pix_list]) / len(pix_list)
    S = sum([i[1] for i in pix_list]) / len(pix_list)
    V = sum([i[2] for i in pix_list]) / len(pix_list)

    return H, S, V

def reference_points(surface, webcam, font, star_font, control_pin):
    """
    A function to allow the user to choose greenspace.

    Takes a Pygame webcam, (what is imagen in the Main file,) a star font, and
    a Pygame screen object.  Returns 4 tuples of pixels that are 'known' to be
    green in a list.

    This function was born primarily out of the main function in
    greenscreenMain.py, so if you don't get how it works, look there first.

    NOTE: PiGPIO must already be initialized!
    """
    close = False
    while close is False:
        # Tuples of star locations will be stored in this list:
        star_locs = []
        while len(star_locs) < 4:
            # Take an image and display it in the upper right hand corner:
            imagen = webcam.get_image()
            surface.blit(imagen, (0, 0))

            # Tell the user what to do:
            message = "Choose 4 points that are green for reference, or press"\
                      " button to cancel."
            color = (0, 0, 255)
            disp_text(surface, font, message, color)

            # Display all chosen points so far:
            if star_locs:
                for p in star_locs:
                    disp_text(surface, star_font, '*', (255, 0, 0), p)
            pygame.display.update()

            # Now we can get events and see if anything has happened:
            events = pygame.event.get()
            for e in events:
                # If the user has DEclicked: (mouse button up,):
                if e.type == 5:
                    star_locs.append(e.dict['pos'])
                    break

            # See if the button was hit, (again, it's a low-active pin, so
            # False means it was triggered):
            if GPIO.input(control_pin) is False:
                surface.blit(imagen, (0, 0))
                message = "Defaulting reference points and closing, please"\
                          "wait..."
                color = (255, 255, 255)
                disp_text(surface, font, message, color)
                pygame.display.update()
                time.sleep(3)
                return None

            time.sleep(0.005)

        close = True # Done here after they verify, so...

        # Now have the user verify their chosen points:
        time_start = time.time()
        wait_time = 5.
        while (time.time() - time_start < wait_time) and close is True:
            # Update display:
            imagen = webcam.get_image()
            surface.blit(imagen, (0, 0))
            message = "Verify chosen points; press button to reselect."
            color = (0, 0, 255)
            disp_text(surface, font, message, color)

            # Display each point:
            for s in star_locs:
                disp_text(surface, star_font, '*', (255, 0, 0), s)

            pygame.display.update()
            time.sleep(0.005)

            # Check if they hit the button:
            if GPIO.input(control_pin) is False:
                close = False # Need to reset from above
                surface.blit(imagen, (0, 0))
                message = "Restarting, please wait..."
                color = (255, 255, 255)
                disp_text(surface, font, message, color)
                pygame.display.update()
                time.sleep(3)

    # The while loop terminated because shouldClose == True:
    return star_locs


def disp_text(surface, font, message, color, location=None):
    """
    A function that prints a message in some color at the center of the screen.
    It then returns the screen object.

    Takes a surface to print on, a font to render in, a message (str) to render
    and an RGB tuple value for the color.  Can also accept a location value,
    which will place the object at that location.

    Types:
        surface is a pygame.display.Display type
        font is a pygame.font.Font type
        message is a str.
        color is a tuple (R, G, B)
        location is a tuple (x, y)
    """
    # No location, assume center:
    if location is None:
        msg_rend = font.render(message, True, color)
        msg_loc = msg_rend.get_rect()
        msg_loc.centerx = surface.get_rect().centerx
        msg_loc.centery = surface.get_rect().centery
        surface.blit(msg_rend, msg_loc)
    else:
        msg_rend = font.render(message, True, color)
        msg_loc = msg_rend.get_rect()
        msg_loc.centerx = location[0]
        msg_loc.centery = location[1]
        surface.blit(msg_rend, msg_loc)


def rm_img(surface, font, pathOfficial, listOfPathOthers):
    """
    A function to delete files from given directories.

    Takes a surface, the path to the official, source-rendered image,
    (what getImage returns) and a list of strings indicating where the
    images are saved.
    """
    surface.fill((169, 169, 169))
    imagen = pygame.image.load(pathOfficial)
    surface.blit(imagen, (0, 0))
    message = "Deleting image..."
    color = (255, 255, 255)
    disp_text(surface, font, message, color)
    pygame.display.update()

    # We want to use the default value of font, so we have to do this:
    disp_text(surface, font, message, color)
    for f in listOfPathOthers:
        try:
            print "Deleting image from", f
            os.remove(f)
        except:
            print "There was an error removing the file at", f
