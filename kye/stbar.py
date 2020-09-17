# -*- coding: utf-8 -*-
#    Kye - classic puzzle game
#    Copyright (C) 2005, 2006, 2007, 2010 Colin Phipps <cph@moria.org.uk>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

"""Classes for the status bar for the Kye game GUI."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class StatusBarKyes(Gtk.DrawingArea):
    """Small gtk DrawingArea-derived widget for the bottom-left of the game display, showing lives left."""

    def __init__(self, kyeimg):
        Gtk.DrawingArea.__init__(self)
        self.set_size_request(20*3+4, 20)
        self.__kyeimg = kyeimg
        self.connect("draw", self.draw_event)
        self.__kyes = None

    def draw_event(self, da, cairo_ctx):
        """Handle redraws."""
        style_ctx = da.get_style_context()
        width = da.get_allocated_width()
        height = da.get_allocated_height()
        Gtk.render_background(style_ctx, cairo_ctx, 0, 0, width, height)

        if self.__kyes is not None:
            for n in range(self.__kyes):
                Gdk.cairo_set_source_pixbuf(cairo_ctx, self.__kyeimg, n*20, 0)
                cairo_ctx.paint()

    def update(self, num_kyes):
        """Set the number of kye lives to show; schedules a redraw if needed."""
        if num_kyes != self.__kyes:
            self.__kyes = num_kyes
            self.queue_draw_area(0, 0, 20*3+4, 20)


class StatusBar(Gtk.HBox):
    """Gtk widget for the Kye status bar."""
    string_map = {
        "diamonds": "Diamonds left",
        "levelnum": "Level",
        "hint": "Hint"
    }

    def __init__(self, kyeimg):
        Gtk.HBox.__init__(self)
        self.hint = None
        self.levelnum = None
        self.diamonds = None

        self.__kyes_widget = StatusBarKyes(kyeimg)
        self.pack_start(self.__kyes_widget, False, False, 2)

        for k in ("diamonds", "levelnum", "hint"):
            this_label = self.__dict__[k] = Gtk.Label("")
            this_label.set_alignment(0.5, 0.5)
            if k == "hint":
                # Need an eventbox around the hint label, so we can add a
                # tooltip later.
                add_widget = self.__hint_eventbox = Gtk.EventBox()
                add_widget.add(this_label)
            else:
                add_widget = this_label
            self.pack_start(add_widget, False, False, 3)
        self.show_all()

    def update(self, **keywords):
        """Update data displayed in the status bar."""
        for k, value in keywords.items():
            # hint text should also be added to the tooltip.
            if k == "hint":
                self.__hint_eventbox.set_tooltip_text(value)

            # The string labels we update; the kye count, we pass to the
            # special kyes widget.
            if k in StatusBar.string_map:
                self.__dict__[k].set_text(
                    "%s: %s" % (StatusBar.string_map[k], value))
            elif k == "kyes":
                self.__kyes_widget.update(value)
