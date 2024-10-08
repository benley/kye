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

"""Input handling code - mouse input and recorded input."""

import gi
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk
from gi.repository.Gdk import keyval_from_name

import pickle
from gzip import GzipFile
import os.path
from pathlib import Path
from random import Random
from typing import Any, List, Optional, Tuple, Union

from kye.common import VERSION


Move = Tuple[str, int, int]


class KMoveInput:
    """Gets movement input, and converts it into game actions."""

    def __init__(self) -> None:
        self.__recordto: Optional[GzipFile] = None
        self.clear()

    def clear(self) -> None:
        """Clears the current state of mouse buttons/keyboard keys held."""
        self.heldkeys: List[Move] = []
        self.keyqueue: List[Move] = []
        self.mousemoving = False
        self.currentmouse: Optional[Tuple[str, int, int]] = None

    keymap = {
        keyval_from_name('Left'): ("rel", -1, 0),
        keyval_from_name('Right'): ("rel", 1, 0),
        keyval_from_name('Up'): ("rel", 0, -1),
        keyval_from_name('Down'): ("rel", 0, 1),
        keyval_from_name('KP_4'): ("rel", -1, 0),
        keyval_from_name('KP_6'): ("rel", 1, 0),
        keyval_from_name('KP_2'): ("rel", 0, 1),
        keyval_from_name('KP_8'): ("rel", 0, -1),
        keyval_from_name('KP_1'): ("rel", -1, 1),
        keyval_from_name('KP_3'): ("rel", 1, 1),
        keyval_from_name('KP_7'): ("rel", -1, -1),
        keyval_from_name('KP_9'): ("rel", 1, -1),
        keyval_from_name('KP_Left'): ("rel", -1, 0),
        keyval_from_name('KP_Right'): ("rel", 1, 0),
        keyval_from_name('KP_Down'): ("rel", 0, 1),
        keyval_from_name('KP_Up'): ("rel", 0, -1),
        keyval_from_name('KP_End'): ("rel", -1, 1),
        keyval_from_name('KP_Page_Down'): ("rel", 1, 1),
        keyval_from_name('KP_Home'): ("rel", -1, -1),
        keyval_from_name('KP_Page_Up'): ("rel", 1, -1),
    }

    def key_press_event(self, widget, event) -> None:
        """Handle a keypress event."""
        try:
            pressedkey = KMoveInput.keymap[event.keyval]
            # If this key is not already pressed, then it's a new press and so
            # we want to move at least one square and remember that it is held
            # down.
            if pressedkey not in self.heldkeys:
                self.keyqueue.append(pressedkey)

                # There is no way at this point to know if this is a key press
                # or a key hold. So we'll have a 'delay' which causes us to
                # wait a few ticks before considering the key held and reacting
                # to it again.  But have SHIFT as a way for the user to tell us
                # that it's a hold.
                if event.state & Gdk.ModifierType.SHIFT_MASK == 0:
                    self.__delay = 1  # wait 1 tic
                self.heldkeys.append(pressedkey)
        except KeyError:
            return

    def key_release_event(self, widget, event) -> None:
        """Handle a key release event."""
        try:
            self.heldkeys.remove(KMoveInput.keymap[event.keyval])
        except KeyError:
            return
        except ValueError:
            return

    def mouse_motion_event(self, x: int, y: int) -> None:
        """Update mouse position after a mouse move."""
        self.currentmouse = ("abs", x, y)

    def button_press_event(self, button: int, x: int, y: int) -> None:
        """Mouse button press event."""
        if button == 1:
            self.mousemoving = True

    def button_release_event(self, button: int, x: int, y: int) -> None:
        """Mouse button release event."""
        if button == 1:
            self.mousemoving = False

    def __get_move(self) -> Optional[Move]:
        """Gets the move from the current keys/mouse state."""
        # If there are key presses in the queue, use them first
        if len(self.keyqueue) > 0:
            k = self.keyqueue[0]
            self.keyqueue = self.keyqueue[1:]
            return k

        # Then, if the mouse is pressed, do it
        if self.mousemoving and self.currentmouse:
            return self.currentmouse

        # Finally, if any keys are held, use the most recently pressed
        if len(self.heldkeys) > 0:
            if self.__delay <= 0:
                return self.heldkeys[-1]
            self.__delay = self.__delay - 1

        # No action
        return None

    def end_record(self) -> None:
        """End any previous recording."""
        if self.__recordto is not None:
            try:
                self.__recordto.close()
            except IOError:
                print("error closing recording")

        self.__recordto = None

    def record_to(self, recfile: Path,
                  playfile: Path,
                  playlevel: str,
                  rng: Random) -> None:
        """Set this input to be recorded to the supplied stream."""
        # Open the stream
        stream = GzipFile(recfile, "w")
        self.__recordto = stream

        # Write header
        stream.write(bytes("Kye %s recording:\n" % VERSION, "UTF-8"))
        stream.write(bytes(os.path.basename(playfile) + "\n", "UTF-8"))
        stream.write(bytes(playlevel + "\n", "UTF-8"))
        pickle.dump(rng.getstate(), stream)

    def is_recording(self) -> bool:
        """Return true iff we are recording at the moment."""
        return self.__recordto is not None

    def get_move(self) -> Optional[Move]:
        """Gets the move from the current keys/mouse state (and records the move if required)."""
        m = self.__get_move()
        if self.__recordto is not None:
            if m is not None:
                self.__recordto.write(bytes("\t".join(map(str, m)), "UTF-8"))
            self.__recordto.write(b"\n")
        return m


class KDemoError(Exception):
    pass


class KDemoFormatError(KDemoError):
    pass


class KDemoFileMismatch(KDemoError):
    def __init__(self, filename: Union[Path, str]) -> None:
        KDemoError.__init__(self)
        self.filename = filename


class KyeRecordedInput:
    """An input source which is a recording in a file of a previous game."""

    def __init__(self, playfile: Path, playback: Path) -> None:
        instream = GzipFile(playback)
        header = instream.readline().rstrip().decode()
        if not (header.startswith("Kye ") and header.endswith(" recording:")):
            raise KDemoFormatError()

        # Check filename in the demo is what we have loaded.
        fn = instream.readline().rstrip().decode()
        if fn != os.path.basename(playfile):
            raise KDemoFileMismatch(fn)

        # Okay
        self.__level = instream.readline().rstrip().decode()
        self.__rng: Tuple[Any, ...] = pickle.load(instream)
        self.__s: GzipFile = instream

    def get_level(self) -> str:
        """Return the level name for this recording."""
        return self.__level

    def set_rng(self, rng: Random) -> None:
        """Set the supplied RNG to the state needed for this recording."""
        rng.setstate(self.__rng)

    def get_move(self) -> Optional[Move]:
        """Get a move from the recording."""
        line = self.__s.readline().rstrip().decode()
        if len(line) == 0:
            return None
        s = line.split("\t")
        return (s[0], int(s[1]), int(s[2]))
