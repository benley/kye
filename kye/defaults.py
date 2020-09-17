#    Kye - classic puzzle game
#    Copyright (C) 2006, 2007, 2010 Colin Phipps <cph@moria.org.uk>
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
"""kye.defaults - contains the KyeDefaults class."""

import os.path
from pathlib import Path
from typing import Dict, List

from xdg import BaseDirectory


class KyeDefaults:
    """Class for reading, querying and saving game preferences,
    including the list of recently-played files and known level names.
    """
    known_header = "[Known Levels]"
    settings_header = "[Settings]"

    def __init__(self) -> None:
        # Initialise.
        self.__count = 0
        self.__known: Dict[str, List[str]] = {}
        self.__orderfiles: Dict[str, int] = {}
        self.__path: Dict[str, Path] = {}
        self.settings: Dict[str, str] = {}

        # Path to the config file.
        cf = BaseDirectory.load_first_config("kye/kye.config")

        if cf is None:
            return

        # Try reading the config file.
        try:
            s = open(cf)
            while 1:
                # Read header lines until done.
                line = s.readline().strip()
                if line == "":
                    break
                elif line == KyeDefaults.known_header:
                    # Inside the [known levels] block; keep reading until we get to a blank line.
                    while 1:
                        line = s.readline().strip()
                        if line == "":
                            break

                        # Format here is filename<TAB>known_level<TAB>known_level<TAB>...
                        fields = line.split("\t")
                        path = fields.pop(0)
                        filename = os.path.basename(path)
                        self.__known[filename] = fields
                        self.__path[filename] = Path(path)

                        # Order in the config file is the recently-used order.
                        self.__orderfiles[filename] = self.__count
                        self.__count = self.__count + 1

                elif line == KyeDefaults.settings_header:
                    # Read into settings hash until we get to a blank line.
                    while 1:
                        line = s.readline().strip()
                        if line == "":
                            break
                        key, value = line.split("\t")
                        if key == "Size":
                            self.settings[key] = value

        except IOError:
            pass

    def get_known_levels(self, path: Path) -> List[str]:
        """Get all known level names for the given filename."""
        fname = os.path.basename(path)
        if fname in self.__known:
            return self.__known[fname]
        return []

    def add_known(self, path: Path, level_name: str) -> None:
        """For this kye file, we now know this level name."""
        # Index by just the filename
        fname = os.path.basename(path)
        self.__path[fname] = path

        # Remember that this is the most recently loaded level
        self.__orderfiles[fname] = self.__count
        self.__count = self.__count + 1

        # Add this level to the known list for this file (adding the file to
        # the dictionary if new)
        if fname not in self.__known:
            self.__known[fname] = []
        if level_name not in self.__known[fname]:
            self.__known[fname].append(level_name)

    def get_recent(self) -> List[Path]:
        """Returns paths to the five most recently loaded .kye files."""
        known_names = sorted(self.__known.keys(),
                             key=lambda x: self.__orderfiles[x])
        return [self.__path[name] for name in known_names[-5:]]

    def save(self) -> None:
        """Try to save the configuration back to the config file."""
        try:
            path = os.path.join(BaseDirectory.save_config_path("kye"),
                                "kye.config")
            with open(path, "w") as s:
                # Known levels etc
                s.write(KyeDefaults.known_header+"\n")
                known_names = sorted(self.__known.keys(),
                                     key=lambda x: self.__orderfiles[x])
                for name in known_names:
                    s.write("%s\t%s\n" % (self.__path[name],
                                          "\t".join(self.__known[name])))
                s.write("\n")

                # other settings
                s.write(KyeDefaults.settings_header+"\n")
                for setting, value in self.settings.items():
                    s.write("%s\t%s\n" % (setting, value))
                s.write("\n")

        except IOError as err:
            print("Failed to save settings: %s" % err)
            pass
