import pathlib

from bdflib import reader


def read_bdf_font(font_filename):
    font_path = pathlib.Path(__file__).parents[0] / font_filename
    with font_path.open("rb") as f:
        return reader.read_bdf(f)


class BoardTextException(Exception):
    pass


class BoardText:
    def __init__(self, font, colour_map=None, tabs=None):
        self.font = font
        self.colour_map = colour_map
        self.tabs = tabs

    def _glyph_pixels(self, glyph, x_offset, y_offset, colour=(255, 255, 255)):
        # pixel coordinate system (x,y) = (0,0) => top left
        # glyph coordinate system (x,y) = (0,0) => bottom left
        # y_offset = (FONT_ASCENT - 1) + line_number * (FONT_HEIGHT + line_spacing)
        # where FONT_HEIGHT = FONT_ASCENT + FONT_DESCENT
        return [
            (x_offset + x, y_offset - y - glyph.bbY, colour)
            for x in range(glyph.bbW)
            for y in range(glyph.bbH)
            if glyph.data[y] & (1 << (glyph.bbW - x - 1))
        ]

    def monochrome_text_pixels(
        self, text, colour=(255, 255, 255), max_width=0  # 0 == no max width
    ):
        pixels = []
        advance = 0
        for c in text:
            glyph = self.font[ord(c)]
            pixels += self._glyph_pixels(
                glyph, advance, self.font[b"FONT_ASCENT"] - 1, colour
            )
            advance += glyph.advance
            if max_width > 0 and advance > max_width:
                break

        return pixels, (advance, self.font[b"FONT_ASCENT"] + self.font[b"FONT_DESCENT"])

    def colour_text_pixels(self, text_array):
        if self.colour_map is None:
            raise BoardTextException("missing colour map")

        x_size, y_size = 0, 0
        output_pixels = []

        for text_part in text_array:
            text, colour = text_part[:2]
            if len(text_part) == 3:
                max_width = text_part[2]
            else:
                max_width = 0
            pixels, size = self.monochrome_text_pixels(
                text, self.colour_map[colour], max_width
            )
            output_pixels += [(x + x_size, y, c) for x, y, c in pixels]
            x_size += size[0]
        y_size = size[1]
        return output_pixels, (x_size, y_size)

    def colour_text_tabbed_row_pixels(self, text_row):
        if self.tabs is None:
            raise BoardTextException("missing tabs")

        output_pixels = []
        x_size = 0
        for i, text_part in enumerate(text_row):
            tab_pos, tab_type = self.tabs[i]
            text, colour = text_part[:2]
            if len(text_part) == 3:
                max_width = text_part[2]
            else:
                max_width = 0
            pixels, size = self.monochrome_text_pixels(
                text, self.colour_map[colour], max_width
            )

            if tab_type == "l":
                output_pixels += [(x + tab_pos, y, c) for x, y, c in pixels]
                # extend width as needed
                x_size = max(x_size, size[0] + tab_pos)

            elif tab_type == "r":
                output_pixels += [
                    (tab_pos + 1 - size[0] + x, y, c) for x, y, c in pixels
                ]
                # extend width as needed
                x_size = max(x_size, tab_pos + 1)

        y_size = size[1]

        return output_pixels, (x_size, y_size)

    def colour_text_tabbed_rows_pixels(self, text_rows, row_height):
        pixels = []
        x_size = 0
        i = 0

        for i, text_row in enumerate(text_rows):
            row_pixels, size = self.colour_text_tabbed_row_pixels(text_row)
            pixels += [(x, y + i * row_height, c) for x, y, c in row_pixels]
            x_size = max(x_size, size[0])

        y_size = (i + 1) * row_height

        return pixels, (x_size, y_size)
