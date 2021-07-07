import re
import os.path
import string

import base64

import logging

logger = logging.getLogger(__name__)


import PyPDF2


from ._embedder_engine import EmbedderEngine


# want:
# \def\CMDNAME{\phantom{\rule{<size of graphics>}{...}}\pdfliteral{ ... PDF CODE ... }}
# (or something like that)
_tmpl_defcmd = string.Template(r"""%% <$PDFNAME> -> \$CMDNAME
\def\$CMDNAME{\begingroup
\unitlength=1bp\relax
\begin{picture}($PAGEWIDTH,$PAGEHEIGHT)($PAGEORIGINX,$PAGEORIGINY)%
%\put(0,0){\line(1,0){100}} %DEBUG
%\put(0,0){\line(0,1){25}} %DEBUG
\pdfliteral{q $PDFLITERAL Q}%
\end{picture}\endgroup
}%
""")


class PdfLogoEmbedder:
    def __init__(self, target_bundle, kwargs):
        super().__init__()
        self.target_bundle = target_bundle
        self._initialize(**kwargs)

    def _initialize(self, *, pdfname, page=0, cmdname):
        self.pdfname = pdfname
        self.page = page
        self.cmdname = cmdname

        
    def get_pdf_contents(self):

        pdfreader = PyPDF2.PdfFileReader(self.pdfname)
        pageobj = pdfreader.getPage(self.page)

        contents = pageobj.getContents()

        #logger.debug(f"{contents=!r}")

        data = contents.getData()

        # try to "sanitize" data as best as possible
        # remove binary data:  <<...>> ID ...DATA... EI

        rx = re.compile(
            rb'\bBI\s+(?P<dict>.*?)\s*ID\s(?P<data>.*?)\s*EI\b',
            flags=re.DOTALL
        )

        def sub_m(m):
            if re.search(rb'/F(ilter)?\b', m.group('dict')) is not None:
                logger.error(f"There's an inline binary image in {self.pdfname} "
                             "that I couldn't handle, sorry. Maybe try to reencode "
                             "your PDF differently?")
                raise RuntimeError(f"Can't handle inline binary image in {self.pdfname}.")
            new_img_code = (
                b'BI ' + m.group('dict') + b' /Filter /ASCIIHexDecode '
                + b'ID ' + base64.b16encode(m.group('data')) + b'\nEI ')
                # + b'<<' + m.group('dict') + b' /Filter /ASCII85Decode >> '
                # + b'ID ' + base64.a85encode(m.group('data')) + b'\nEI ')
            return new_img_code

        data = rx.sub(sub_m, data)

        logger.debug(f"{data=!r}")

        (x1,y1,x2,y2) = pageobj.mediaBox

        return ( data, (x1,y1,x2,y2) )
            

    def embed(self, f):

        pdfdata, pagebox = self.get_pdf_contents()

        #logger.debug(f"{pdfdata=!r}")

        # pdfdata_enc = re.sub(
        #     # not r'..' so that \u.... gets expanded, also include '^' char itself
        #     b'([^\x20-\x7e\x0a]|[%^&\\\\])',
        #     lambda m: '^^{:02x}'.format(ord(m.group())).encode('ascii'),
        #     pdfdata
        # ).decode('utf-8')

        try:
            pdfdatastr = pdfdata.decode('ascii')
        except UnicodeDecodeError as e:
            logger.error(f"Cannot embed file {self.pdfname}: content stream "
                         "has binary contents (perhaps an inline image?).  Please "
                         "re-encode your PDF file contents differently.")
            raise RuntimeError(f"Cannot embed file {self.pdfname}")

        logger.debug(f"{pdfdatastr=}")

        f.write(_tmpl_defcmd.substitute(
            PDFNAME=self.pdfname,
            CMDNAME=self.cmdname,
            PAGEORIGINX="{:.6g}".format(-pagebox[0]),
            PAGEORIGINY="{:.6g}".format(-pagebox[1]),
            PAGEWIDTH="{:.6g}".format(pagebox[2]-pagebox[0]),
            PAGEHEIGHT="{:.6g}".format(pagebox[3]-pagebox[1]),
            PDFLITERAL=pdfdatastr,
        ))

