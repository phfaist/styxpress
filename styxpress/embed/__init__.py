# styxpress.embed [__init__]


from ._embedder_engine import EmbedderEngine


from ._bundle import Bundle

class Embedder:
    ....



embed_engines = {
    'sty': _engine_sty
}

def load_embedder_engine(engine_name):
    from . import sty as _engine_sty
    

    

