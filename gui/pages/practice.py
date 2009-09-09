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

from gui import find_target
from gui.pages import GenericPage

class PracticePage(GenericPage):
    title = 'Practice'

    def create_ui(self):
        lbl = self.new_label('Target:')
        self.status = self.new_label('')

        self.combo = gtk.combo_box_new_text()
        self.update()

        hbox = gtk.HBox(False, 10)
        hbox.set_border_width(4)
        hbox.pack_start(lbl, False, False)
        hbox.pack_start(self.combo)

        self.pack_start(hbox, False, False)
        self.pack_start(self.status, False, False)

        self.owner.combo.connect('changed', lambda w: self.update())
        self.owner.area.connect('character-changed', self.__on_recognize)

    def update(self):
        self.combo.get_model().clear()

        for char in self.get_alphabet():
            self.combo.append_text(char)

        self.combo.set_active(0)

    def __on_recognize(self, widget, receptor_states):
        if not self.is_active():
            return

        alp_idx = self.get_alphabet_index()
        network = self.owner.get_network(alp_idx)

        old = network.learning_rate

        network.learning_rate = 1.0
        network.train(receptor_states,
                      find_target(self.combo.get_active_text(), alp_idx))
        network.learning_rate = old
