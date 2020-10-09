import pygame

from departure.board import renderer


class PygameRenderer(renderer.Renderer):
    def __init__(self):
        self.screen = None
        pygame.init()

    def initialise(self, size):  # pylint: disable=arguments-differ
        self.screen = pygame.display.set_mode(size)

    def render_pixel(self, x, y, colour):
        raise NotImplementedError()

    def render_frame(self, pixels):
        self.screen.fill((0, 0, 0))

        for x, y, colour in pixels:
            self.render_pixel(x, y, colour)

        # show current frame
        pygame.display.flip()

    def terminate(self):
        pygame.quit()


class PygameRendererActualSize(PygameRenderer):
    def render_pixel(self, x, y, colour):
        self.screen.set_at((x, y), colour)


class PygameRendererLarge(PygameRenderer):
    def initialise(self, size):
        super().initialise((5 * size[0], 5 * size[1]))

    def render_pixel(self, x, y, colour):
        pygame.draw.circle(self.screen, colour, (2 + 5 * x, 2 + 5 * y), 2)
