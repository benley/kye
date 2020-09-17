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

"""kye.canvas - module containing the KCanvas class, which implements the display of the game itself."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk
import cairo

from kye.common import xsize, ysize, findfile, KyeImageDir


class KCanvas(Gtk.DrawingArea):
    """A gtk DrawingArea which draws the game."""
    tilesize = 16

    def __init__(self, responder, tilesize=16):
        Gtk.DrawingArea.__init__(self)

        # Remember the tilesize, and set the canvas size appropriately.
        KCanvas.tilesize = tilesize
        self.set_size_request(KCanvas.tilesize*xsize, KCanvas.tilesize*ysize)

        # Set GTK window flags & expose handler.
        self.set_events(Gdk.EventMask.EXPOSURE_MASK
                        | Gdk.EventMask.KEY_PRESS_MASK
                        | Gdk.EventMask.KEY_RELEASE_MASK
                        | Gdk.EventMask.BUTTON_PRESS_MASK
                        | Gdk.EventMask.BUTTON_RELEASE_MASK
                        | Gdk.EventMask.POINTER_MOTION_MASK)
        self.set_can_focus(True)
        self.connect("draw", self.draw_event)

        # Set up mouse event handling.
        self.mouseto = responder.mouse_motion_event
        self.bpress = responder.button_press_event
        self.brelease = responder.button_release_event
        self.connect("motion_notify_event",  self.mouse_motion_event)
        self.connect("button_press_event",   self.button_press_event)
        self.connect("button_release_event", self.button_release_event)

        # Set up keyboard handling.
        if hasattr(responder, "key_press_event"):
            self.connect("key_press_event",   responder.key_press_event)
        if hasattr(responder, "key_release_event"):
            self.connect("key_release_event", responder.key_release_event)

        # Get the image directory and create the rendered image cache.
        imgdirname = findfile("images.tar.gz")
        if imgdirname is None:
            md = Gtk.MessageDialog(type=Gtk.MESSAGE_ERROR,
                                   message_format="Could not find tileset",
                                   buttons=Gtk.BUTTONS_OK)
            md.format_secondary_markup("You need a set of tile images - images.tar.gz - to run python-kye. There should be such a set included with python-kye, or you can download an alternate set from the website.")
            md.run()
            md.destroy()
            raise Exception("aborting, no tileset")
        self.imgdir = KyeImageDir(imgdirname)
        self.images = {}

        # Set up array holding the on-screen state.
        self.showboard = []
        for i in range(xsize * ysize):
            self.showboard.append("blank")

    def game_redraw(self, game, changed_squares):
        """Update the displayed game from the game in memory (e.g. after a game tick has run).

        game  -- the game object (we call get_tile on this to get the new state.
        changed_squares -- array containing true/false values to indicate which squares (may) have changed since the last rendering. Note that this is flattened, so it contains values for (0,0), (1,0), ..., (30,0), (0, 1), ... etc.

        Note that changed_squares is updated back to false for all tiles as they are queued for redrawing.
        """
        i = -1
        for y in range(ysize):
            for x in range(xsize):
                i = i + 1
                if changed_squares[i] == 1:
                    changed_squares[i] = None
                    tile = game.get_tile(x, y)
                    if tile != self.showboard[xsize*y+x]:
                        self.showboard[xsize*y+x] = tile
                        self.queue_draw_area(self.tilesize*x, self.tilesize*y,
                                             self.tilesize, self.tilesize)

    def get_image(self, tilename, tilesize=None) -> GdkPixbuf.Pixbuf:
        """Get a GDK PixBuf containing the rendered image for the named tile.

        If specified, tilesize overrides the current tile size of the canvas
        (e.g. to get images for dialogs or the status bar at an invariant size).
        """
        # Use current tilesize by default.
        if tilesize is None:
            tilesize = KCanvas.tilesize

        # Use cached image data if available.
        if tilesize == KCanvas.tilesize and tilename in self.images:
            return self.images[tilename]
        else:
            image_data = self.imgdir.get_tile(tilename)

            # Make gdk PixbufLoader, feed it the data, get the resulting pixbuf
            pixbuf_loader = GdkPixbuf.PixbufLoader()
            pixbuf_loader.set_size(tilesize, tilesize)
            pixbuf_loader.write(image_data)
            pixbuf_loader.close()
            pb = pixbuf_loader.get_pixbuf()
            if pb is None:
                raise KeyError("Incomplete image for %s" % tilename)

            # Add in the white background.
            pb = pb.composite_color_simple(
                tilesize, tilesize, GdkPixbuf.InterpType.BILINEAR, 255,
                tilesize, 0xffffff, 0xffffff)

            # Adding an alpha channel seems to help it work with some image
            # formats/colour depths.
            pb = pb.add_alpha(False, 0, 0, 0)

            # Cache if this is the useful size for us.
            if tilesize == KCanvas.tilesize:
                self.images[tilename] = pb
            return pb

    def settilesize(self, size):
        """Sets the size for tiles; causes the canvas to resize and be redrawn."""
        KCanvas.tilesize = size
        self.set_size_request(self.tilesize*xsize, self.tilesize*ysize)
        self.queue_draw_area(0, 0, self.tilesize*xsize, self.tilesize*ysize)

        # And must flush the tile cache; need to redraw from the image data at
        # the new tile size.
        self.images = {}

    def drawcell(self, cairo_ctx: cairo.Context, i, j):
        """Draw the cell at i, j, using the supplied graphics context."""
        tile = self.showboard[i + j * xsize]

        i = i * self.tilesize
        j = j * self.tilesize

        if (tile == "blank"):
            cairo_ctx.set_source_rgb(1, 1, 1)
            cairo_ctx.rectangle(i, j, self.tilesize, self.tilesize)
            cairo_ctx.fill()
        else:
            Gdk.cairo_set_source_pixbuf(cairo_ctx,
                                        self.get_image(tile), i, j)
            cairo_ctx.paint()

    def draw_event(self, widget, cairo_ctx) -> None:
        """draw handler; redraws the invalidated part of the display."""
        x, y = 0, 0
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        tilesize = self.tilesize
        try:
            for i in range(xsize):
                if (i+1)*tilesize <= x or i*tilesize > x+width:
                    continue
                for j in range(ysize):
                    if (j+1)*tilesize <= y or j*tilesize > y+height:
                        continue
                    self.drawcell(cairo_ctx, i, j)
        except KeyError as e:
            md = Gtk.MessageDialog(
                type=Gtk.MessageType.ERROR,
                message_format="Tileset is missing image for %s" % e,
                buttons=Gtk.ButtonsType.OK)
            md.run()
            md.destroy()
            Gtk.main_quit()

    def button_press_event(self, widget, event):
        """Handler for mouse button presses; just translates to game coords and passes on."""
        window, x, y, mods = event.window.get_pointer()
        x = x // KCanvas.tilesize
        y = y // KCanvas.tilesize
        self.bpress(event.button, x, y)

    def button_release_event(self, widget, event):
        """Handler for mouse button release; just translates to game coords and passes on."""
        window, x, y, mods = event.window.get_pointer()
        x = x // KCanvas.tilesize
        y = y // KCanvas.tilesize
        self.brelease(event.button, x, y)

    def mouse_motion_event(self, widget, event):
        """Handler for mouse movement; just translates to game coords and passes on."""
        window, x, y, mods = event.window.get_pointer()
        x = x // KCanvas.tilesize
        y = y // KCanvas.tilesize
        self.mouseto(x, y)
