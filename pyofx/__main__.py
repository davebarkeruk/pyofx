#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import argparse
import os
from PIL import Image
from ofx_host import ofx_host
from ofx_status_codes import *

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
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='Simple command line OFX plugin render host.',
                                     epilog='Use -h on commands for further info.\n')
    subparsers = parser.add_subparsers(dest='command',
                                       metavar='{command}')
    subparsers.required = True

    bundle_parser = argparse.ArgumentParser(add_help=False)
    bundle_parser.add_argument('dir',
                               type=extant_dir,
                               help='Path to the ofx bundle directory.')
    bundle_parser.add_argument('bundle', type=str,
                               help='Name of the ofx bundle to load.')

    list_subparser = subparsers.add_parser('list',
                                           help='List all the plugins in the OFX bundle.',
                                           parents=[bundle_parser])

    describe_subparser = subparsers.add_parser('desc',
                                               help='Describe an OFX Plugin.',
                                               parents=[bundle_parser])
    describe_subparser.add_argument('plugin',
                                    help='Name of plugin to use.')

    describe_subparser.add_argument('-j', '--json',
                                    help='Save parameter details to JSON file (can be used as input to render).')

    render_subparser = subparsers.add_parser('render',
                                             help='Render an OFX Plugin.',
                                             parents=[bundle_parser])
    render_subparser.add_argument('plugin',
                                  help='Name of plugin to use.')
    render_subparser.add_argument('infile',
                                  type=extant_file,
                                  help='Filename of input image.')
    render_subparser.add_argument('outfile',
                                  type=valid_filetype,
                                  help='Filename of output image.')
    render_subparser.add_argument('-j', '--json',
                                  help='Load parameter settings from JSON file.')

    args = parser.parse_args()

    if args.command == 'list':
        host = ofx_host()
        if host.load_ofx_binary(args.dir, args.bundle) == OFX_STATUS_OK:
            host.list_all_plugins(args.bundle)
    elif args.command == 'desc':
        host = ofx_host()
        if host.load_ofx_binary(args.dir, args.bundle) == OFX_STATUS_OK:
            status = host.plugin_load_and_describe(args.bundle, args.plugin)
            status = host.list_plugin_parameters(args.bundle, args.plugin)
            if args.json is not None:
                status = host.save_plugin_parameters(args.bundle, args.plugin, args.json)
    elif args.command == 'render':
        input_frame = Image.open(args.infile)
        (width, height) = input_frame.size

        host = ofx_host()
        if host.load_ofx_binary(args.dir, args.bundle) == OFX_STATUS_OK:
            status = host.plugin_load_and_describe(args.bundle, args.plugin)
            (active_uid, status) = host.create_plugin_instance(args.bundle, args.plugin, width, height)
            if args.json is not None:
                status = host.load_plugin_parameters(active_uid, args.json)
            status = host.begin_render_sequence(active_uid)
            status = host.connect_image(active_uid, 'Source', args.infile, width, height)
            status = host.connect_buffer(active_uid, 'Output', width, height)
            status = host.render(active_uid, width, height)
            status = host.save_image(active_uid, 'Output', args.outfile, width, height)
            status = host.disconnect_image(active_uid, 'Source')
            status = host.disconnect_buffer(active_uid, 'Output')
            status = host.end_render_sequence(active_uid)
            status = host.destroy_plugin_instance(active_uid)
            status = host.unload_plugin(args.bundle, args.plugin)

