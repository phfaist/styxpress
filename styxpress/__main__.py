import sys
import os
import os.path

import argparse
import logging
import string

import yaml

import colorlog

from ._bundle import Environment, TargetBundle


def setup_logging(level):
    # You should use colorlog >= 6.0.0a4
    handler = colorlog.StreamHandler()
    handler.setFormatter( colorlog.LevelFormatter(
        log_colors={
            "DEBUG": "white",
            "INFO": "",
            "WARNING": "red",
            "ERROR": "bold_red",
            "CRITICAL": "bold_red",
        },
        fmt={
            # emojis we can use: 🐞 🐜 🚨 🚦 ⚙️ 🧨 🧹 ❗️❓‼️ ⁉️ ⚠️ ℹ️ ➡️ ✔️ 〰️
            # 🎶 💭 📣 🔔 ⏳ 🔧 🔩 ✨ 💥 🔥 🐢 👉
            "DEBUG":    "%(log_color)s〰️    %(message)s", #'  [%(name)s]'
            "INFO":     "%(log_color)s✨  %(message)s",
            "WARNING":  "%(log_color)s⚠️   %(message)s", # (%(module)s:%(lineno)d)",
            "ERROR":    "%(log_color)s🚨  %(message)s", # (%(module)s:%(lineno)d)",
            "CRITICAL": "%(log_color)s🚨  %(message)s", # (%(module)s:%(lineno)d)",
        },
        stream=sys.stderr
    ) )

    root = colorlog.getLogger()
    root.addHandler(handler)

    root.setLevel(level)




def main():

    parser = argparse.ArgumentParser(
        prog='styxpress',
        epilog='Have loads of fun!',
    )

    parser.add_argument("styxpress_folder", metavar='styxpress_folder',
                        help="Folder (conventionally with suffix *.styxpress) containing "
                        "a 'info.yml' describing a styxpress merger")

    parser.add_argument('-q', '--quiet', dest='verbosity', action='store_const',
                        const=logging.ERROR, default=logging.INFO,
                        help="Suppress warning messages")
    parser.add_argument('-v', '--verbose', dest='verbosity', action='store_const',
                        const=logging.DEBUG,
                        help='verbose mode')

    args = parser.parse_args()

    setup_logging(level=args.verbosity)
    logger = logging.getLogger(__name__)


    styxpress_folder = args.styxpress_folder.rstrip('/') # remove any trailing slashes
    styxpress_folder_parent_dir, styxpress_folder_name = os.path.split(styxpress_folder)

    info_yml = os.path.join(styxpress_folder, 'info.yml')

    logger.debug("Reading styxpress merger info from ‘%s’", info_yml)

    # parse config file
    with open(info_yml, 'r') as stream:
        try:
            setup_config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.critical(f'Parse error in ‘{info_yml}’.',
                            exc_info=exc)
            sys.exit(1)

    logger.debug("Read config: %r", setup_config)

    env = Environment()

    bundle_config = setup_config.get('bundle', {})
    package_name = bundle_config.get('package_name', styxpress_folder_name)
    output_dir = bundle_config.get('output_dir', styxpress_folder_parent_dir)

    bundle = TargetBundle(env, styxpress_folder, package_name)

    if 'version' in bundle_config:
        bundle.bundle_package_version = bundle_config['version']

    if 'date' in bundle_config:
        bundle.bundle_package_date = bundle_config['date']

    embed_rules = setup_config['embed']

    for em_d in embed_rules:

        bundle.add_embed(em_d['embed_engine'], em_d.get('config', {}))

    bundle.generate(output_dir=output_dir)

    logger.info('Done.')


if __name__ == '__main__':
    main()

