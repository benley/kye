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

"""kye.app - the Kye game application. Just contains the KyeApp class.
"""

from pathlib import Path
from random import Random
from typing import Literal, List, Optional

from gi.repository import GObject

from kye.common import tryopen, KYEPATHS
from kye.defaults import KyeDefaults
from kye.frame import KFrame
from kye.game import KGame, KGameFormatError
from kye.input import KyeRecordedInput, KDemoFormatError, KDemoFileMismatch


class KyeApp:
    """This class is a wrapper around the game class, which handles various
    extra-game actions, such as selecting whether the game is taking input from
    the user or a recording, loading new levels and changeover between levels.
    """

    def __init__(self,
                 defaults: KyeDefaults,
                 playfile: Path = Path("intro.kye"),
                 playlevel: str = "") -> None:
        self.__playfile = playfile
        self.__playlevel = playlevel
        self.__gamestate = "starting level"

        self.__recto: Optional[Path] = None
        self.__playback: Optional[Path] = None
        self.__game: Optional[KGame] = None
        self.__frame: Optional[KFrame] = None
        self.__defaults = defaults

    def run(self, frame: KFrame) -> None:
        """Run the application. You must supply a 'KFrame' for the UI."""
        self.__frame = frame

        # Run first tick - loads the level - immediately
        self.do_tick()
        GObject.timeout_add(100, self.do_tick)

        self.__frame.main()

        # End any recording going on at the time of exit.
        self.__frame.moveinput.end_record()

    def do_tick(self) -> Literal[True]:
        """Performs all actions required for one clock tick in the game"""

        # First, we handle any extra-game actions like switching levels.

        # If starting a new level...
        if self.__gamestate == "starting level":
            self.__start_new_level()

        # If we are in a level...
        if self.__gamestate == "playing level":
            assert self.__game is not None   # for mypy
            assert self.__frame is not None  # for mypy
            # Check if the level has been completed.
            if self.__game.diamonds == 0:
                self.__gamestate = "between levels"
                msg = self.__game.exitmsg
                if self.__frame.moveinput.is_recording():
                    msg = "Recording complete."
                if self.__frame.moveinput != self.__game.ms:
                    msg = "Playback complete."
                self.__frame.endleveldialog(self.__game.nextlevel, msg)

            # If we are still playing, run a gametick and update the screen.
            if self.__gamestate == "playing level":
                self.__game.dotick()
                self.__frame.canvas.game_redraw(self.__game,
                                                self.__game.invalidate)
                self.__frame.stbar.update(diamonds=self.__game.diamonds)
                if self.__game.thekye is not None:
                    self.__frame.stbar.update(kyes=self.__game.thekye.lives)

        # And tell glib knows that we want this timer event to keep occurring.
        return True

    def __start_new_level(self) -> None:
        """Performs actions needed when beginning a new level."""
        # Clean up any previous recording/playback title & close existing record
        assert self.__frame is not None  # for mypy

        self.__frame.moveinput.end_record()
        self.__frame.extra_title(None)

        # If recording this game, open the file to record to & tell the input system about it
        rng = Random()
        try:
            if self.__recto:
                self.__frame.moveinput.record_to(self.__recto,
                                                 playfile=self.__playfile,
                                                 playlevel=self.__playlevel,
                                                 rng=rng)
        except IOError:
            self.__frame.error_message(
                message="Failed to write to %s " % self.__recto)

        self.__recto = None
        if self.__frame.moveinput.is_recording():
            self.__frame.extra_title("Recording")

        # If playing a demo, open it & read the header
        self.__frame.moveinput.clear()
        move_source = self.__frame.moveinput
        if self.__playback is not None:
            try:
                move_source = KyeRecordedInput(self.__playfile,
                                               self.__playback)
                self.__playlevel = move_source.get_level()
                move_source.set_rng(rng)
                self.__frame.extra_title("Replay")
            except KDemoFileMismatch as e:
                self.__frame.error_message(message="Recording is for %s; you must load this level set first" % e.filename)
            except KDemoFormatError:
                self.__frame.error_message(message="This file is not a Kye recording")
            except IOError:
                self.__frame.error_message(message="Failed to read %s" % self.__playback)
            self.__playback = None

        # Now try loading the actual level
        try:
            gamefile = tryopen(self.__playfile, KYEPATHS)

            # Create the game state object.
            self.__game = KGame(gamefile, want_level=self.__playlevel,
                                movesource=move_source, rng=rng)

            # And remember that we have reached this level.
            self.__defaults.add_known(self.__playfile, self.__game.thislev)

            # UI updates - level name in window title, hint in the status bar.
            self.__frame.level_title(self.__game.thislev)
            self.__frame.stbar.update(hint=self.__game.hint,
                                      levelnum=self.__game.levelnum)
        except KeyError:
            self.__frame.error_message(
                message="Level %s not known" % self.__playlevel)
        except KGameFormatError:
            self.__frame.error_message(
                message="%s is not a valid Kye level file." % self.__playfile)
        except IOError:
            self.__frame.error_message(
                message="Failed to read %s" % self.__playfile)
        if self.__game is not None:
            self.__gamestate = "playing level"
        else:
            self.__gamestate = ""

    def restart(self,
                recordto: Optional[Path] = None,
                demo: Optional[Path] = None) -> None:
        """Restarts the current level, with optional recording or playback
        (specified by recordto or demo parameters respectively).
        """
        self.__gamestate = "starting level"
        self.__recto = recordto
        self.__playback = demo
        assert self.__game is not None  # for mypy
        self.__playlevel = self.__game.thislev

    def goto(self, lname: str) -> None:
        """Jump to the named level."""
        self.__gamestate = "starting level"
        self.__playlevel = lname.upper()

    def open(self, fname: Path) -> None:
        """Open a new set of levels from the supplied filename."""
        self.__playfile = fname
        self.__playlevel = ""
        self.__gamestate = "starting level"

    def known_levels(self) -> List[str]:
        """Returns a list of levels that the player knows about from this level set."""
        return self.__defaults.get_known_levels(self.__playfile)
