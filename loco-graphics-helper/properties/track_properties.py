'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os
from ..builders.task_builder import TaskBuilder

from ..operators.render_operator import RCTRender

def object_type_update_func(self, context):
    object = context.object
    props = object.loco_graphics_helper_track_properties
    type = props.track_type
    if type == "TRACK":
        props.layers_flat = 3
        props.layers_slope = 1
    if type == "ROAD":
        props.layers_flat = 1
        props.layers_slope = 1
    if type == "TRAM":
        props.layers_flat = 3
        props.layers_slope = 3
    

class TrackProperties(bpy.types.PropertyGroup):
    track_type = bpy.props.EnumProperty(
        name="track_type",
        items=(
            ("TRACK", "Railway", "", 0),
            ("ROAD", "Road", "", 1),
            ("TRAM", "Tramway", "", 2),
        ),
        default="TRACK",
        update=object_type_update_func
    )
    layers_flat = bpy.props.IntProperty(
        name="layers_flat",
        default = 3)
    layers_slope = bpy.props.IntProperty(
        name="layers_slope",
        default = 3)
    one_way = bpy.props.BoolProperty(
        name="one_way",
        description="Models for both directions required",
        default = False)

    # for determining how many layers each track piece has
    def get_num_layers(self, track_type):
        if track_type == "FLAT":
            return self.layers_flat
        if track_type == "SLOPE":
            return self.layers_slope
        return 1

    # for determining which track pieces to render
    def get_object_type(self):
        if track_type == "TRAM":
            return "ROAD"
        return track_type


def register_track_properties():
    bpy.types.Scene.loco_graphics_helper_track_properties = bpy.props.PointerProperty(
        type=TrackProperties)


def unregister_track_properties():
    del bpy.types.Scene.loco_graphics_helper_track_properties
