#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import argparse
import os
from ofx_host import ofx_host

def extant_file(x):
    if not os.path.isfile(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

def extant_dir(x):
    if not os.path.isdir(x):
        raise argparse.ArgumentTypeError("{0} does not exist".format(x))
    return x

def valid_filetype(x):
    if x.rsplit('.', 1)[1].lower() not in ['png', 'jpg']:
        raise argparse.ArgumentTypeError("Filetype needs to be PNG or JPG")
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple command line OFX plugin render host.',
                                     epilog='Use -h on commands for further info.')

    subparsers = parser.add_subparsers(dest='command',
                                       metavar='{command}')
    subparsers.required = True

    bundle_parser = argparse.ArgumentParser(add_help=False)
    bundle_parser.add_argument('dir',
                               type=extant_dir,
                               help='Path to the ofx bundle directory.')
    bundle_parser.add_argument('bundle',
                               help='Name of the ofx bundle to load.')

    list_subparser = subparsers.add_parser('list',
                                           help='List all the plugins in the OFX bundle.',
                                           parents=[bundle_parser])

    param_subparser = subparsers.add_parser('params',
                                            help='Display or save a plugin\'s parameters.',
                                            parents=[bundle_parser])
    param_subparser.add_argument('plugin',
                                 help='Name of plugin to use.')
    param_subparser.add_argument('-j', '--json',
                                 help='Save parameters to JSON file. Used as input to render.')

    filter_subparser = subparsers.add_parser('filter',
                                             help='Render using filter context and default parameters.',
                                             parents=[bundle_parser])
    filter_subparser.add_argument('plugin',
                                  help='Name of plugin to use.')
    filter_subparser.add_argument('infile',
                                  type=extant_file,
                                  help='Filename of input image.')
    filter_subparser.add_argument('outfile',
                                  type=valid_filetype,
                                  help='Filename of output image.')

    render_subparser = subparsers.add_parser('render',
                                             help='Render using JSON file to set parameters.')
    render_subparser.add_argument('dir',
                                  type=extant_dir,
                                  help='Path to the ofx bundle directory.')
    render_subparser.add_argument('json',
                                  type=extant_file,
                                  help='Load parameter settings from JSON file.')

    args = parser.parse_args()

    host = ofx_host()

    if args.command == 'list':
        host.display_plugins(args.dir, args.bundle)
    elif args.command == 'params':
        if args.json is not None:
            host.params_to_json(args.dir, args.bundle, args.plugin, args.json)
        else:
            host.display_params(args.dir, args.bundle, args.plugin)
    elif args.command == 'filter':
        host.filter_render(args.dir, args.bundle, args.plugin, args.infile, args.outfile)
    elif args.command == 'render':
        host.json_render(args.dir, args.json)


