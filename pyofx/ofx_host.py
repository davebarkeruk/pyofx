#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import platform
import os
import json
import uuid
import logging
import PIL.Image
import PIL.ImageOps
import numpy

import ofx_ctypes
import ofx_property_suite
import ofx_parameter_suite
import ofx_image_effect_suite
import ofx_memory_suite
import ofx_multi_thread_suite
import ofx_message_suite
import ofx_property_sets
import ofx_status_codes

class OfxHost():
    def __init__(self):
        host_handle = ofx_ctypes.CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeImageEffectHost'),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b'pyofx')
        )

        fetch_suite_func = ofx_ctypes.cfunc_fetch_suite(self._fetch_suite)
        host_struct = ofx_ctypes.CStructOfxHost(ctypes.pointer(host_handle), fetch_suite_func)

        self._host = {
            'handle':         host_handle,
            'fetchSuiteFunc': fetch_suite_func,
            'hostStruct':     host_struct,
            'bundles':        {},
            'active':         {'plugins':{}, 'memory':{}},
            'ctypes':         ofx_property_sets.OfxHostProperties()
        }

        self._property_suite = ofx_property_suite.OfxPropertySuite(self._host)
        self._parameter_suite = ofx_parameter_suite.OfxParameterSuite(self._host)
        self._image_effect_suite = ofx_image_effect_suite.OfxImageEffectSuite(self._host)
        self._memory_suite = ofx_memory_suite.OfxMemorySuite(self._host)
        self._multi_thread_suite = ofx_multi_thread_suite.OfxMultiThreadSuite()
        self._message_suite = ofx_message_suite.OfxMessageSuite()

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
            logging.warning('{} is not supported by host'.format(requested_suite))
            return 0

    def _list_all_plugins(self, bundle):
        for p in self._host['bundles'][bundle]['plugins']:
            print(p)

    def _list_plugin_parameters(self, bundle, plugin_id, context):
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
        return ofx_status_codes.OFX_STATUS_OK

    def _save_plugin_parameters(self, bundle, plugin_id, context, json_filename):
        plugin_variables = {
            'bundle': bundle,
            'plugin': plugin_id,
            'context': context,
            'parameters': {},
            'frame_size': {
                'width': 1280,
                'height': 720
            },
            'image_paths': {
                'required': {},
                'optional': {}
            } 
        }

        params = self._host['bundles'][bundle]['plugins'][plugin_id]['contexts'][context]['parameters']
        clips = self._host['bundles'][bundle]['plugins'][plugin_id]['contexts'][context]['clips']

        for key in params:
            p = params[key]['ctypes'].as_tuple()
            if p[0] is not None:
                plugin_variables['parameters'][p[0]] = p[1]

        for key in clips:
            is_optional = clips[key]['ctypes'].get('OfxImageClipPropOptional').value
            if is_optional == 1:
                plugin_variables['image_paths']['optional'][key] = None
            else:
                plugin_variables['image_paths']['required'][key] = None

        with open(json_filename, 'w') as fp:
            json.dump(plugin_variables, fp, indent=4)

        return ofx_status_codes.OFX_STATUS_OK

    def _load_plugin_parameters(self, active_uid, update_params):
        current_params = self._host['active']['plugins'][active_uid]['parameters']

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

        return ofx_status_codes.OFX_STATUS_OK

    def _generate_ofx_binary_filename(self, ofx_dir, bundle):
        bundle_dir = os.path.join(ofx_dir, bundle + '.ofx.bundle')
        if platform.system() == 'Linux':
            return os.path.join(bundle_dir, 'Contents', 'Linux-x86-64', bundle + '.ofx')
        elif platform.system() == 'Windows':
            return os.path.join(bundle_dir, 'Contents', 'Win64', bundle + '.ofx')
        elif platform.system() == 'Darwin':
            return os.path.join(bundle_dir, 'Contents', 'MacOS-x86-64', bundle + '.ofx')
        else:
            logging.error('Cannot determin the system')
            return None

    def _load_ofx_binary(self, ofx_dir, bundle):
        filename = self._generate_ofx_binary_filename(ofx_dir, bundle)
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
            plugin_info = ofx_ctypes.CStructOfxPlugin.from_address(get_plugin(n))

            set_host_func = ofx_ctypes.cfunc_set_host(plugin_info.setHost)
            set_host_func(ctypes.pointer(self._host['hostStruct']))

            plugin_id = plugin_info.pluginIdentifier.decode("utf-8")
            effect_handle = ofx_ctypes.CStructOfxHandle(
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
                'ctypes':             ofx_property_sets.OfxEffectProperties(plugin_id)
            }

        return ofx_status_codes.OFX_STATUS_OK

    def _plugin_load_and_describe(self, bundle, plugin_id):
        plugin = self._host['bundles'][bundle]['plugins'][plugin_id]

        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

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
                context_handle = ofx_ctypes.CStructOfxHandle(
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
                    'ctypes':           ofx_property_sets.OfxEffectContextProperties(context_string)
                }

                plugin['contexts'][context_string] = context_descriptor

                entry_point(
                    ctypes.c_char_p(b'OfxImageEffectActionDescribeInContext'),
                    ctypes.pointer(context_handle),
                    ctypes.pointer(context_handle),
                    0
                )

        return ofx_status_codes.OFX_STATUS_OK

    def _create_plugin_instance(self, bundle_id, plugin_id, context, width, height):
        plugin = self._host['bundles'][bundle_id]['plugins'][plugin_id]
        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

        active_uid = str(uuid.uuid1())

        effect_handle = ofx_ctypes.CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeImageEffectInstance'),
            ctypes.c_char_p(bundle_id.encode('utf-8')),
            ctypes.c_char_p(plugin_id.encode('utf-8')),
            ctypes.c_char_p(context.encode('utf-8')),
            ctypes.c_char_p(active_uid.encode('utf-8')),
            ctypes.c_char_p(active_uid.encode('utf-8'))
        )

        clips = {}
        parameters = {}

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
            'ctypes':     ofx_property_sets.OfxEffectInstanceProperties(context, width, height)
        }

        self._host['active']['plugins'][active_uid] = active_plugin

        entry_point(
            ctypes.c_char_p(b'OfxActionCreateInstance'),
            ctypes.pointer(self._host['active']['plugins'][active_uid]['handle']),
            0,
            0
        )

        return active_uid

    def _connect_image(self, active_uid, clip_name, filename, width, height):
        im_frame = PIL.ImageOps.flip(PIL.Image.open(filename))
        im_frame = im_frame.convert('RGBA')
        im_frame = im_frame.resize((width, height), PIL.Image.ANTIALIAS)
        np_frame = numpy.ascontiguousarray(numpy.array(im_frame.getdata()), dtype=numpy.uint8)
        frame_ptr = np_frame.ctypes.data_as(ctypes.c_void_p).value

        image_handle = ofx_ctypes.CStructOfxHandle(
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
            'ctypes':      ofx_property_sets.OfxImageProperties('source', frame_ptr, width, height)
        }

        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]
        clip['image'] = image_props
        clip['ctypes'].update('OfxImageClipPropConnected', 1, 'int')

        return ofx_status_codes.OFX_STATUS_OK

    def _connect_buffer(self, active_uid, clip_name, width, height):
        buffer = numpy.ascontiguousarray(numpy.zeros(width*height*4, numpy.uint8), dtype=numpy.uint8)
        buffer_ptr = buffer.ctypes.data_as(ctypes.c_void_p).value

        buffer_handle = ofx_ctypes.CStructOfxHandle(
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
            'ctypes':      ofx_property_sets.OfxImageProperties('output', buffer_ptr, width, height)
        }

        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]
        clip['image'] = buffer_props
        clip['ctypes'].update('OfxImageClipPropConnected', 1, 'int')

        return ofx_status_codes.OFX_STATUS_OK

    def _disconnect_image(self, active_uid, clip_name):
        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]
        clip['image'] = {}
        clip['ctypes'].update('OfxImageClipPropConnected', 0, 'int')

        return  ofx_status_codes.OFX_STATUS_OK

    def _disconnect_buffer(self, active_uid, clip_name):
        return self._disconnect_image(active_uid, clip_name)

    def _save_image(self, active_uid, clip_name, filename, width, height):
        clip = self._host['active']['plugins'][active_uid]['clips'][clip_name]

        if clip['ctypes'].get('OfxImageClipPropConnected').value == 0:
            return ofx_status_codes.OFX_STATUS_FAILED

        ptr = clip['image']['ctypes'].get('OfxImagePropData').value
        np_array = numpy.ctypeslib.as_array(ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte)), (height,width,4))
        im = PIL.ImageOps.flip(PIL.Image.fromarray(np_array))
        if filename.rsplit('.', 1)[1].lower() in ['jpg']:
            im = im.convert('RGB')
        im.save(filename)

        return ofx_status_codes.OFX_STATUS_OK

    def _begin_render_sequence(self, active_uid):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

        sequence_render_handle = ofx_ctypes.CStructOfxHandle(
            ctypes.c_char_p(b'OfxSequenceRenderAction'),
            self._host['active']['plugins'][active_uid]['handle'].bundle,
            self._host['active']['plugins'][active_uid]['handle'].plugin,
            self._host['active']['plugins'][active_uid]['handle'].context,
            self._host['active']['plugins'][active_uid]['handle'].active_uid,
            ctypes.c_char_p(b'render_sequence')
        )

        sequence_render_props = {
            'handle': sequence_render_handle,
            'ctypes': ofx_property_sets.OfxSequenceRenderActionProperties()
        }

        plugin['render']['sequence'] = sequence_render_props

        entry_point(
            ctypes.c_char_p(b'OfxImageEffectActionBeginSequenceRender'),
            ctypes.pointer(plugin['handle']),
            ctypes.pointer(sequence_render_handle),
            0
        )

        return ofx_status_codes.OFX_STATUS_OK

    def _render(self, active_uid, width, height):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

        render_handle = ofx_ctypes.CStructOfxHandle(
            ctypes.c_char_p(b'OfxRenderAction'),
            self._host['active']['plugins'][active_uid]['handle'].bundle,
            self._host['active']['plugins'][active_uid]['handle'].plugin,
            self._host['active']['plugins'][active_uid]['handle'].context,
            self._host['active']['plugins'][active_uid]['handle'].active_uid,
            ctypes.c_char_p(b'render_action')
        )

        render_props = {
            'handle': render_handle,
            'ctypes': ofx_property_sets.OfxRenderActionProperties(width, height)
        }

        plugin['render']['action'] = render_props

        entry_point(
            ctypes.c_char_p(b'OfxImageEffectActionRender'),
            ctypes.pointer(self._host['active']['plugins'][active_uid]['handle']),
            ctypes.pointer(render_handle),
            0
        )

        plugin['render']['action'] = None

        return ofx_status_codes.OFX_STATUS_OK

    def _end_render_sequence(self, active_uid):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxImageEffectActionEndSequenceRender'),
            ctypes.pointer(plugin['handle']),
            ctypes.pointer(plugin['render']['sequence']['handle']),
            0
        )

        plugin['render']['sequence'] = None

        return ofx_status_codes.OFX_STATUS_OK

    def _destroy_plugin_instance(self, active_uid):
        plugin = self._host['active']['plugins'][active_uid]

        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxActionDestroyInstance'),
            ctypes.pointer(self._host['active']['plugins'][active_uid]['handle']),
            0,
            0
        )

        del(self._host['active']['plugins'][active_uid])

        return ofx_status_codes.OFX_STATUS_OK

    def _unload_plugin(self, bundle, plugin_id):
        plugin = self._host['bundles'][bundle]['plugins'][plugin_id]
        entry_point = ofx_ctypes.cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(
            ctypes.c_char_p(b'OfxActionUnload'),
            0,
            0,
            0
        )

        return ofx_status_codes.OFX_STATUS_OK

    def display_plugins(self, directory, bundle):
        self._load_ofx_binary(directory, bundle)
        self._list_all_plugins(bundle)

    def display_params(self, directory, bundle, plugin):
        context = 'OfxImageEffectContextGeneral'
        self._load_ofx_binary(directory, bundle)
        self._plugin_load_and_describe(bundle, plugin)
        self._list_plugin_parameters(bundle, plugin, context)

    def params_to_json(self, directory, bundle, plugin, json_file):
        context = 'OfxImageEffectContextGeneral'
        self._load_ofx_binary(directory, bundle)
        self._plugin_load_and_describe(bundle, plugin)
        self._save_plugin_parameters(bundle, plugin, context, json_file)

    def filter_render(self, directory, bundle, plugin, infile, outfile):
        context = 'OfxImageEffectContextFilter'

        input_frame = PIL.Image.open(infile)
        (width, height) = input_frame.size

        self._load_ofx_binary(directory, bundle)
        self._plugin_load_and_describe(bundle, plugin)
        active_uid = self._create_plugin_instance(bundle, plugin, context, width, height)
        self._begin_render_sequence(active_uid)
        self._connect_image(active_uid, 'Source', infile, width, height)
        self._connect_buffer(active_uid, 'Output', width, height)
        self._render(active_uid, width, height)
        self._save_image(active_uid, 'Output', outfile, width, height)
        self._disconnect_image(active_uid, 'Source')
        self._disconnect_buffer(active_uid, 'Output')
        self._end_render_sequence(active_uid)
        self._destroy_plugin_instance(active_uid)
        self._unload_plugin(bundle, plugin)

    def json_render(self, directory, json_file):
        with open(json_file, 'r') as fp:
            settings = json.load(fp)

        for i in settings['image_paths']['required']:
            if settings['image_paths']['required'][i] is None:
                logging.critical('Required image path for \'{}\' is not set in JSON file'.format(i))
                exit()

        width = settings['frame_size']['width']
        height = settings['frame_size']['height']

        self._load_ofx_binary(directory, settings['bundle'])
        self._plugin_load_and_describe(settings['bundle'], settings['plugin'])
        active_uid = self._create_plugin_instance(settings['bundle'], settings['plugin'], settings['context'], width, height)
        self._load_plugin_parameters(active_uid, settings['parameters'])
        self._begin_render_sequence(active_uid)

        for i in settings['image_paths']['required']:
            if i == 'Output':
                self._connect_buffer(active_uid, 'Output', width, height)
            else:
                self._connect_image(active_uid, i, settings['image_paths']['required'][i], width, height)

        for i in settings['image_paths']['optional']:
            if settings['image_paths']['optional'][i] is not None:
                self._connect_image(active_uid, i, settings['image_paths']['optional'][i], width, height)

        self._render(active_uid, width, height)

        self._save_image(active_uid, 'Output', settings['image_paths']['required']['Output'], width, height)

        for i in settings['image_paths']['required']:
            if i == 'Output':
                self._disconnect_buffer(active_uid, i)
            else:
                self._disconnect_image(active_uid, i)

        for i in settings['image_paths']['optional']:
            if settings['image_paths']['optional'][i] is not None:
                self._disconnect_image(active_uid, i)

        self._end_render_sequence(active_uid)
        self._destroy_plugin_instance(active_uid)
        self._unload_plugin(settings['bundle'], settings['plugin'])



