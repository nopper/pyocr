# -*- coding: utf-8 -*-
# Copyright (C) 2009 Francesco Piccinno
#
# Author: Francesco Piccinno <stack.box@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys

from math import sqrt
from copy import copy
from PIL import Image, ImageChops

PIXELS = 10
IMG_PIXELS = 32

ALPHABETS = (
    ('Numbers', '0123456789'),
    ('Uppercase', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
    ('Lowercase', 'abcdefghijklmnopqrstuvwxyz'),
)

NETWORK_FILES = (
    'numbers.pkl',
    'uppercase.pkl',
    'lowercase.pkl',
)

NINPUT_NEURONS = (
    PIXELS * PIXELS,
    PIXELS * PIXELS,
    PIXELS * PIXELS,
)

NHIDDEN_NEURONS = (
    (PIXELS * len(ALPHABETS[0][1])) / 3,
    (PIXELS * len(ALPHABETS[1][1])) / 3,
    (PIXELS * len(ALPHABETS[2][1])) / 3,
)

LEARNING_RATE = 0.1

BRUSH_SIZE = 7
DEBUG = True

class memoized(object):
    """
    Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args, **kwargs):
        try:
            if 'cacheable' in kwargs and kwargs['cacheable'] != True:
                raise TypeError('') # Dummy hack

            return self.cache[args]
        except KeyError:
            self.cache[args] = value = self.func(*args)
            return value
        except TypeError:
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

###############################################################################
# Utilities functions
###############################################################################

def scaled_from_rawdata(rawdata, w=IMG_PIXELS, h=IMG_PIXELS, stride=0, \
                        format='RGBX'):
    """
    Create a scaled PIXEL x PIXEL image from rawdata
    @param rawdata: str containing the raw image
    @param w: width of the raw image
    @param h: height of the raw image
    @param stride: leave 0
    @param format: a string representing input image format
    @return: a PIL.Image object at size (IMG_PIXELS, IMG_PIXELS)
    """
    first_image = Image.frombuffer(format, (w, h), rawdata[:],
                                   'raw', format, stride, 1)
    raw = first_image.load()

    # Now we have to find where character fits.

    row_min, row_max = h, 0
    col_min, col_max = w, 0

    for y in xrange(w):
        for x in xrange(h):
            if raw[x, y][0] == 0:
                row_min = min(row_min, y)
                row_max = max(row_max, y)
                col_min = min(col_min, x)
                col_max = max(col_max, x)

    #out = first_image.crop((col_min, row_min, col_max, row_max))
    out = first_image.crop((0, row_min, w, row_max))
    out = ImageChops.duplicate(out)
    out = out.resize((IMG_PIXELS, IMG_PIXELS), Image.BILINEAR)

    if DEBUG:
        try:
            first_image.save('images/before.png', 'PNG')
            out.save('images/after.png', 'PNG')
        except:
            pass

    return out

@memoized
def find_target(char, idx):
    """
    Simple function (memoized) that create a target
    list() with '1' in position where the target letter
    is located.
    @return: a list() with one '1' and all '0'
    """
    alphabet = ALPHABETS[idx][1]
    neurons = [0] * len(alphabet)
    neurons[alphabet.index(char)] = 1
    return neurons

@memoized
def check_receptor(img):
    """
    Prepare the input of the neural network
    @param img: a PIL.Image at size (IMG_PIXELS, IMG_PIXELS)
    @return: a list() that should be used to feed your neural network
    """
    raw = img.load()
    receptor_states = [0] * (PIXELS * PIXELS)

    xstep = IMG_PIXELS / float(PIXELS)
    ystep = IMG_PIXELS / float(PIXELS)

    for i in xrange(0, IMG_PIXELS):
        for j in xrange(0, IMG_PIXELS):

            x = int(j / xstep)
            y = int(i / ystep)

            color = raw[j, i]

            if DEBUG:
                if color[0] != 255:
                    sys.stdout.write("# ")
                else:
                    sys.stdout.write("_ ")

            value = sqrt(color[0] ** 2 + \
                         color[1] ** 2 + \
                         color[2] ** 2)
            receptor_states[y * PIXELS + x] += value

        if DEBUG:
            sys.stdout.write('\n')

    imax = max(receptor_states)

    if imax > 0:
        receptor_states = map(lambda x: x / imax, receptor_states)

    if DEBUG:
        idx = 0

    for i in receptor_states:

        if DEBUG:
            if i <= 0.50: sys.stdout.write("# ")
            else: sys.stdout.write("_ ")

            idx += 1

            if idx == PIXELS:
                sys.stdout.write('\n')
                idx = 0

    return receptor_states

def guess_letter(network, receptor_states, idx):
    """
    Guess the letter returning back the character with highest score
    @param network: your neural network
    @param receptor_states: the input to feed your neural network
    @param idx: the alphabet index
    @return: guessed character
    """

    output = network.test(receptor_states)

    i = 0
    highest = 0

    for o_neuron in output:
        if o_neuron > output[highest]:
            highest = i
        i += 1

    return ALPHABETS[idx][1][highest]
