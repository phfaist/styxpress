import re
import os.path
import string

import base64

import logging

logger = logging.getLogger(__name__)


from ._embedder_engine import EmbedderEngine


_tmpl_defcmd = string.Template(r"""%% <$PDFNAME> -> \$CMDNAME
\RequirePackage{graphicx}%
\def\$CMDNAME{\includegraphics{$TEMPGRAPHICSFILENAME}}
\begin{filecontents*}{$TEMPGRAPHICSFILENAME}
$PDFDATA
\end{filecontents*}%
""")


class PdfEmbedder(EmbedderEngine):
    def __init__(self, target_bundle, kwargs):
        super().__init__(target_bundle)
        self._initialize(**kwargs)

    def _initialize(self, *, pdfname, cmdname,
                    temp_graphics_filename=None, hidden_temp_file=False):
        self.pdfname = pdfname
        self.cmdname = cmdname
        if temp_graphics_filename is None:
            temp_graphics_filename = f'_styxpress_tmp_{pdfname}'
            if hidden_temp_file:
                temp_graphics_filename = '.' + temp_graphics_filename
        self.temp_graphics_filename = temp_graphics_filename

        
    def get_pdf_data(self):

        fname = self.target_bundle.resolve_file_name(self.pdfname)

        with open(fname, 'rb') as f:
            data = f.read()

        def comment_with_length(n):
            if n == 0:
                return b''
            if n == 1:
                return b'\n'
            return b'%'*(n-1) + b'\n'

        # cut out the initial binary data that you see sometimes in the initial
        # header.  CAREFUL: We need to keep the byte addresses the same in the
        # file, so make sure that the number of characters doesn't change !
        data = re.sub(rb'^(%PDF-[\d.]+)(.*\r?\n)(\%.*\r?\n)*',
                      lambda m: (
                          m.group(1) + b'\n' +
                          comment_with_length(len(m.group())-len(m.group(1))-1)
                      ),
                      data)

        # check that the contents is not binary data
        try:
            data = data.decode('ascii')
        except UnicodeDecodeError:
            msg = (
                f"The PDF file ‘{fname}’ contains binary data.  Please process the "
                f"file to make it ASCII-only.  You can do this e.g. with the `mutool` "
                f"utility from the `mupdf` suite with the command `` "
                f"mutool convert -F pdf -O \"decompress,ascii\" -o OUTPUT_FILE.pdf INPUT_FILE.pdf"
                f" ``.  One day I might be able to do this automatically, but that's "
                f"not the case yet, sorry.  If `mutool` complains about fonts, you can "
                f"try to outline all fonts with ghostscript first using `` "
                f"gs -q -dBATCH -dSAFER -dNOPAUSE -dNoOutputFonts "
                    f"-sDEVICE=pdfwrite -sOutputFile=OUTPUT_FILE.pdf INPUT_FILE.pdf"
                f" ``).")
            logger.error(msg)
            raise ValueError(msg)

        return data
            

    def embed(self, f):

        pdfdata = self.get_pdf_data()

        f.write(_tmpl_defcmd.substitute(
            PDFNAME=self.pdfname,
            CMDNAME=self.cmdname,
            TEMPGRAPHICSFILENAME=self.temp_graphics_filename,
            PDFDATA=pdfdata
        ))

