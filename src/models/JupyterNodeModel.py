class JupyterNodeModel(object):
    def __init__(self, title, code, parent=None):
        self.title = title
        self.code = code
        self.source = None
        self.destination = None
        self.children = []
        self.x = 0
        self.y = 0
        super().__init__()

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            "title": self.title,
            "code": self.code,
            "source": self.source,
            "destination": self.destination,
            "children": [child.to_dict() for child in self.children],
            "x": self.x,
            "y": self.y
            }