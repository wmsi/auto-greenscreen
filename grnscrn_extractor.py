# -*- coding: utf-8 -*-
"""
Asher Merrill, WMSI

See grnscrn.py for more details.
"""

import numpy
import scipy
import scipy.misc
import sys

from PIL import Image
from PIL import ImageFilter


def rm_background(img_path, green, threshold, outname):
    # Open image:
    hsv = scipy.misc.imread(img_path, mode='HSV').reshape(-1, 3)
    rgba = scipy.misc.imread(img_path, mode='RGBA').reshape(-1, 3)
    scipy.misc.imsave(outname, numpy.array([rgba[i] if hsv[i, 0] -
                                            float(threshold) <= float(green)
                                            <= hsv[i, 0] + float(threshold)
                                            else numpy.append(rgba[i, 0:3], 0)
                                            for i in range(hsv.shape[0])],
                                           shape=hsv.shape))

#def rm_background_py(img_path, green, threshold, outname):
#    H, S, V = green
#    imgRGBA = Image.open(img_path).convert('RGBA')
#    imgHSV = imgRGBA.convert('HSV')
#    pixdata = imgRGBA.load()
#    for y in xrange(imgRGBA.size[1]):
#        for x in xrange(imgRGBA.size[0]):
#            r, g, b, a = imgRGBA.getpixel((x, y))
#            h, s, v = imgHSV.getpixel((x, y))
#            if (H - threshold <= h <= H + threshold):
#                pixdata[x, y] = (255, 255, 255, 0)
#            # Remove anti-aliasing outline of body.
#            if r == 0 and g == 0 and b == 0:
#                pixdata[x, y] = (255, 255, 255, 0)
#    _ = [pixdata[x, y] = (255, 255, 255, 0) if (H - threshold <= h
#     <= H + threshold) for y in range(imgRGBA.size[1]) for x in
#     range(imgRGBA.size[0])]
#    imgOut = imgRGBA.filter(ImageFilter.GaussianBlur(radius=1))
#    print "Saving tmp. image in", outname
#    imgOut.save(outname, "PNG")
    
if __name__ == '__main__':
    rm_background(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    