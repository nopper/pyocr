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

import gtk
import gobject

import os
import cPickle as pickle

from bpnn.network import Network

from gui import *
from gui.pages.training import TrainingPage
from gui.pages.practice import PracticePage
from gui.pages.recognize import RecognizePage
from gui.widgets.inputwidget import InputWidget

try:
    import psyco
    psyco.full()
except:
    print 'Install python-psyco for extra speed'

class NeuralApp(object):
    def __init__(self):
        idx = 0
        self.networks = []

        for name, fname in zip(
            map(lambda x: x[0].lower(), ALPHABETS),
            NETWORK_FILES):

            try:
                f = open(fname, 'r')
                setattr(self, name, pickle.load(f))
                f.close()

                if DEBUG:
                    print 'Network %s loaded correctly from %s' \
                          % (name, fname)

            except Exception, err:
                inputs = (NINPUT_NEURONS[idx], NHIDDEN_NEURONS[idx],
                          len(ALPHABETS[idx][1]), LEARNING_RATE)

                if DEBUG:
                    print "Creating new neural network with", inputs

                #self._network = Network(165, 80, len(ALFABETO), 0.2)
                setattr(self, name, Network(*inputs))

            self.networks.append(getattr(self, name))
            idx += 1

    def save_network(self, idx):
        net = self.networks[idx]
        
        with open(NETWORK_FILES[idx], 'w') as f:
            pickle.dump(net, f)

    def get_network(self, idx):
        return self.networks[idx]

class OCRApp(gtk.Window, NeuralApp):
    def __init__(self):
        gtk.Window.__init__(self)
        NeuralApp.__init__(self)

        self._locked = False

        self.set_title('OCR - neural network')
        self.set_border_width(4)
        self.connect('destroy', lambda w: gtk.main_quit())

        hbox = gtk.HBox(spacing=4)
        self.add(hbox)

        self.area = InputWidget()
        self.area.set_size_request(200, 200)

        self.combo = gtk.combo_box_new_text()

        for title, letters in ALPHABETS:
            self.combo.append_text(title)

        self.combo.set_active(0)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        frame.add(self.area)

        vbox = gtk.VBox(spacing=2)
        vbox.pack_start(frame, False, False)
        vbox.pack_end(self.combo, False, False)

        hbox.pack_start(vbox, False, False)

        self.notebook = gtk.Notebook()

        for page in (TrainingPage(self), \
                     RecognizePage(self), \
                     PracticePage(self)):

            self.notebook.append_page(page, page.get_label_widget())
            page.show()

        hbox.pack_end(self.notebook)

        self.show_all()

    def get_locked(self):
        return self._locked
    
    def set_locked(self, value):
        lock = not value

        self.combo.set_sensitive(lock)
        self.area.set_sensitive(lock)

    def run(self):
        gobject.threads_init()
        gtk.main()

    locked = property(get_locked, set_locked)
