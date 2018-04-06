# Welcome to the WMSI Autogreenscreen!
This program allows the user to take an image with a webcam attached to a Raspberry Pi, select the background color to be removed from the taken image, and will output the image with the background removed.

This project is a derivative of the work done by the Tufts Maker Network, (see their GitHub at https://github.com/tuftsceeo/Documentation-Station)  Ultimately, however, the project is different enough that it warrants a unique repository of its own.

## A note on contibuting to this script:
To contribute to this program, be sure to contribute to the `dev` branch.  (Ei., run `git checkout dev` once you've cloned into this repo.)  This will allow you to continue from the most recent additions to this program without interfering with the installed version on the Mobile Pi.

## Dependencies
The dependencies for this project are listed as all the packages imported into Python at the beginning of greenscreenMain.py.  However, they are:
* PIL (the Python Imaging Library)
* RPi.GPIO
* os
* time
* pygame

## Usage
Use this script by running `python greenscreenMain.py` from the command line, or by running one of the shortcuts created onthe Mobile Pi's desktop.
