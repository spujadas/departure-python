from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from departure_board import renderer


class Renderer(renderer.Renderer):
    def __init__(self):
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 192
        options.hardware_mapping = "adafruit-hat"
        options.brightness = 50
        self.matrix = RGBMatrix(options=options)

    def initialise(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()

    def render_frame(self, pixels):
        self.offscreen_canvas.Clear()

        for x, y, colour in pixels:
            self.offscreen_canvas.SetPixel(x, y, *colour)

        self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def terminate(self):
        pass
