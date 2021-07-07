import string

from ._embedder_engine import EmbedderEngine


#keys: FILEBASENAME, FILEEXTENSION, MERGEDPACKAGENAME, PKGOPTIONS

# taken from latex.ltx -> \def\@onefilewithoptions{...}
_wrapper_sty_start = string.Template(
r"""%%% -- styxpress wrapper code begin --
\@pushfilename
\xdef\@currname{$FILEBASENAME}%
\gdef\@currext{$FILEEXTENSION}%
\expandafter\let\csname\@currname.\@currext-h@@k\endcsname\@empty
\let\CurrentOption\@empty
\@reset@ptions
\makeatletter
\@ifl@aded\@currext{$FILEBASENAME}{%
  \PackageError{$MERGEDPACKAGENAME}{%
  A package named `$FILEBASENAME` is already loaded.}{}%
}{}%
\@pass@ptions\@currext{$PKGOPTIONS}{$FILEBASENAME}%
\global\expandafter\let\csname ver@\@currname.\@currext\endcsname\@empty
%%% -- $FILEBASENAME.$FILEEXTENSION contents begin --
\message{***STYXPRESS: USING PRE-PACKAGED VERSION OF $FILEBASENAME***}%
""")

_wrapper_sty_end = string.Template(
r"""%%% -- $FILEBASENAME.$FILEEXTENSION contents end --
\let\@unprocessedoptions\@@unprocessedoptions
\csname\@currname.\@currext-h@@k\endcsname
\expandafter\let\csname\@currname.\@currext-h@@k\endcsname
\@undefined
\@unprocessedoptions
\ifx\@currext\@clsextension\let\LoadClass\@twoloadclasserror\fi
\@popfilename
\@reset@ptions
%%% -- styxpress wrapper code end --
""")


_latex_endinput_commands = [
    r'\endinput',
    r'\file_input_stop:', # for packages w/ Expl3 syntax
]


class StyEmbedder(EmbedderEngine):
    def __init__(self, target_bundle, kwargs):
        super().__init__()
        self.target_bundle = target_bundle
        self._initialize(**kwargs)

    def _initialize(self, styname, options='', use_auto_ext=True, tex_path_search=False)
        self.styname = styname
        self.options = options
        self.use_auto_ext = use_auto_ext
        self.tex_path_search = tex_path_search
        
        sty_file_name = self.styname
        if use_auto_ext:
            if not sty_file_name.endswith('.sty'):
                sty_file_name += '.sty'
        if tex_path_search:
            sty_file_name = target_bundle.environment.kpsewhich(sty_file_name)

        styfnamebase, styfnameext = os.path.splitext(self.sty_file_name)
        self.styfnamebase = styfnamebase
        self.styfnameext = styfnameext.lstrip('.')
        self._tmpl_substkeys = {
            'FILEBASENAME': self.styfnamebase,
            'FILEEXTENSION': self.styfnameext,
            'MERGEDPACKAGENAME': target_bundle.bundle_package_name(),
            'PKGOPTIONS': self.options,
        }

        self.latex_endinput_commands = list(_latex_endinput_commands)

    def wrapper_sty_begin(self):
        return _wrapper_sty_start.substitute(**self._tmpl_substkeys)
        
    def wrapper_sty_end(self):
        return _wrapper_sty_end.substitute(**self._tmpl_substkeys)

    def read_and_copy_sty(self, fout):
        with open(self.sty_file_name, 'r') as fsty:
            contents = fsty.read()
            for endinputcmd in self.latex_endinput_commands:
                i = contents.rfind(endinputcmd)
                if i != -1:
                    contents = contents[:i]
            fout.write(contents)

    def embed(self, f):
        f.write(wrapper_sty_start.substitute(**substkeys))
        self.read_and_copy_sty(f)
        f.write(wrapper_sty_end.substitute(**substkeys))

