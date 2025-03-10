'''
Copyright (c) 2025 Loco Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/OpenLoco/Blender-Loco-Graphics

Loco Graphics Helper is licensed under the GNU General Public License version 3.
'''

from enum import Enum

track_angle_sections_names = [
    "VEHICLE_SPRITE_FLAG_FLAT",
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES",
    "VEHICLE_SPRITE_FLAG_STEEP_SLOPES",
]

# is_transition, number_rotation_frames, angle
track_angle_sections = {
    "VEHICLE_SPRITE_FLAG_FLAT": [
        [False, 32, 0]
    ],
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES": [
        [True, 4, 11.1026 / 2],
        [True, 4, -11.1026 / 2],
        [False, 4, 22.2052 / 2],
        [False, 4, -22.2052 / 2]
    ],
    "VEHICLE_SPRITE_FLAG_STEEP_SLOPES": [
        [True, 4, 11.1026 + 11.1026 / 2],
        [True, 4, -11.1026 - 11.1026 / 2],
        [False, 4, 22.2052],
        [False, 4, -22.2052]
    ],
}

# note to self: images are ordered by sequence FIRST then angle SECOND
"""
layer_names = [
    ["Model"],
    ["Pickup Icon", "Placement Icon"],
    ["Ballast", "Ties", "Rails"]
]

layer_descriptions = [
    ["Icon Model"],
    ["Icon, drawn as train pickup button", "Icon, drawn as train placement button"],
    ["Ballast, drawn above terrain or bridge. Sloped tracks use only this layer, sloped tram track still use all three.", "Ties, drawn above ballast", "Rails, drawn above ties"],
]
"""

# these are not the OpenLoco track piece IDs. These are the index of the piece in the manifest
class TrackPieceType(Enum):
    PREVIEW = 0
    PICKUP = 1
    PLACE = 2
    STRAIGHT = 3
    CURVE_SMALL = 7
    SMALL_CURVE_SLOPE_SHALLOW = 8
    SMALL_CURVE_SLOPE_STEEP = 9
    CURVE = 10
    SLOPE_SHALLOW = 11
    SLOPE_STEEP = 12
    CURVE_DIAG = 13
    DIAG_STRAIGHT = 14
    S_BEND = 15
    VERY_SMALL_CURVE = 16

class RoadPieceType(Enum):
    PREVIEW = 0
    PICKUP = 1
    PLACE = 2
    STRAIGHT = 3
    VERY_SMALL_CURVE = 4
    T_INTERSECTION = 5
    FOUR_WAY_INTERSECTION = 6
    SMALL_CURVE = 7
    SLOPE_SHALLOW = 11
    SLOPE_STEEP = 12


default_manifest = {
    "name": "null track type",
    "angles": 4,
    "symmetric": False,
    "render_mirror": False,
    "grid_size": [1,1],
    "subposition_order": [0],
    "track_type": "NULL",
    "canvas_size": None,
    "track": False,
    "road": False
}

class TrackPieceManifest:
    name= "null track type"
    angles= 4
    symmetric= False
    render_mirror= False
    grid_size= [1,1]
    subposition_order= [0]
    track_type= "NULL"
    canvas_size= None
    track= False
    road= False
    
    def __init__(self, input):
        for key in default_manifest.keys():
            if key in input:
                setattr(self, key, input[key])
        if self.canvas_size == None:
            self.canvas_size = [max(self.grid_size[0],self.grid_size[1])*64 for _ in range(2)]

track_piece_mappings = [
    { # Tab icon when building track type
        "name": "Spinning Preview",
        "angles": 32,
        "symmetric": True,
        "grid_size": [1,1],
        "subposition_order": [0],
        "track_type": "UI",
        "canvas_size": [29,22],
        "track": True,
        "road": True
    },
    { # vehicle UI icons for picking up and placing vehicle
        "name": "Pickup icon",
        "angles": 1,
        "grid_size": [1,1],
        "subposition_order": [0],
        "track_type": "UI",
        "canvas_size": [20,20],
        "track": True,
        "road": True
    },
    { # vehicle UI icons for picking up and placing vehicle
        "name": "Placement icon",
        "angles": 1,
        "grid_size": [1,1],
        "subposition_order": [0],
        "track_type": "UI",
        "canvas_size": [20,20],
        "track": True,
        "road": True
    },
    {
        "name": "Straight",
        "track_type": "FLAT",
        "symmetric": True,
        "track": True,
        "road": True
    },
    { # Roads put this here in the order
        "name": "Very Small Curve",
        "track_type": "FLAT",
        "grid_size": [1,1],
        "subposition_order": [0],
        "road": True
    },
    {
        "name": "T-Intersection",
        "track_type": "FLAT",
        "grid_size": [1,1],
        "subposition_order": [0],
        "road": True
    },
    {
        "name": "4-Way Intersection",
        "track_type": "FLAT",
        "angles": 1,
        "grid_size": [1,1],
        "subposition_order": [0],
        "road": True
    },
    {
        "name": "Small Curve",
        "track_type": "FLAT",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "track": True,
        "road": True
    },
    {
        "name": "Small Curve Gentle Slope",
        "track_type": "SLOPE",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "track": True
    },
    {
        "name": "Small Curve Steep Slope",
        "track_type": "SLOPE",
        "grid_size": [2,2],
        "subposition_order": [2,3,0,1],
        "track": True
    },
    {
        "name": "Medium Curve",
        "track_type": "FLAT",
        "grid_size": [3,3],
        "subposition_order": [6,3,4,1,2],
        "track": True
    },
    {
        "name": "Gentle Slope",
        "track_type": "SLOPE",
        "grid_size": [1,2],
        "subposition_order": [1,0],
        "track": True,
        "road": True
    },
    {
        "name": "Steep Slope",
        "track_type": "SLOPE",
        "track": True,
        "road": True
    },
    {
        "name": "Diagonal Curve",
        "track_type": "FLAT",
        "render_mirror": True,
        "grid_size": [2,3],
        "subposition_order": [4,2,3,0,1],
        "track": True
    },
    {
        "name": "Diagonal Straight",
        "track_type": "FLAT",
        "grid_size": [2,2],
        "subposition_order": [2,0,3,1],
        "track": True
    },
    {
        "name": "S-Bend",
        "track_type": "FLAT",
        "symmetric": True,
        "grid_size": [2,3],
        "subposition_order": [],
        "render_mirror": True,
        "track": True
    },
    { # Railways put it here in the order
        "name": "Very Small Curve",
        "track_type": "FLAT",
        "track": True
    }
]

for i in range(len(track_piece_mappings)):
    track_piece_mappings[i] = TrackPieceManifest(track_piece_mappings[i])