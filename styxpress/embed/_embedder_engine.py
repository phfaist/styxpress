import io


class EmbedderEngine:
    def __init__(self, target_bundle):
        super().__init__()
        self.target_bundle = target_bundle


    def embed_s(self):
        f = io.StringIO()
        self.embed(f)
        return f.getvalue()
