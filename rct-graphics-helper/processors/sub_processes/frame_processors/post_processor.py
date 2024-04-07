'''
Copyright (c) 2022 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import os
import subprocess
from unicodedata import ucnhash_CAPI

from ....magick_command import MagickCommand
from ..sub_processor import SubProcessor


class Output:
    def __init__(self):
        self.path = ""
        self.index = 0
        self.offset_x = 0
        self.offset_y = 0

# Frame processor for masking, dithering and cropping the final image


class PostProcessor(SubProcessor):
    def __init__(self, renderer):
        super().__init__()

        self.renderer = renderer

    def process(self, frame, callback=None):
        main_render_path = frame.get_base_render_output_path()

        mask_path = frame.get_meta_render_output_path()

        magick_command = MagickCommand(mask_path)
        magick_command.write_to_cache("meta", True, main_render_path)
        magick_command.write_to_cache("render")

        magick_command.quantize(self.renderer.get_palette_path(
            frame.base_palette),self.renderer.dither_mode, self.renderer.floyd_steinberg_diffusion)

        # this should be moved somewhere it can run once per palette change
        self.renderer.get_recolor_shades()

        # Force the recolorables to a palette that only contains the recolorable color
        channels_to_exclude_for_mai = ["Green", "Blue"]

        for i in range(frame.recolorables):
            mask = MagickCommand("mpr:meta")
            mask.nullify_channels(channels_to_exclude_for_mai)
            mask.id_mask(i + 1, 0, 0)

            palette = self.renderer.palette_manager.get_recolor_palette(i)
            orct2_palette = self.renderer.palette_manager.get_orct2_recolor_palette(
                i)

            forced_color_render = MagickCommand("mpr:render")
            forced_color_render.quantize(self.renderer.get_palette_path(palette), self.renderer.floyd_steinberg_diffusion)
            
            # Replace our input color with the appropriate orct2 remap color
            for i in range(min(len(palette.shades), len(orct2_palette.shades))):
                forced_color_render.replace_color(palette.shades[i],orct2_palette.shades[i])

            magick_command.mask_mix(forced_color_render, mask)

        if frame.maintain_aliased_silhouette:
            magick_command.copy_alpha("mpr:meta")

        if not frame.oversized:
            self._process_default(magick_command, frame)
        else:
            self._process_oversized(magick_command, frame)

    def _process_default(self, magick_command, frame):
        quantized_output_path = frame.get_quantized_render_output_path()
        mask_path = frame.get_meta_render_output_path()

        if frame.occlusion_layers > 0:
            # If we are using occlusion layers, then render each seperately.
            result = str(subprocess.check_output(magick_command.get_command_string(
                self.renderer.magick_path, quantized_output_path), shell=True))

            magick_command = MagickCommand(quantized_output_path)

        layers = frame.occlusion_layers

        if layers == 0:
            layers = 1

        layer_command = magick_command

        for i in range(layers):
            output_index = frame.output_indices[i]
            output_path = frame.get_final_output_paths()[i]

            if frame.occlusion_layers > 0:
                layer_command = magick_command.clone()

                # Mask the occlusion layer
                mask = MagickCommand(mask_path)
                mask.nullify_channels(["Red", "Green"])
                mask.id_mask(0, 0, frame.occlusion_layers - i - 1)
                layer_command.mask_mix_self(mask)

            layer_command.trim()

            result = str(subprocess.check_output(layer_command.get_command_string(
                self.renderer.magick_path, output_path), shell=True))

            output_info = self._get_output_info_from_results(
                result, output_index, output_path)

            output_info.offset_y -= self.renderer.lens_shift_y_offset
            output_info.offset_y += self.renderer.context.scene.rct_graphics_helper_general_properties.y_offset

            output_info.offset_x += frame.offset_x
            output_info.offset_y += frame.offset_y

            frame.task.output_info.append(output_info)

    def _process_oversized(self, magick_command, frame):
        quantized_output_path = frame.get_quantized_render_output_path()

        mask_path = frame.get_meta_render_output_path()

        result = str(subprocess.check_output(magick_command.get_command_string(
            self.renderer.magick_path, quantized_output_path), shell=True))

        output_infos = []

        num_frames = frame.width * frame.length
        for i in range(frame.width):
            for j in range(frame.length):
                tile_index = j * frame.width + i
                final_output_index = frame.output_indices[tile_index]
                final_output_path = frame.get_final_output_paths()[tile_index]
                tile_magic_command = MagickCommand(quantized_output_path)

                inverse_tile_index = num_frames - tile_index - 1
                mask = MagickCommand(mask_path)
                mask.nullify_channels(["Red", "Blue"])
                mask.id_mask(0, inverse_tile_index, 0)

                tile_magic_command.mask_mix_self(mask)

                tile_magic_command.trim()

                result = str(subprocess.check_output(tile_magic_command.get_command_string(
                    self.renderer.magick_path, final_output_path), shell=True))

                output_info = self._get_output_info_from_results(
                    result, final_output_index, final_output_path)

                # Modify the output offsets for the sub tile we're processing
                x, y = (i - (frame.width - 1) /
                        2), (j - (frame.length - 1) / 2)

                rot = round(frame.view_angle / 90) % 4

                if rot == 1:
                    x, y = (-y,  x)
                if rot == 2:
                    x, y = (-x, -y)
                if rot == 3:
                    x, y = (y, -x)

                dx = -int((x * 32) - (y * 32))
                dy = -int((y * 16) + (x * 16))

                output_info.offset_x += dx
                output_info.offset_y += dy

                output_info.offset_y -= self.renderer.lens_shift_y_offset
                output_info.offset_y += self.renderer.context.scene.rct_graphics_helper_general_properties.y_offset

                output_info.offset_x += frame.offset_x
                output_info.offset_y += frame.offset_y

                output_infos.append(output_info)

        frame.task.output_info += output_infos

    def _get_output_info_from_results(self, result, output_index, output_path):
        output = Output()
        output.index = output_index
        output.path = output_path

        if result[2:][:-1] is not "":
            offset_coords = result[2:][:-1].split(" ")
            output.offset_x = int(round(float(offset_coords[0])))
            output.offset_y = int(round(float(offset_coords[1]))) + 15

        return output
