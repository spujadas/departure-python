class Renderer:
    def initialise(self):
        raise NotImplementedError()

    def render_frame(self, pixels):
        raise NotImplementedError()

    def terminate(self):
        raise NotImplementedError()
