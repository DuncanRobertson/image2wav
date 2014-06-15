image2wav
=========

This program will generate a mono 16 bit wav file from an image file. The audio, when viewed in a spectrograph, will contain a resemblance to the source image. 

his was done after reading about Aphex Twin placing images in his music this way, and I thought software to do this task should not be difficult to write, given access to suitable image handling and Fourier transform libraries.
license
The program is copyright duncan@linuxbandwagon.com and released under the GPL 'as is'.

The program was developed with Python 1.5.2 on RedHat Linux 7.3. It should work on any system the Python language runs on, although the .wav output stuff has not been checked for endian issues.

Update: 17/10/2004 : After this project sitting idle for ages I have just tweaked it so it works with newer Python and Python Imaging Library.

Update: 15/6/2014 : As the old site for this was suffering bitrot may as well publish on github to keep the code available. Still works fine with modern Python 2.X

requirements

    The Python programming language. Most Linux distributions will have it, and it is available for Mac, MS-windows and others.
    The Python Imaging Library free from Pythonware.

The Fast Fourier transform functions I used are included in the program, but came from Recipes In Python

To install Python Imaging Library on Debian, do:

apt-get install python-imaging


