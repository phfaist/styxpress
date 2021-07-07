import string
import datetime

from ._resolve_engine import resolve_embed_engine


class Environment:
    def __init__(self):
        self.tex_distribution_path = .... # find TeX distribution path


    def kpsewhich(fname):

        path = subprocess.check_output('kpsewhich', ......)
        return path


_tmpl_header = string.Template(r"""\NeedsTeXFormat{$BUNDLELATEXFORMAT}
\ProvidesPackage{$BUNDLEPACKAGENAME}[$BUNDLEPACKAGEDATE $BUNDLEPACKAGEVERSION]
%% Begin styxpress <%BUNDLEPACKAGENAME>
""")

_tmpl_footer = string.Template(r"""%% End styxpress <$BUNDLEPACKAGENAME>""" + "\n")


class TargetBundle:
    def __init__(self, environment, package_name):

        self.environment = environment

        self.bundle_package_name = bundle_package_name
        self.bundle_latex_format = 'LaTeX2e'
        self.bundle_package_date = datetime.datetime.now().strftime('%Y/%m/%d')
        self.bundle_package_version = 'v0.1.0'

        self._embeds = []

        self._tmpl_subst = dict(
            BUNDLELATEXFORMAT=self.bundle_latex_format,
            BUNDLEPACKAGENAME=self.bundle_package_name,
            BUNDLEPACKAGEDATE=self.bundle_package_date,
            BUNDLEPACKAGEVERSION=self.bundle_package_version,
        )

    def add_embed(self, embed_engine, config):

        embed_engine_cls = resolve_embed_engine(embed_engine)
        # create embed engine instance
        instance = embed_engine_cls(self, config)

        self._embeds.append( {
            'embed_engine': embed_engine,
            'embed_engine_cls': embed_engine_cls,
            'config': config
        } )

    def get_header(self):
        return _tmpl_header.substitute( **self._tmpl_subst )

    def get_footer(self):
        return _tmpl_footer.substitute( **self._tmpl_subst )

    def generate(self):
        f.write( get_header() )
        
        for d in self._embeds:
            d['instance'].embed(f)

        f.write( get_footer() )


