import importlib


def resolve_embed_engine(embed_engine):

    m = importlib.import_module(embed_engine)

    cls = m.__dict__['StyxpressEmbedder']
    return cls

    


