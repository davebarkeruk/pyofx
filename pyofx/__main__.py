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
    if x.rsplit('.', 1)[1] not in ['png', 'PNG', 'jpg', 'JPG']:
        raise argparse.ArgumentTypeError("Filetype needs to be PNG or JPG")
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple command line OFX plugin processor.')
    subparsers = parser.add_subparsers(dest='subparser_name')

    list_subparser = subparsers.add_parser('list', help='List all the plugins in the OFX bundle.')
    list_subparser.add_argument('ofx_directory', type=extant_dir,
                       help='Path of the ofx directory.')
    list_subparser.add_argument('bundle', type=str,
                   help='Name of the ofx bundle.')

    render_subparser = subparsers.add_parser('render', help='Render OFX bundle.')
    render_subparser.add_argument('ofx_directory', type=extant_dir,
                   help='Path of the ofx directory.')
    render_subparser.add_argument('bundle',
                   help='Name of the ofx bundle.')
    render_subparser.add_argument('plugin',
                   help='Name of plugin to use.')
    render_subparser.add_argument('input_image', type=extant_file,
                   help='Filename of input image.')
    render_subparser.add_argument('output_image', type=valid_filetype,
                   help='Filename of output image.')

    args = parser.parse_args()

    if args.subparser_name == 'list':
        host = ofx_host()
        if host.load_ofx_lib(args.ofx_directory, args.bundle) == OFX_STATUS_OK:
            host.list_all_plugins()
    elif args.subparser_name == 'render':
        input_frame = Image.open(args.input_image)
        (width, height) = input_frame.size

        host = ofx_host()
        if host.load_ofx_lib(args.ofx_directory, args.bundle) == OFX_STATUS_OK:
            status = host.plugin_load_and_describe(args.plugin)
            (instance_id, status) = host.create_plugin_instance(args.plugin, width, height)
            status = host.render(args.plugin, instance_id, args.input_image, args.output_image, width, height)
            status = host.destroy_plugin_instance(args.plugin, instance_id)
            status = host.unload_plugin(args.plugin)

