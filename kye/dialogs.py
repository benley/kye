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

"""kye.dialogs - classes for dialog boxes used by the interface."""

import os.path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from kye.common import kyepaths, version


class GotoDialog(Gtk.Dialog):
    """A dialog box for the player to select or type a level name to go to."""

    def __init__(self, parent=None, knownlevs=()):
        Gtk.Dialog.__init__(self, title="Go to level",
                            parent=parent,
                            flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK,
                                     Gtk.ResponseType.ACCEPT,
                                     Gtk.STOCK_CANCEL,
                                     Gtk.ResponseType.REJECT))
        self.set_default_response(Gtk.ResponseType.ACCEPT)

        # Add prompt.
        self.label = llabel("Select, or type, the name of the level to go to.")
        self.label.show()
        self.vbox.pack_start(self.label, True, True, 0)

        # Add combobox to select known level or enter level name.
        self.cb = Gtk.ComboBoxText.new_with_entry()
        for level in knownlevs:
            self.cb.append_text(level)
        # Make it so hitting Enter activates the ACCEPT action
        self.cb.get_child().set_activates_default(True)
        self.vbox.pack_start(self.cb, True, True, 0)

        self.cb.show()

    def get_level(self):
        """Returns the selected level name."""
        return self.cb.get_active_text()


def llabel(txt):
    """Return a centered, line-wrapped label."""
    label = Gtk.Label(txt)
    label.set_alignment(0, 0.5)
    label.set_line_wrap(True)
    return label


class KyeHelpDialog(Gtk.Dialog):
    """Help dialog box."""

    def __init__(self, parent=None, after=None, message=None, getimage=None):
        Gtk.Dialog.__init__(self, title="Help", parent=parent,
                            flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
        self.getimage = getimage

        self.set_default_size(800, 600)
        self.add_button(Gtk.STOCK_OK, 0)
        self.connect("response", self.response)

        self.grid = Gtk.Grid()

        box = self.get_content_area()
        box.add(self.grid)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        self.grid.attach(scrolledwindow, 0, 1, 3, 1)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)

        self.textbuffer = self.textview.get_buffer()

        self.insert_image("kye")
        self.insert_markup(
            "You are Kye. Move by point-and-click with the mouse, or the arrow"
            " keys or numeric keypad on the keyboard (note that you can move"
            " diagonally, even using the keyboard).\n")

        self.insert_image("diamond_1")
        self.insert_markup(
            "The object of the game is to collect all the diamonds.\n")

        self.insert_image("wall5")
        self.insert_markup(
            "These are solid walls.\n")

        self.insert_image("block")
        self.insert_markup(
            "These are blocks, which you can push.\n")

        self.insert_image("slider_right")
        self.insert_markup(
            "Sliders move in the direction of the arrow until"
            " they hit an obstacle.\n")

        self.insert_image("rocky_right")
        self.insert_markup(
            "Rockies move like sliders, but they roll around round objects,"
            " like rounded walls and other rockies.\n")

        self.insert_image("blocke")
        self.insert_markup(
            "Soft blocks you can destroy by moving into them.\n")

        for img in ["blob_1", "gnasher_1", "spike_1", "twister_1", "snake_1"]:
            self.insert_image(img)
        self.insert_markup(
            "Monsters kill you if they touch you. You do have 3 lives,"
            " though.\n")

        self.insert_image("sentry_right")
        self.insert_markup(
            "Sentries pace back and forward, and push other objects.\n")

        self.insert_image("black_hole_1")
        self.insert_markup(
            "Objects entering a black hole are destroyed.\n")

        self.insert_image("slider_shooter_right")
        self.insert_markup(
            "Shooters create new sliders or rockies.\n")

        self.insert_image("block_timer_5")
        self.insert_markup(
            "Timer blocks disappear when their time runs out.\n")

        self.insert_image("turner_clockwise")
        self.insert_markup(
            "Turning blocks change the direction of sliders and rockies.\n")

        self.insert_image("sticky_horizontal")
        self.insert_markup(
            "Magnets (also called sticky blocks) allow you to pull objects.\n")

        self.insert_image("oneway_right_1")
        self.insert_markup(
            "One-way doors only allow Kye though, and only in"
            " one direction.\n")

        self.insert_markup(
            "\nIf you make a mistake, or get stuck in a level, go to the Level"
            " menu and select Restart Level. To skip to a particular level (if"
            " you've played a set of levels before and already know the level"
            " name you want to get to), go to the Level menu and select Goto"
            " Level. You can load a new set of levels by specifying the .kye"
            " file on the command line, or by opening it via the File menu.\n")

        scrolledwindow.add(self.textview)

        self.show_all()

    def response(self, a, rid):
        self.destroy()

    def insert_markup(self, markup: str):
        return self.textbuffer.insert_markup(self.textbuffer.get_end_iter(),
                                             markup, -1)

    def insert_image(self, img: str):
        return self.textbuffer.insert_pixbuf(self.textbuffer.get_end_iter(),
                                             self.getimage(img))


def kyeffilter():
    """Constructs a Gtk.FileFilter for .kye files"""
    kfilter = Gtk.FileFilter()
    kfilter.set_name("Kye Levels")
    kfilter.add_pattern("*.kye")
    return kfilter


def kyerfilter():
    """Constructs a Gtk.FileFilter for .kyr files"""
    kfilter = Gtk.FileFilter()
    kfilter.set_name("Kye Recordings")
    kfilter.add_pattern("*.kyr")
    return kfilter


def getopendialog():
    """Build a Gtk.FileChooserDialog suitable for Kye levels"""
    filesel = Gtk.FileChooserDialog("Open Kye Levels",
                                    buttons=(Gtk.STOCK_OK,
                                             Gtk.ResponseType.OK,
                                             Gtk.STOCK_CANCEL,
                                             Gtk.ResponseType.REJECT))
    filesel.add_filter(kyeffilter())
    for path in kyepaths:
        if path[0] == "/" and os.path.exists(path):
            filesel.add_shortcut_folder(path)
    return filesel


def KyeAboutDialog(kimg):
    """Returns a Gtk.AboutDialog with all the names/details/versions for Kye entered.

    Used to be a subclass of AboutDialog, hence the name.
    """
    try:
        d = Gtk.AboutDialog()
        d.set_name("Kye")
        d.set_version(version)
        d.set_website("http://games.moria.org.uk/kye/pygtk")
        d.set_authors(("Colin Phipps <cph@moria.org.uk>",))
        d.set_copyright("Copyright (C) 2004-2007, 2010 Colin Phipps <cph@moria.org.uk>")
        d.set_comments("Based on the original Kye for Windows, by Colin Garbutt")
        d.set_license("Distributed under the GNU General Public License")
        d.set_logo(kimg)
        return d
    except AttributeError:
        # Old pygtk versions do not have an AboutDialog, so fall back on a MessageDialog.
        d = Gtk.MessageDialog(
            type=Gtk.MESSAGE_INFO,
            message_format="Kye %s - by Colin Phipps <cph@moria.org.uk>" % version,
            buttons=Gtk.BUTTONS_OK)
        return d
