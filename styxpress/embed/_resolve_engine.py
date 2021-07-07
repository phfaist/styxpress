

def resolve_embed_engine(embed_engine):

    if embed_engine == 'sty':
        from .sty import StyEmbedder
        return StyEmbedder

    if embed_engine == 'pdflogo':
        from .pdflogo import PdfLogoEmbedder
        return PdfLogoEmbedder

    raise ValueError(f"Unknown/invalid {embed_engine=}")

    


