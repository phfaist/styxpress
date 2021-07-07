
import os
import os.path

import argparse
import logging
import string

from . import embed


def main():

    parser = argparse.ArgumentParser(
        prog='styxpress',
        epilog='Have loads of fun!',
    )

    # parser.add_argument("file", nargs='+',
    #                     metavar='file',
    #                     help="Input file to parse mergers")

    args = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger(__name__)

    mergestybasename = 'merger'

    with open(mergestybasename + ".sty", "w") as f:
        f.write(r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesPackage{merger}[2021/04/22 TEST TEST TEST]
""")
        for styfname, styfoptions in [('testa.sty', ''),
                                      ('xsimverb.sty', 'clear-aux,verbose,no-files'),
                                      ('xsim.sty', 'clear-aux,verbose,no-files'),
                                      ('testb.sty', 'providetestbac,ddd')]:
            #f.write(r"\PassOptionsToPackage{" + styfoptions + "}{" + styfname + "}\n")
            styfnamebase, styfnameext = os.path.splitext(styfname)
            styfnameext = styfnameext.lstrip('.')
            substkeys = {
                'FILEBASENAME': styfnamebase,
                'FILEEXTENSION': styfnameext,
                'MERGEDPACKAGENAME': mergestybasename,
                'PKGOPTIONS': styfoptions,
            }
            f.write(wrapper_sty_start.substitute(**substkeys))
            with open(styfname, 'r') as fsty:
                contents = fsty.read()
                i = contents.rfind(r'\endinput')
                if i != -1:
                    contents = contents[:i]
                i = contents.rfind(r'\file_input_stop:') # for packages w/ Expl3 syntax
                if i != -1:
                    contents = contents[:i]
                f.write(contents)
            f.write(wrapper_sty_end.substitute(**substkeys))


if __name__ == '__main__':
    main()

