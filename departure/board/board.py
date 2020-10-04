from typing import Tuple, List

import departure.board.movement as movement

Pixel = Tuple[int, int, Tuple[int, int, int]]
Pixels = List[Pixel]


def repeated_offsets(
    x_offset: int,
    y_offset: int,
    content_w: int,
    content_h: int,
    display_w: int,
    display_h: int,
    repeat_x: bool = True,
    repeat_y: bool = True,
) -> Tuple[List[int], List[int]]:
    x_offsets = [x_offset]
    y_offsets = [y_offset]

    # repeat right if x_offset + content_w between 0 and display_w
    if repeat_x and (0 < x_offset + content_w < display_w):
        x_offsets.append(x_offset + content_w)

    # repeat down if y_offset + content_h between 0 and display_h
    if repeat_y and (0 < y_offset + content_h < display_h):
        y_offsets.append(y_offset + content_h)

    return x_offsets, y_offsets


def visible_pixels(
    pixels: Pixels, x_offset: int, y_offset: int, display_w: int, display_h: int
) -> Pixels:
    output_pixels = []

    for x, y, c in pixels:
        x_content = x + x_offset
        y_content = y + y_offset
        if (0 <= x_content < display_w) and (0 <= y_content < display_h):
            output_pixels.append((x_content, y_content, c))

    return output_pixels


def visible_pixels_multiple_offsets(
    pixels: Pixels,
    x_offsets: List[int],
    y_offsets: List[int],
    content_w: int,
    content_h: int,
    display_w: int,
    display_h: int,
) -> Pixels:
    output_pixels = []

    for x_offset in x_offsets:
        for y_offset in y_offsets:
            # ignore repetitions that wouldn't be visible
            if (
                (x_offset >= display_w)
                or (x_offset + content_w + display_w < 0)
                or (y_offset >= display_h)
                or (y_offset + content_h + display_h < 0)
            ):
                continue

            output_pixels += visible_pixels(
                pixels, x_offset, y_offset, display_w, display_h
            )

    return output_pixels


class BoardSectionContent:
    def __init__(
        self,
        content_pixels: Pixels,
        content_w: int,
        content_h: int,
        repeat_x: bool = True,
        repeat_y: bool = True,
    ):
        self.content_pixels = content_pixels  # relative to top-left of section

        # virtual bounding box (0, 0, content_w, content_h), used to add space
        # after contents, especially before repeating a message
        self.content_w = content_w
        self.content_h = content_h

        # should content repeat to the right and down?
        self.repeat_x = repeat_x
        self.repeat_y = repeat_y


class BoardSection:
    def __init__(
        self,
        output_x: int,
        output_y: int,
        output_w: int,
        output_h: int,
        content: BoardSectionContent,
        movement: movement.Movement = movement.NoMovement(),
    ):
        # area on the departure board where this section is displayed
        self.output_x = output_x
        self.output_y = output_y
        self.output_w = output_w
        self.output_h = output_h

        # content to be displayed in this section
        self._content = content

        # movement class
        self._movement = movement

        # pixels in absolute coordinates
        self.section_pixels = None

        self._has_changed = True

    def reset(self):
        self._movement.reset()

    def update_content(self, content: BoardSectionContent) -> None:
        self._content = content
        self._has_changed = True

    def update_movement(self, movement: movement.Movement) -> None:
        self._movement = movement
        self._has_changed = True

    def update(self, delta_time: int) -> bool:
        # update movement
        self._has_changed |= self._movement.update(delta_time)

        # wrap offset
        self._wrap_offset()

        return self._has_changed

    def _wrap_offset(self) -> None:
        offset_wrapped = False

        # wrap to between -content_w+1 and 0 if x_offset leq than -content_w
        if self._content.content_w <= 0:
            x_offset = 0
        elif self._movement.x_offset <= -self._content.content_w:
            x_offset = (
                ((self._movement.x_offset - 1) % self._content.content_w)
                - self._content.content_w
                + 1
            )
            offset_wrapped = True
        else:
            x_offset = self._movement.x_offset

        # wrap to between -self._content.content_h+1 and 0 if self._movement.y_offset leq than
        # -self._content.content_h
        if self._content.content_h <= 0:
            y_offset = 0
        elif self._movement.y_offset <= -self._content.content_h:
            y_offset = (
                ((self._movement.y_offset - 1) % self._content.content_h)
                - self._content.content_h
                + 1
            )
            offset_wrapped = True
        else:
            y_offset = self._movement.y_offset

        # update movement offset if it has wrapped
        if offset_wrapped:
            # don't mark as changed as displayed pixels are identical
            self._movement.set_offset(x_offset, y_offset)

    def pixels(self) -> Pixels:
        # return current section pixels if neither content nor movement has
        # changed
        if not self._has_changed:
            return self.section_pixels

        # get repeated offsets
        x_offsets, y_offsets = repeated_offsets(
            self._movement.x_offset,
            self._movement.y_offset,
            self._content.content_w,
            self._content.content_h,
            self.output_w,
            self.output_h,
            self._content.repeat_x,
            self._content.repeat_y,
        )

        # get repeated pixels
        repeated_pixels = visible_pixels_multiple_offsets(
            self._content.content_pixels,
            x_offsets,
            y_offsets,
            self._content.content_w,
            self._content.content_h,
            self.output_w,
            self.output_h,
        )

        # translate pixels to location of board section
        self.section_pixels = []
        for x, y, c in repeated_pixels:
            self.section_pixels.append([x + self.output_x, y + self.output_y, c])

        self._has_changed = False

        return self.section_pixels


class Board:
    def __init__(self, board_w: int, board_h: int, sections: List[BoardSection] = []):
        self.board_w = board_w
        self.board_h = board_h
        self.sections = sections
        self.display_pixels = None
        self._has_changed = True

    def reset(self):
        for section in self.sections:
            section.reset()

    def update(self, delta_time: int):
        for section in self.sections:
            self._has_changed |= section.update(delta_time)
        return self._has_changed

    def pixels(self) -> Pixels:
        if not self._has_changed:
            return self.display_pixels

        self.display_pixels = []
        for section in self.sections:
            self.display_pixels += section.pixels()

        self._has_changed = False

        return self.display_pixels
