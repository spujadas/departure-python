import os
import ctypes.util
import sdl2

from . import renderer


class SdlRendererException(Exception):
    pass


class SdlRenderer(renderer.Renderer):
    def __init__(self):
        if (
            ctypes.util.find_library("SDL2") is None
            and "PYSDL2_DLL_PATH" not in os.environ
        ):
            raise SdlRendererException("missing PYSDL2_DLL_PATH env var")
        self.window = None
        self.renderer = None

    def initialise(self, size):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.SDL_CreateWindow(
            b"Departure board",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            *size,
            sdl2.SDL_WINDOW_SHOWN
        )
        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1, sdl2.SDL_RENDERER_ACCELERATED
        )

    def render_pixel(self, x, y, colour):
        raise NotImplementedError()

    def render_frame(self, pixels):
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(self.renderer)

        for x, y, colour in pixels:
            self.render_pixel(x, y, colour)

        # show current frame
        sdl2.SDL_RenderPresent(self.renderer)

    def terminate(self):
        if self.renderer is not None:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window is not None:
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()


class SdlRendererActualSize(SdlRenderer):
    def __init__(self):
        super().__init__()

    def initialise(self, size):
        super().initialise(size)

    def render_pixel(self, x, y, colour):
        sdl2.SDL_SetRenderDrawColor(self.renderer, *colour, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderDrawPoint(self.renderer, x, y)


class SdlRendererLarge(SdlRenderer):
    def __init__(self):
        super().__init__()

    def initialise(self, size):
        super().initialise((5 * size[0], 5 * size[1]))

    def render_pixel(self, x, y, colour):
        # can't use the below as too slow
        big_x = 5 * x
        big_y = 5 * y
        sdl2.SDL_SetRenderDrawColor(self.renderer, *colour, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 1, big_y)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 2, big_y)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x, big_y + 1)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 1, big_y + 1)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 2, big_y + 1)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 3, big_y + 1)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x, big_y + 2)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 1, big_y + 2)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 2, big_y + 2)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 3, big_y + 2)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 1, big_y + 3)
        sdl2.SDL_RenderDrawPoint(self.renderer, big_x + 2, big_y + 3)

        # self.renderer.fill((5*x, 5*y, 4, 4), sdl2.ext.Color(*colour))
