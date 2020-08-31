#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import traceback
import ctypes
import copy
import platform
import os
import json
import uuid
from ofx_ctypes import *
from ofx_property_suite import *
from ofx_parameter_suite import *
from ofx_image_effect_suite import *
from ofx_memory_suite import *
from ofx_multi_thread_suite import *
from ofx_message_suite import *
from ofx_property_sets import *
from ofx_status_codes import *
from PIL import Image, ImageOps
import numpy as np

class ofx_host():
    def __init__(self):
        host_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeImageEffectHost'),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b'pyofx')
        )

        fetch_suite_func = cfunc_fetch_suite(self._fetch_suite)
        host_struct = CStructOfxHost(ctypes.pointer(host_handle), fetch_suite_func)

        self._host = {
            'handle':         host_handle,
            'fetchSuiteFunc': fetch_suite_func,
            'hostStruct':     host_struct,
            'bundles':        {},
            'active':         {'plugins':{}, 'memory':{}},
            'ctypes':         OfxHostProperties()
        }

        self._property_suite = OfxPropertySuite(self._host)
        self._parameter_suite = OfxParameterSuite(self._host)
        self._image_effect_suite = OfxImageEffectSuite(self._host)
        self._memory_suite = OfxMemorySuite(self._host)
        self._multi_thread_suite = OfxMultiThreadSuite()
        self._message_suite = OfxMessageSuite()

    def _fetch_suite(self, ctype_handle, ctype_name, ctype_version):
        requested_suite = ctype_name.decode("utf-8")

        if requested_suite == 'OfxImageEffectSuite':
            return self._image_effect_suite.get_pointer_as_int()
        elif requested_suite == 'OfxPropertySuite':
            return self._property_suite.get_pointer_as_int()
        elif requested_suite == 'OfxParameterSuite':
            return self._parameter_suite.get_pointer_as_int()
        elif requested_suite == 'OfxMemorySuite':
            return self._memory_suite.get_pointer_as_int()
        elif requested_suite == 'OfxMultiThreadSuite':
            return self._multi_thread_suite.get_pointer_as_int()
        elif requested_suite == 'OfxMessageSuite':
            return self._message_suite.get_pointer_as_int()
        else:
            print('WARNING: {} is not supported by host'.format(requested_suite))
            return 0

    def list_all_plugins(self, bundle):
        for p in self._host['bundles'][bundle]['plugins']:
            print(p)

    def list_plugin_parameters(self, bundle, plugin_id, context='OfxImageEffectContextFilter'):
        print('\n')
        print('Plugin Name')
        print('===========\n')
        print('{}\n'.format(plugin_id))
        print('Parameters')
        print('==========\n')
        params = self._host['bundles'][bundle]['plugins'][plugin_id]['contexts'][context]['parameters']
        for key in params:
            param_string = params[key]['ctypes'].brief_details()
            if param_string is not None:
                print(param_string)
        print()
        print('Clips')
        print('=====\n')
        clips = self._host['bundles'][bundle]['plugins'][plugin_id]['contexts'][context]['clips']
        for key in clips:
            clip_string = clips[key]['ctypes'].brief_details()
            if clip_string is not None:
                print(clip_string)

        print('\n')
        return OFX_STATUS_OK

    def save_plugin_parameters(self, bundle, plugin_id, json_filename, context='OfxImageEffectContextFilter'):
        params = self._host['bundles'][bundle]['plugins'][plugin_id]['contexts'][context]['parameters']
        active_params = {}
        for key in params:
            p = params[key]['ctypes'].as_tuple()
            if p[0] is not None:
                active_params[p[0]] = p[1]

        with open(json_filename, 'w') as fp:
            json.dump(active_params, fp, indent=4)

        return OFX_STATUS_OK

    def load_plugin_parameters(self, active_uid, json_filename):
        current_params = self._host['active']['plugins'][active_uid]['parameters']

        with open(json_filename, 'r') as fp:
            update_params = json.load(fp)

        for p in update_params:
            for cp in current_params:
                script_name = current_params[cp]['ctypes'].value_as_string('OfxParamPropScriptName')
                if script_name == p:
                    param_type = current_params[cp]['ctypes'].value_as_string('OfxParamPropType')
                    if param_type == 'OfxParamTypeInteger':
                        current_params[cp]['value'] = [ctypes.c_int(update_params[p])]
                    elif param_type == 'OfxParamTypeDouble':
                        current_params[cp]['value'] = [ctypes.c_double(update_params[p])]
                    elif param_type == 'OfxParamTypeBoolean':
                        current_params[cp]['value'] = [ctypes.c_int(update_params[p])]
                    elif param_type == 'OfxParamTypeChoice':
                        current_params[cp]['value'] = [ctypes.c_int(update_params[p])]
                    elif param_type == 'OfxParamTypeRGBA':
                        current_params[cp]['value'] = [ctypes.c_double(d) for d in update_params[p]]
                    elif param_type == 'OfxParamTypeRGB':
                        current_params[cp]['value'] = [ctypes.c_double(d) for d in update_params[p]]
                    elif param_type == 'OfxParamTypeDouble2D':
                        current_params[cp]['value'] = [ctypes.c_double(d) for d in update_params[p]]
                    elif param_type == 'OfxParamTypeInteger2D':
                        current_params[cp]['value'] = [ctypes.c_int(i) for i in update_params[p]]
                    elif param_type == 'OfxParamTypeDouble3D':
                        current_params[cp]['value'] = [ctypes.c_double(d) for d in update_params[p]]
                    elif param_type == 'OfxParamTypeInteger3D':
                        current_params[cp]['value'] = [ctypes.c_int(i) for i in update_params[p]]
                    elif param_type == 'OfxParamTypeString':
                        current_params[cp]['value'] = [ctypes.create_string_buffer(update_params[p].encode('utf-8'))]

        return OFX_STATUS_OK

    def load_ofx_binary(self, ofx_dir, bundle):
        bundle_dir = os.path.join(ofx_dir, bundle + '.ofx.bundle')
        if platform.system() == 'Linux':
            filename = os.path.join(bundle_dir, 'Contents', 'Linux-x86-64', bundle + '.ofx')
        elif platform.system() == 'Windows':
            filename = os.path.join(bundle_dir, 'Contents', 'Win64', bundle + '.ofx')
        elif platform.system() == 'Darwin':
            filename = os.path.join(bundle_dir, 'Contents', 'MacOS-x86-64', bundle + '.ofx')
        else:
            print('ERROR: Cannot determin the system')
            return OFX_STATUS_FAILED
 
        plugin_lib = ctypes.CDLL(filename)
        plugin_count = plugin_lib.OfxGetNumberOfPlugins()
        self._host['bundles'][bundle] = {
            'cdll':          plugin_lib,
            'filename':      filename,
            'plugins_count': plugin_count,
            'plugins':       {}
        }

        get_plugin = plugin_lib.OfxGetPlugin
        get_plugin.restype = ctypes.c_void_p
        for n in range(0, plugin_count):
            plugin_info = CStructOfxPlugin.from_address(get_plugin(n))

            set_host_func = cfunc_set_host(plugin_info.setHost)
            set_host_func(self._host['hostStruct'])

            plugin_id = plugin_info.pluginIdentifier.decode("utf-8")
            effect_handle = CStructOfxHandle(
                ctypes.c_char_p(b"OfxTypeImageEffect"),
                ctypes.c_char_p(bundle.encode('utf-8')),
                ctypes.c_char_p(plugin_id.encode('utf-8')),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(plugin_id.encode('utf-8'))
            )

            self._host['bundles'][bundle]['plugins'][plugin_id] = {
                'handle':             effect_handle,
                'pluginApi':          plugin_info.pluginApi.decode("utf-8"),
                'apiVersion':         plugin_info.apiVersion,
                'pluginVersionMajor': plugin_info.pluginVersionMajor,
                'pluginVersionMinor': plugin_info.pluginVersionMinor,
                'setHost':            plugin_info.setHost,
                'mainEntry':          plugin_info.mainEntry,
                'contexts':           {},
                'ctypes':             OfxEffectProperties(plugin_id)
            }

        return OFX_STATUS_OK

    def _add_active_plugin(self, bundle_id, plugin_id, context, width, height):
        active_uid = str(uuid.uuid1())

        effect_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeImageEffectInstance'),
            ctypes.c_char_p(bundle_id.encode('utf-8')),
            ctypes.c_char_p(plugin_id.encode('utf-8')),
            ctypes.c_char_p(context.encode('utf-8')),
            ctypes.c_char_p(active_uid.encode('utf-8')),
            ctypes.c_char_p(active_uid.encode('utf-8'))
        )

        clips = {}
        parameters = {}
        plugin = self._host['bundles'][bundle_id]['plugins'][plugin_id]

        for key in plugin['contexts'][context]['clips']:
            descriptor = plugin['contexts'][context]['clips'][key]
            clips[key] = self._image_effect_suite.create_clip_instance(descriptor, active_uid)
            clips[key]['ctypes'].add_instance_properties()

        for key in plugin['contexts'][context]['parameters']:
            descriptor = plugin['contexts'][context]['parameters'][key]
            parameters[key] = self._parameter_suite.create_parameter_instance(descriptor, active_uid)

        active_plugin = {
            'handle':     effect_handle,
            'mainEntry':  plugin['mainEntry'],
            'plugin':     plugin_id,
            'context':    context,
            'clips':      clips,
            'parameters': parameters,
            'render':     {'sequence': None, 'action':None},
            'ctypes':     OfxEffectInstanceProperties(context, width, height)
        }

        self._host['active']['plugins'][active_uid] = active_plugin
        return active_uid

    def plugin_load_and_describe(self, bundle, plugin_id):
        plugin = self._host['bundles'][bundle]['plugins'][plugin_id]

        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxActionLoad'),
            0,
            0,
            0
        )

        entry_point(
            ctypes.c_char_p(b'OfxActionDescribe'),
            ctypes.pointer(plugin['handle']),
            0,
            0
        )

        for context in self._host['ctypes'].get('OfxImageEffectPropSupportedContexts'):
            context_string = ctypes.cast(context, ctypes.c_char_p).value.decode('utf-8')
            plugin_contexts = [
                ctypes.cast(i, ctypes.c_char_p).value.decode('utf-8')
                for i in plugin['ctypes'].get('OfxImageEffectPropSupportedContexts')
            ]

            if context_string in plugin_contexts:
                context_id = '{}.{}'.format(plugin_id, context_string)

                context_handle = CStructOfxHandle(
                    ctypes.c_char_p(b'OfxImageEffectPropContext'),
                    plugin['handle'].bundle,
                    plugin['handle'].plugin,
                    ctypes.c_char_p(context_string.encode('utf-8')),
                    ctypes.c_char_p(b''),
                    ctypes.c_char_p(context_string.encode('utf-8'))
                )

                context_descriptor = {
                    'handle':           context_handle,
                    'clips':            {},
                    'parameters':       {},
                    'pluginIdentifier': plugin_id,
                    'ctypes':           OfxEffectContextProperties(context_string)
                }

                plugin['contexts'][context_string] = context_descriptor

                entry_point(
                    ctypes.c_char_p(b'OfxImageEffectActionDescribeInContext'),
                    ctypes.pointer(context_handle),
                    ctypes.pointer(context_handle),
                    0
                )

        return OFX_STATUS_OK

    def create_plugin_instance(self, bundle, plugin_id, width, height):
        plugin = self._host['bundles'][bundle]['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        active_uid = self._add_active_plugin(bundle, plugin_id, 'OfxImageEffectContextFilter', width, height)

        entry_point(
            ctypes.c_char_p(b'OfxActionCreateInstance'),
            ctypes.pointer(self._host['active']['plugins'][active_uid]['handle']),
            0,
            0
        )

        return(active_uid, OFX_STATUS_OK)

    def connect_image(self, active_uid, clip_name, filename, width, height):
        im_frame = ImageOps.flip(Image.open(filename))
        im_frame = im_frame.convert('RGBA')
        im_frame = im_frame.resize((width, height), Image.ANTIALIAS)
        np_frame = np.ascontiguousarray(np.array(im_frame.getdata()), dtype=np.uint8)
        frame_ptr = np_frame.ctypes.data_as(ctypes.c_void_p).value

        image_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxImage'),
            self._host['active']['plugins'][active_uid]['handle'].bundle,
            self._host['active']['plugins'][active_uid]['handle'].plugin,
            self._host['active']['plugins'][active_uid]['handle'].context,
            self._host['active']['plugins'][active_uid]['handle'].active_uid,
            ctypes.c_char_p(clip_name.encode('utf-8'))
        )

        image_props = {
            'handle':      image_handle,
            'numpy_array': np_frame,
            'ctypes':      OfxImageProperties('source', frame_ptr, width, height)
        }

        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]
        clip['image'] = image_props
        clip['ctypes'].update('OfxImageClipPropConnected', 1, 'int')

        return  OFX_STATUS_OK

    def connect_buffer(self, active_uid, clip_name, width, height):
        buffer = np.ascontiguousarray(np.zeros(width*height*4, np.uint8), dtype=np.uint8)
        buffer_ptr = buffer.ctypes.data_as(ctypes.c_void_p).value

        buffer_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxImage'),
            self._host['active']['plugins'][active_uid]['handle'].bundle,
            self._host['active']['plugins'][active_uid]['handle'].plugin,
            self._host['active']['plugins'][active_uid]['handle'].context,
            self._host['active']['plugins'][active_uid]['handle'].active_uid,
            ctypes.c_char_p(clip_name.encode('utf-8'))
        )

        buffer_props = {
            'handle':      buffer_handle,
            'numpy_array': buffer,
            'ctypes':      OfxImageProperties('output', buffer_ptr, width, height)
        }

        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]
        clip['image'] = buffer_props
        clip['ctypes'].update('OfxImageClipPropConnected', 1, 'int')

        return OFX_STATUS_OK

    def disconnect_image(self, active_uid, clip_name):
        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]
        clip['image'] = {}
        clip['ctypes'].update('OfxImageClipPropConnected', 0, 'int')

        return  OFX_STATUS_OK

    def disconnect_buffer(self, active_uid, clip_name):
        return self.disconnect_image(active_uid, clip_name)

    def save_image(self, active_uid, clip_name, filename, width, height):
        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]

        if clip['ctypes'].get('OfxImageClipPropConnected').value == 0:
            return OFX_STATUS_FAILED

        ptr = clip['image']['ctypes'].get('OfxImagePropData').value
        np_array = np.ctypeslib.as_array(ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte)), (height,width,4))
        im = ImageOps.flip(Image.fromarray(np_array))
        if filename.rsplit('.', 1)[1].lower() in ['jpg']:
            im = im.convert('RGB')
        im.save(filename)

        return OFX_STATUS_OK

    def begin_render_sequence(self, active_uid):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        sequence_render_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxSequenceRenderAction'),
            self._host['active']['plugins'][active_uid]['handle'].bundle,
            self._host['active']['plugins'][active_uid]['handle'].plugin,
            self._host['active']['plugins'][active_uid]['handle'].context,
            self._host['active']['plugins'][active_uid]['handle'].active_uid,
            ctypes.c_char_p(b'render_sequence')
        )

        sequence_render_props = {
            'handle': sequence_render_handle,
            'ctypes': OfxSequenceRenderActionProperties()
        }

        plugin['render']['sequence'] = sequence_render_props

        entry_point(
            ctypes.c_char_p(b'OfxImageEffectActionBeginSequenceRender'),
            ctypes.pointer(plugin['handle']),
            ctypes.pointer(sequence_render_handle),
            0
        )

        return OFX_STATUS_OK

    def render(self, active_uid, width, height):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        render_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxRenderAction'),
            self._host['active']['plugins'][active_uid]['handle'].bundle,
            self._host['active']['plugins'][active_uid]['handle'].plugin,
            self._host['active']['plugins'][active_uid]['handle'].context,
            self._host['active']['plugins'][active_uid]['handle'].active_uid,
            ctypes.c_char_p(b'render_action')
        )

        render_props = {
            'handle': render_handle,
            'ctypes': OfxRenderActionProperties(width, height)
        }

        plugin['render']['action'] = render_props

        entry_point(
            ctypes.c_char_p(b'OfxImageEffectActionRender'),
            ctypes.pointer(self._host['active']['plugins'][active_uid]['handle']),
            ctypes.pointer(render_handle),
            0
        )

        plugin['render']['action'] = None

        return OFX_STATUS_OK

    def end_render_sequence(self, active_uid):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxImageEffectActionEndSequenceRender'),
            ctypes.pointer(plugin['handle']),
            ctypes.pointer(plugin['render']['sequence']['handle']),
            0
        )

        plugin['render']['sequence'] = None

        return OFX_STATUS_OK

    def destroy_plugin_instance(self, active_uid):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxActionDestroyInstance'),
            ctypes.pointer(self._host['active']['plugins'][active_uid]['handle']),
            0,
            0
        )

        del(self._host['active']['plugins'][active_uid])

        return OFX_STATUS_OK

    def unload_plugin(self, bundle, plugin_id):
        plugin = self._host['bundles'][bundle]['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxActionUnload'),
            0,
            0,
            0
        )

        return OFX_STATUS_OK



