'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import subprocess
import os
import bpy
import math

from .models.palette import Palette, palette_base_path, palette_groups_path

default_full_palette = Palette(os.path.join(
    palette_base_path, "default_full_palette.bmp"), [
    "black",
    "gray",
    "lavender_purple",
    "violet_purple",
    "blue",
    "teal",
    "yellow_green",
    "sea_green",
    "light_olive_green",
    "dark_olive_green",
    "lime_green",
    "yellow",
    "bright_yellow",
    "orange",
    "salmon",
    "sandy_brown",
    "tan_brown",
    "bordeaux_red",
    "bright_red",
    "magenta",
    "transparent"
])

default_vehicle_palette = Palette(os.path.join(
    palette_base_path, "default_vehicle_palette.bmp"), [
    "black",
    "gray",
    "transparent"
])

rider_palette = Palette(os.path.join(palette_base_path, "peep_palette.bmp"), [
    "black",
    "salmon",
    "transparent"
])

recolor_1_orct2_palette = Palette(os.path.join(
    palette_base_path, "recolor_1_orct2_palette.bmp"), [
    "recolor_1_orct2",
    "transparent"
])

recolor_2_palette = Palette(os.path.join(
    palette_base_path, "recolor_2_palette.bmp"), [
    "magenta",
    "transparent"
])

recolor_3_palette = Palette(os.path.join(
    palette_base_path, "recolor_3_palette.bmp"), [
    "yellow",
    "transparent"
])

custom_palette = Palette(os.path.join(
    palette_base_path, "custom_palette.bmp"), [
    "yellow",
])

# The palette manager takes care of the different palette modes and build a modified palette based on the selected parameters.


class PaletteManager:
    def __init__(self):
        self.recolor_palettes = []

        self.orct2_recolor_palettes = [
            recolor_1_orct2_palette,
            recolor_2_palette,
            recolor_3_palette
        ]

    def set_recolor_palettes(self, recolor1, recolor2, recolor3):
        self.recolor_palettes = [
            Palette(
                os.path.join(palette_groups_path, recolor1 + ".png"),
                [ recolor1 ]
            ),
            Palette(
                os.path.join(palette_groups_path, recolor2 + ".png"),
                [ recolor2 ]
            ),
            Palette(
                os.path.join(palette_groups_path, recolor3 + ".png"),
                [ recolor3 ]
            ),
        ]

    def get_recolor_shades(self, renderer):
        for palette in self.recolor_palettes:
            palette.get_shades(renderer)
        for palette in self.orct2_recolor_palettes:
            palette.get_shades(renderer)

    # Gets a base palette for the selected palette mode for the selected number of recolorables
    def get_base_palette(self, selected_palette_mode, recolors, preference="FULL"):
        if selected_palette_mode == "AUTO":
            selected_palette_mode = preference

        base_palette = None

        if selected_palette_mode == "FULL":
            base_palette = default_full_palette.copy()
            base_palette.invalidated = True
        elif selected_palette_mode == "VEHICLE":
            base_palette = default_vehicle_palette.copy()
        elif selected_palette_mode == "CUSTOM":
            base_palette = custom_palette.copy()
            base_palette.invalidated = True
        else:
            raise Exception(
                "Failed to get base palette. Unknown palette mode " + selected_palette_mode + ".")

        for i in range(recolors):
            base_palette.exclude_color(self.recolor_palettes[i].colors[0])

        return base_palette

    # Gets the recolor palette for the specified recolor index
    def get_recolor_palette(self, recolor_index):
        return self.recolor_palettes[recolor_index]

    # Gets the recolor palette for the specified recolor index that is used by ORCT2
    def get_orct2_recolor_palette(self, recolor_index):
        return self.orct2_recolor_palettes[recolor_index]

    # Gets the rider palette
    def get_rider_palette(self):
        return rider_palette

    # Overwrites the colors of the custom palette
    def set_custom_palette(self, colors):
        custom_palette.clear()
        custom_palette.add_colors(colors)
