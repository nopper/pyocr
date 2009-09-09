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

class AdaptableWidget(gtk.VBox):
    def __init__(self, label, create_cb):
        assert callable(create_cb)

        gtk.VBox.__init__(self, False, 2)
        self.set_border_width(4)

        self.create_cb = create_cb
        self.label_fmt = label

        self.widgets = []
        self._append_new()

    def _append_new(self):
        lbl = gtk.Label(self.label_fmt)
        lbl.set_alignment(.0, .5)
        lbl.show()

        widget = self.create_cb()
        widget.show()

        idx = len(self.widgets)

        btn = gtk.Button()

        if idx != 0:
            btn.connect('clicked', self.__on_remove)
            b_image = gtk.image_new_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)
        else:
            btn.connect('clicked', self.__on_add)
            b_image = gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)

        b_image.show()

        btn.add(b_image)
        btn.set_relief(gtk.RELIEF_NONE)
        btn.show()

        hbox = gtk.HBox(False, 10)
        hbox.pack_start(lbl, False, False, 0)
        hbox.pack_start(widget)
        hbox.pack_start(btn, False, False, 0)
        hbox.show()

        self.pack_start(hbox, False, False, 0)

        self.widgets.append((lbl, widget, btn))

    def __on_add(self, _btn):
        self._append_new()

    def __on_remove(self, _btn):
        found = False

        for lbl, widget, btn in self.widgets:
            if btn is _btn:
                found = True
                break

        if found:
            lbl.hide()
            btn.hide()
            widget.hide()

            hbox = lbl.get_parent()
            hbox.hide()

            self.remove(hbox)
            self.widgets.remove((lbl, widget, btn))

    def foreach(self):
        return (y for x, y, z in self.widgets)
