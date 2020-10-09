import os
import ctypes.util
import sdl2.ext

from departure.board import renderer


class SdlExtRendererException(Exception):
    pass


class SdlExtRenderer(renderer.Renderer):
    def __init__(self):
        if (
            ctypes.util.find_library("SDL2") is None
            and "PYSDL2_DLL_PATH" not in os.environ
        ):
            raise SdlExtRendererException("missing PYSDL2_DLL_PATH env var")
        self.window = None
        self.renderer = None

    def initialise(self, size):  # pylint: disable=arguments-differ
        sdl2.ext.init()
        self.window = sdl2.ext.Window("Departure board", size=size)
        self.window.show()
        self.renderer = sdl2.ext.Renderer(self.window)

    def render_pixel(self, x, y, colour):
        raise NotImplementedError()

    def render_frame(self, pixels):
        self.renderer.clear(sdl2.ext.Color(0, 0, 0))

        for x, y, colour in pixels:
            self.render_pixel(x, y, colour)

        # show current frame
        self.renderer.present()

    def terminate(self):
        sdl2.ext.quit()


class SdlExtRendererActualSize(SdlExtRenderer):
    def render_pixel(self, x, y, colour):
        self.renderer.draw_point((x, y), sdl2.ext.Color(*colour))


class SdlExtRendererLarge(SdlExtRenderer):
    def initialise(self, size):
        super().initialise((5 * size[0], 5 * size[1]))

    def render_pixel(self, x, y, colour):
        # can't use the below as too slow
        """
        big_x = 5*x
        big_y = 5*y
        self.renderer.draw_point(
            (
                big_x + 1, big_y,
                big_x + 2, big_y,
                big_x, big_y + 1,
                big_x + 1, big_y + 1,
                big_x + 2, big_y + 1,
                big_x + 3, big_y + 1,
                big_x, big_y +2,
                big_x + 1, big_y + 2,
                big_x + 2, big_y + 2,
                big_x + 3, big_y + 2,
                big_x + 1, big_y + 3,
                big_x + 2, big_y + 3
            ),
            sdl2.ext.Color(*colour))
        """
        self.renderer.fill((5 * x, 5 * y, 4, 4), sdl2.ext.Color(*colour))
