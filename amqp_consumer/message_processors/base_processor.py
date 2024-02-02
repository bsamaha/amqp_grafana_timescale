class BaseProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        raise NotImplementedError("Each processor needs a specific implementation of process()")
