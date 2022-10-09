#!python
# OTOS - Open Tec Operating System
# Copyright (c) 2022 Sebastian Oberschwendtner, sebastian.oberschwendtner@gmail.com
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
### Details
- *File:*     FontGenerator/__init__.py
- *Details:*  Python 3.9
- *Date:*     2022-10-08
- *Version:*  v1.0.0

## Description
This utility module can be used to generate font files for the *OTOS*
Graphics library.

### Author
Sebastian Oberschwendtner, :email: sebastian.oberschwendtner@gmail.com
"""
# === Modules ===
import pathlib, math
from . import BitConverter, Exporter

# === Package Information ===
__author__ = "Sebastian Oberschwendtner"
__version__ = "1.0.0"
__all__ = ["BitConverter", "Exporter"]

# === Functions ===

# === Classes ===
class FontData:
    """Data type to store font data."""

    def __init__(self):
        """Constructor of the font data type."""
        self.name = ""
        self.size = 0
        self.width = 0
        self.stride = 0
        self.data = [
            [],
        ] * 256


class Font:
    """Class to generate font files."""

    def __init__(self, font_file: pathlib.Path, font_size: int):
        """Constructor of the font class."""
        self.data: FontData = FontData()
        self.converter: BitConverter.FontConverter = BitConverter.FontConverter(
            str(font_file), font_size
        )

    def convert(self):
        """Convert the font file to a font file."""
        # Assign meta data
        self.data.name = self.converter.fontname
        self.data.size = self.converter.height_px
        self.data.width = self.converter.width_px
        self.data.stride = int(math.ceil(self.converter.height_px / 8))

        # Convert the characters
        for i in range(256):
            self.data.data[i] = self.converter.convert_character(i)


class Fonts:
    """Class to generate multiple font files."""

    def __init__(self, font_file: pathlib.Path, font_sizes: list):
        """Constructor of the fonts class."""
        self.fonts = []
        for iSize in font_sizes:
            self.fonts.append(Font(font_file, iSize))

    def convert(self):
        """Convert all fonts."""
        for font in self.fonts:
            font.convert()

    def export(self, export_path: pathlib.Path):
        """Export the font file."""
        # Create file
        _name = self.fonts[0].data.name
        file = export_path / f"{_name}.h"

        # Write Copyright
        Exporter.write_copyright_header(file)

        # Write autogenerated warning
        with open(file, "a") as f:
            f.write(
                f"\n/**\n * @attention\n * This file is autogenerated by {__name__} - {__version__}.\n * You should probably not edit this file manually.\n */\n"
            )

        # Write lookup preamble
        Exporter.write_lookup_table_preamble(file, _name)

        for iFont in self.fonts:
            # Write lookup table begin
            Exporter.write_lookup_table_begin(
                file, _name, (iFont.data.width, iFont.data.size)
            )

            # Write lookup table
            with open(file, "a") as f:
                for iChar in range(256):
                    line = Exporter.get_array_line(iChar, iFont.data.data[iChar])
                    f.write(8 * " " + line)

            # Write lookup table end
            Exporter.write_lookup_table_end(
                file, _name, (iFont.data.width, iFont.data.size), iFont.data.stride
            )

        # Finalize file
        Exporter.finalize_file(file, _name)
