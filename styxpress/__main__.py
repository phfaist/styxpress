
import sys
import os
import os.path

import yaml

import argparse
import logging
import string

from .embed import Environment, TargetBundle


def main():

    parser = argparse.ArgumentParser(
        prog='styxpress',
        epilog='Have loads of fun!',
    )

    parser.add_argument("styxpress_setup_file", metavar='styxpress_setup_file',
                        help="YaML setup file describing a merger of sty files")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # parse config file
    with open(args.styxpress_setup_file, 'r') as stream:
        try:
            setup_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.critical(f'Parse error in {args.styxpress_setup_file}.',
                            exc_info=exc)
            sys.exit(1)

    logger.info("Read config: %r", setup_config)

    env = Environment()

    bundle = TargetBundle(
        env,
        setup_config['bundle']['package_name']
    )

    for em_d in setup_config['embed']:

        if 'styname' in em_d:
            em_d = { 'embed_engine': 'sty',
                     'config': dict(em_d) }

        bundle.add_embed(em_d['embed_engine'], em_d['config'])


    bundle.generate(output_dir=setup_config['bundle'].get('output_dir', '.'))

    logger.info('Done.')


if __name__ == '__main__':
    main()

