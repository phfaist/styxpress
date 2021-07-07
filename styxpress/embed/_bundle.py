import os.path
import string
import datetime
import logging
import subprocess

logger = logging.getLogger(__name__)


class Environment:
    def __init__(self):
        self.tex_kpsewhich_path = None
        #self.tex_distribution_path = None

    def find_executable(self, exe_name):
        from distutils.spawn import find_executable
        x = find_executable(exe_name)
        if not x:
            raise RuntimeError(
                f"Could not locate executable ‘{x}’. Please set PATH accordingly."
            )
        return x

    def _ensure_tex_kpsewhich_path(self):
        # find TeX distribution path
        if self.tex_kpsewhich_path is None:
            self.tex_kpsewhich_path = self.find_executable('kpsewhich')

    def kpsewhich(self, fname):
        self._ensure_tex_kpsewhich_path()
        try:
            output = subprocess.check_output(
                args=[self.tex_kpsewhich_path, fname],
                input=None,
            ).decode('utf-8').strip()
            return output
        except subprocess.CalledProcessError as e:
            logger.error("kpsewhich failed: %s", e)
            raise RuntimeError(
                f"Unable to locate file {fname} via TeX' kpsewhich"
            )



_tmpl_header = string.Template(r"""\NeedsTeXFormat{$BUNDLELATEXFORMAT}
\ProvidesPackage{$BUNDLEPACKAGENAME}[$BUNDLEPACKAGEDATE $BUNDLEPACKAGEVERSION]
%% Begin styxpress <$BUNDLEPACKAGENAME>
""")

_tmpl_footer = string.Template(r"""%% End styxpress <$BUNDLEPACKAGENAME>""" + "\n")


class TargetBundle:
    def __init__(self, environment, package_name):

        self.environment = environment

        self.bundle_package_name = package_name
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

        from ._resolve_engine import resolve_embed_engine

        embed_engine_cls = resolve_embed_engine(embed_engine)
        # create embed engine instance
        instance = embed_engine_cls(self, config)

        self._embeds.append( {
            'embed_engine': embed_engine,
            'embed_engine_cls': embed_engine_cls,
            'config': config,
            '_instance': instance
        } )

    def get_header(self):
        return _tmpl_header.substitute( **self._tmpl_subst )

    def get_footer(self):
        return _tmpl_footer.substitute( **self._tmpl_subst )

    def generate(self, output_dir='.'):

        foutname = os.path.join(output_dir, self.bundle_package_name + '.sty')

        if os.path.exists(foutname):
            logger.error(f"File {foutname} exists, sorry I'm not confident enough to overwrite it. Please delete it first.")
            raise RuntimeError(f"File {foutname} exists")

        with open(foutname, 'w') as f:

            f.write( self.get_header() )

            for d in self._embeds:
                d['_instance'].embed(f)

            f.write( self.get_footer() )


