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

from gui import ALPHABETS

class GenericPage(gtk.VBox):
    title = 'GenericPage'
    image = gtk.STOCK_INFO

    def __init__(self, owner):
        gtk.VBox.__init__(self, False, 2)
        self.set_border_width(4)
        self.owner = owner

        self.create_ui()

    def create_ui(self):
        pass

    def new_label(self, txt, bold=False):
        label = gtk.Label('')
        label.set_alignment(.0, .5)

        if bold:
            label.set_markup('<b>%s</b>' % txt)
        else:
            label.set_text(txt)

        return label

    def get_label_widget(self):
        img = gtk.image_new_from_stock(self.image, gtk.ICON_SIZE_MENU)
        label = self.new_label(self.title, True)

        hbox = gtk.HBox(False, 2)
        hbox.pack_start(img, False, False)
        hbox.pack_end(label)
        hbox.show_all()

        return hbox

    def get_alphabet(self):
        idx = self.owner.combo.get_active()
        return ALPHABETS[idx][1]

    def get_alphabet_index(self):
        return self.owner.combo.get_active()

    def lock_widgets(self, lock):
        self.owner.locked = lock

    def is_active(self):
        pn = self.owner.notebook.get_current_page()
        return self.owner.notebook.page_num(self) == pn
