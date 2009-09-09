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
import cairo
import gobject

from math import pi, sqrt
from gui import check_receptor, scaled_from_rawdata, DEBUG, BRUSH_SIZE

EPSILON = 0.0001
CHANGED_TIMEOUT = 600

class InputWidget(gtk.DrawingArea):
    __gtype_name__ = 'OCRInput'
    __gsignals__ = {
        'character-changed' : (gobject.SIGNAL_RUN_FIRST,
                               gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    }

    def __init__(self):
        gtk.DrawingArea.__init__(self)

        self.pixmap = None
        self.tracking = False
        self.lastpoint = (0, 0)
        self.brush_distance = 0
        self.brush_spacing = 1.0

        self.timeout_id = None

    def do_realize(self):
        self.set_events(gtk.gdk.EXPOSURE_MASK |
                        gtk.gdk.LEAVE_NOTIFY_MASK |
                        gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)
        gtk.DrawingArea.do_realize(self)

    def do_configure_event(self, evt):
        width, height = self.window.get_size()
        self.pixmap = gtk.gdk.Pixmap(self.window, width, height)
        self.pixmap.draw_rectangle(self.style.white_gc, True,
                                   0, 0, width, height)
        return True

    def do_expose_event(self, evt):
        x, y, width, height = evt.area
        gc = self.style.fg_gc[gtk.STATE_NORMAL]
        self.window.draw_drawable(gc, self.pixmap, x, y, x, y, width, height)
        return False

    def __on_complete(self):
        self.emit('character-changed', self.get_receptor())
        self.clear()

        return False

    def do_button_press_event(self, evt):
        if evt.button == 1 and self.pixmap != None and not self.tracking:

            if self.timeout_id:
                gobject.source_remove(self.timeout_id)
                self.timeout_id = None

            self.tracking = True

            ctx = self.pixmap.cairo_create()

            self._draw_point(ctx, evt.x, evt.y)
            self.lastpoint = (evt.x, evt.y)

            self.queue_draw()

        self.brush_distance = 0
        return True

    def do_button_release_event(self, evt):
        if evt.button == 1 and self.pixmap != None and self.tracking:
            self.tracking = False

            self.timeout_id = gobject.timeout_add(
                CHANGED_TIMEOUT, self.__on_complete
            )

        return True

    def do_motion_notify_event(self, evt):
        if not self.tracking:
            return True

        if evt.is_hint:
            x, y, state = evt.window.get_pointer()
        else:
            x , y = evt.x, evt.y
            state = evt.state

        x -= 1
        y -= 1
        width, height = self.window.get_size()

        if x > 0 and y > 0 and x < width and y < height and \
           state & gtk.gdk.BUTTON1_MASK and self.pixmap != None:

            self._interpolate(x, y)
            self.queue_draw()

        return True

    def _interpolate(self, x, y):
        initial_x, initial_y = x, y
        dx = x - self.lastpoint[0]
        dy = y - self.lastpoint[1]

        moved = sqrt(dx * dx + dy * dy)

        initial = self.brush_distance
        final = initial + moved

        ctx = self.pixmap.cairo_create()

        while self.brush_distance < final:
            points = self.brush_distance / self.brush_spacing + 1.0 + EPSILON
            next = points * self.brush_spacing - self.brush_distance
            self.brush_distance += next

            if self.brush_distance <= (final + EPSILON):
                percent = (self.brush_distance - initial) / moved
                x = self.lastpoint[0] + percent * dx
                y = self.lastpoint[1] + percent * dy

                self._draw_point(ctx, x, y)

        self.brush_distance = final
        self.lastpoint = (initial_x, initial_y)

    def _draw_point(self, ctx, x, y):
        ctx.save()
        ctx.set_source_rgb(0, 0, 0)
        ctx.translate(x + BRUSH_SIZE / 2., y + BRUSH_SIZE / 2.)
        ctx.scale(BRUSH_SIZE / 2., BRUSH_SIZE / 2.)
        ctx.arc(0., 0., 1., 0., 2 * pi)

        ctx.stroke()
        ctx.restore()

    def clear(self):
        width, height = self.window.get_size()
        self.pixmap.draw_rectangle(self.style.white_gc, True,
                                   0, 0, width, height)
        self.queue_draw()

    def get_receptor(self):
        """
        @return: a list like check_receptor()
        """
        width, height = self.window.get_size()

        # We need to transform the pixmap to a pixbuf
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,
                                False, 8, width, height)
        pixbuf.get_from_drawable(self.pixmap, gtk.gdk.colormap_get_system(),
                                 0, 0, 0, 0, width, height)

        if DEBUG:
            pixbuf.save('images/out.png', 'png', {})

        pixels = pixbuf.get_pixels()
        stride = pixbuf.get_rowstride()

        return check_receptor(
            scaled_from_rawdata(pixels, width, height, stride, 'RGB'),
            cacheable=False # Do not cache this image
        )
