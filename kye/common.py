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

"""kye.common - Common utility functions and classes.
Exposed constants:

XSIZE, YSIZE - size of the game playing area.

VERSION - version number of this release of the game.

KYEPATHS - the list of paths that we will try for opening levels given on the
           command line, and for searching for tilesets."""

import os.path
from pathlib import Path
import tarfile
from typing import Dict, IO, Sequence, Union

XSIZE = 30
YSIZE = 20

VERSION = "2.0"

KYEPATHS = [Path(x) for x in ["levels",
                              "/usr/local/share/kye",
                              "/usr/share/kye"]]


def tryopen(filename: Path, paths: Sequence[Path]) -> IO:
    """Returns a reading file handle for filename, searching through directories in the supplied paths."""
    try:
        f = open(filename)
        return f
    except IOError:
        for path in paths:
            try:
                return open(os.path.join(path, filename))
            except IOError:
                pass
    raise IOError("Unable to find file %s" % filename)


def findfile(filename: Union[Path, str]) -> Path:
    """Looks for filename, searching a built-in list of directories.
    Returns the path where it finds the file.
    """
    if os.path.exists(filename):
        return Path(filename)
    for path in KYEPATHS:
        x = os.path.join(path, filename)
        if os.path.exists(x):
            return Path(x)
    raise FileNotFoundError


class KyeImageDir:
    """Class for retrieving images from a tileset tar.gz."""

    def __init__(self, filename: Path) -> None:
        self.tiles: Dict[str, bytes] = {}
        with tarfile.open(filename, 'r|gz') as tar:
            for tarinfo in tar:
                (tilename, ext) = tarinfo.name.split('.', 2)
                fh = tar.extractfile(tarinfo)
                assert fh is not None  # for mypy
                self.tiles[tilename] = fh.read()

    def get_tile(self, tilename: str) -> bytes:
        """Returns the image file data for the requested tile."""
        return self.tiles[tilename]
