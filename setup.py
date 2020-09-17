#!/usr/bin/env python

from setuptools import setup
from glob import glob

share = glob("levels/*.kye")
share.append("images.tar.gz")

setup(
    name="kye",
    version="1.0",
    description="Clone of Kye puzzle game",
    url="http://games.moria.org.uk/kye/pygtk",
    author="Colin Phipps",
    author_email="cph@moria.org.uk",
    scripts=["Kye", "Kye-edit"],
    packages=["kye"],
    data_files=[
        ("share/kye", share),
    ],
    install_requires=[
        "pygobject>=3",
        "pyxdg",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "User Interface :: Graphical :: Gnome"
    ],
    )
