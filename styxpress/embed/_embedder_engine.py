import io


class EmbedderEngine:
    def __init__(self):
        return

    def embed_s(self):
        f = io.StringIO()
        self.embed(f)
        return f.getvalue()
