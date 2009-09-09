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
import gtk
import cairo
import gobject

from random import choice
from threading import Thread
from collections import defaultdict

from gui import *
from gui.pages import GenericPage
from gui.widgets.adaptable import AdaptableWidget

class TrainingPage(GenericPage):
    title = 'Auto training'
    image = gtk.STOCK_ABOUT

    def create_ui(self):
        self.progress = gtk.ProgressBar()

        self.exec_btn = gtk.Button(stock=gtk.STOCK_EXECUTE)
        self.exec_btn.connect('clicked', self.__on_start_training)

        self.fonts = AdaptableWidget('Font:', gtk.FontButton)

        self.pack_start(self.fonts)
        self.pack_start(self.progress, False, False)
        self.pack_end(self.exec_btn, False, False)

        self.thread = None
        self.status = None

    def lock_widgets(self, lock):
        GenericPage.lock_widgets(self, lock)

        lock = not lock

        self.fonts.set_sensitive(lock)
        self.exec_btn.set_sensitive(lock)

    def __on_start_training(self, widget):
        self.lock_widgets(True)

        # Initialize the cairo surface and relative context
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, IMG_PIXELS, IMG_PIXELS)
        ctx = cairo.Context(surface)

        # Disable antialias for font rendering
        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_NONE)
        fo.set_hint_style(cairo.HINT_STYLE_NONE)

        ctx.set_font_options(fo)

        train_dict = defaultdict(list)

        for fntbtn in self.fonts.foreach():
            font = fntbtn.get_font_name()

            # Select new font face
            ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(IMG_PIXELS)

            for char in self.get_alphabet():
                ctx.set_source_rgb(1, 1, 1)
                ctx.rectangle(0, 0, IMG_PIXELS, IMG_PIXELS)
                ctx.fill()

                ctx.set_source_rgb(0, 0, 0)
                x_bearing, y_bearing, width, height = ctx.text_extents(char)[:4]

                fx = IMG_PIXELS / 2
                fy = IMG_PIXELS / 2

                fx = fx - width / 2 - x_bearing
                fy = fy - height / 2 - y_bearing

                ctx.move_to(fx, fy)
                ctx.show_text(char)

                train_dict[char].append(
                    scaled_from_rawdata(surface.get_data())
                )

                #if DEBUG:
                #   surface.write_to_png("images/" + str(ord(char)) + ".png")

        self.thread = Thread(target=self.__on_train, args=(train_dict, ))
        self.thread.setDaemon(True)
        self.thread.start()

        gobject.timeout_add(500, self.__update_percentage)

    def __update_percentage(self):
        text, percentage = self.status

        self.progress.set_fraction(percentage)
        self.progress.set_text(text)

        working = (self.thread and self.thread.isAlive() or False)

        if not working:
            self.lock_widgets(False)

        return working

    def __on_train(self, tdict):
        """
        Learning thread function
        @param tdict: a dictionary containing the scaled images
        """
        correct = 0
        previous = []
        keys = tdict.keys()

        alp_idx = self.get_alphabet_index()
        network = self.owner.get_network(alp_idx)

        for i in xrange(100000):
            target = choice(keys)
            image  = choice(tdict[target])

            receptor_states = check_receptor(image)
            guess = guess_letter(network, receptor_states, alp_idx)

            e = network.train(
                receptor_states,
                find_target(target, alp_idx)
            )

            hit = (guess == target)

            if len(previous) == 1000:
                previous.pop(0)

            previous.append(hit)
            success = \
                float(len([a for a in previous if a])) / len(previous) * 100

            if DEBUG:
                sys.stdout.write(
                  '\rLetter was %s, guessed %s (err: %2.6f) - %s - %.1f%%' % \
                  (target, guess, e, hit and 'right' or 'wrong', success)
                )

            correct = hit and correct + 1 or 0

            if success > 98 and len(previous) == 1000:
                print 'Greater than 98% success over 1000 guesses'
                break

            if i % 5 == 0:
                self.status = ('%.1f%% - Letter was %s, guessed %s (err: %2.6f) - %s' %
                               (success, target, guess, e, hit and 'right' or 'wrong'),
                               success / 100.0)

            if i % 100 == 0:
                self.owner.save_network(alp_idx)
