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

from gui import guess_letter
from gui.pages import GenericPage

class RecognizePage(GenericPage):
    title = 'Recognize'
    image = gtk.STOCK_GO_FORWARD

    def create_ui(self):
        self.buff = gtk.TextBuffer()
        self.text = gtk.TextView(self.buff)
        self.text.set_wrap_mode(gtk.WRAP_WORD_CHAR)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.add(self.text)

        self.pack_start(sw)
        self.owner.area.connect('character-changed', self.__on_recognize)

    def __on_recognize(self, btn, receptor_states):
        if self.is_active():
            alp_idx = self.get_alphabet_index()
            network = self.owner.get_network(alp_idx)

            res = guess_letter(network, receptor_states, alp_idx)
            self.buff.insert(self.buff.get_end_iter(), res)
