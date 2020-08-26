#! /usr/bin/python3

import traceback
import ctypes
import copy
import platform
import os
from ofx_ctypes import *
from ofx_property_suite import *
from ofx_parameter_suite import *
from ofx_image_effect_suite import *
from ofx_property_sets import *
from ofx_status_codes import *
from PIL import Image, ImageOps
import numpy as np

class ofx_host():
    def __init__(self):
        host_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxTypeImageEffectHost'),
                                       ctypes.c_char_p(b'pyOfx'))

        fetch_suite_func = cfunc_fetch_suite(self._fetch_suite)
        host_struct = CStructOfxHost(ctypes.pointer(host_handle), fetch_suite_func)

        self._host = {'handle':           host_handle,
                      'fetchSuiteFunc':   fetch_suite_func,
                      'hostStruct':       host_struct,
                      'libs':             [],
                      'plugins':          {},
                      'active_plugins':   {},
                      'render_sequences': {},
                      'render_actions':   {},
                      'images':           {},
                      'memory':           {},
                      'ctypes':           OfxHostProperties()}

        self._property_suite = OfxPropertySuite(self._host)
        self._parameter_suite = OfxParameterSuite(self._host)
        self._image_effect_suite = OfxImageEffectSuite(self._host)

    def _fetch_suite(self, ctype_handle, ctype_name, ctype_version):
        requested_suite = ctype_name.decode("utf-8")

        if requested_suite == 'OfxImageEffectSuite':
            return self._image_effect_suite.get_pointer_as_int()
        elif requested_suite == 'OfxPropertySuite':
            return self._property_suite.get_pointer_as_int()
        elif requested_suite == 'OfxParameterSuite':
            return self._parameter_suite.get_pointer_as_int()
        else:
            print('WARNING: {} is not supported by host'.format(requested_suite))
            return OFX_STATUS_ERR_MISSING_HOST_FEATURE

    def list_all_plugins(self):
        for p in self._host['plugins']:
            print( ctypes.cast(self._host['plugins'][p]['handle'].id, ctypes.c_char_p).value.decode('utf-8'))

    def load_ofx_lib(self, ofx_dir, bundle):
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
        self._host['libs'].append({'cdll': plugin_lib,
                                   'filename': filename,
                                   'plugins_count': plugin_count})

        get_plugin = plugin_lib.OfxGetPlugin
        get_plugin.restype = ctypes.c_void_p
        for n in range(0, plugin_count):
            plugin_info = CStructOfxPlugin.from_address(get_plugin(n))

            set_host_func = cfunc_set_host(plugin_info.setHost)
            set_host_func(self._host['hostStruct'])

            plugin_id = plugin_info.pluginIdentifier.decode("utf-8")
            effect_handle = CStructOfxHandle(ctypes.c_char_p(b"OfxTypeImageEffect"),
                                             ctypes.c_char_p(plugin_id.encode('utf-8')))

            self._host['plugins'][plugin_id] = {'handle':             effect_handle,
                                                'pluginApi':          plugin_info.pluginApi.decode("utf-8"),
                                                'apiVersion':         plugin_info.apiVersion,
                                                'pluginVersionMajor': plugin_info.pluginVersionMajor,
                                                'pluginVersionMinor': plugin_info.pluginVersionMinor,
                                                'setHost':            plugin_info.setHost,
                                                'mainEntry':          plugin_info.mainEntry,
                                                'contexts':           {},
                                                'ctypes':             OfxEffectProperties(plugin_id)}

        return OFX_STATUS_OK

    def _add_active_plugin(self, plugin_id, context, width, height):
        active_id = ('fx_%05d'%(len(self._host['active_plugins'])))

        effect_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxTypeImageEffectInstance'),
                                         ctypes.c_char_p(active_id.encode('utf-8')))

        clips = {}
        parameters = {}

        for key in self._host['plugins'][plugin_id]['contexts'][context]['clips']:
            descriptor = self._host['plugins'][plugin_id]['contexts'][context]['clips'][key]
            clips[key] = self._image_effect_suite.create_clip_instance(descriptor, active_id)
            clips[key]['ctypes'].add_instance_properties()

        for key in self._host['plugins'][plugin_id]['contexts'][context]['parameters']:
            descriptor = self._host['plugins'][plugin_id]['contexts'][context]['parameters'][key]
            parameters[key] = self._parameter_suite.create_parameter_instance(descriptor, active_id)

        active_plugin = {'handle':     effect_handle,
                         'plugin':     plugin_id,
                         'context':    context,
                         'clips':      clips,
                         'parameters': parameters,
                         'ctypes':     OfxEffectInstanceProperties(context, width, height)}

        self._host['active_plugins'][active_id] = active_plugin
        return active_id

    def plugin_load_and_describe(self, plugin_id):
        plugin = self._host['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        print('=== OfxActionLoad')

        entry_point(ctypes.c_char_p(b'OfxActionLoad'),
                    0,
                    0,
                    0)

        print('=== OfxActionDescribe')

        entry_point(ctypes.c_char_p(b'OfxActionDescribe'),
                    ctypes.pointer(plugin['handle']),
                    0,
                    0)

        for context in self._host['ctypes'].get('OfxImageEffectPropSupportedContexts'):
            context_string = ctypes.cast(context, ctypes.c_char_p).value.decode('utf-8')
            plugin_contexts = [ctypes.cast(i, ctypes.c_char_p).value.decode('utf-8')
                               for i in plugin['ctypes'].get('OfxImageEffectPropSupportedContexts')]

            if context_string in plugin_contexts:
                context_id = '%s.%s'%(plugin_id, context_string)

                context_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxImageEffectPropContext'),
                                                  ctypes.c_char_p(context_id.encode('utf-8')))

                context_descriptor = {'handle':           context_handle,
                                      'clips':            {},
                                      'parameters':       {},
                                      'pluginIdentifier': plugin_id,
                                      'ctypes':           OfxEffectContextProperties(context_string)}

                plugin['contexts'][context_string] = context_descriptor

                print('=== OfxImageEffectActionDescribeInContext %s'%context_string)

                entry_point(ctypes.c_char_p(b'OfxImageEffectActionDescribeInContext'),
                            ctypes.pointer(context_handle),
                            ctypes.pointer(context_handle),
                            0)

        return OFX_STATUS_OK

    def create_plugin_instance(self, plugin_id, width, height):
        plugin = self._host['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        active_id = self._add_active_plugin(plugin_id, 'OfxImageEffectContextFilter', width, height)

        print('=== OfxActionCreateInstance')

        entry_point(ctypes.c_char_p(b'OfxActionCreateInstance'),
                    ctypes.pointer(self._host['active_plugins'][active_id]['handle']),
                    0,
                    0)

        return(active_id, OFX_STATUS_OK)

    def load_image(self, filename, width, height):
        im_frame = ImageOps.flip(Image.open(filename))
        im_frame = im_frame.convert('RGBA')
        im_frame = im_frame.resize((width, height), Image.ANTIALIAS)
        np_frame = np.ascontiguousarray(np.array(im_frame.getdata()), dtype=np.uint8)
        frame_ptr = np_frame.ctypes.data_as(ctypes.c_void_p).value

        image_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxImage'),
                                        ctypes.c_char_p(b'Source'))

        image_props = {'handle':      image_handle,
                       'numpy_array': np_frame,
                       'ctypes':      OfxImageProperties('source', frame_ptr, width, height)}

        self._host['images']['Source'] = image_props

        return  OFX_STATUS_OK

    def create_output_buffer(self, width, height):
        out_frame = np.ascontiguousarray(np.zeros(width*height*4, np.uint8), dtype=np.uint8)
        out_frame_ptr = out_frame.ctypes.data_as(ctypes.c_void_p).value

        out_image_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxImage'),
                                            ctypes.c_char_p(b'Output'))

        out_image_props = {'handle':      out_image_handle,
                           'numpy_array': out_frame,
                           'ctypes':      OfxImageProperties('output', out_frame_ptr, width, height)}

        self._host['images']['Output'] = out_image_props

        return OFX_STATUS_OK

    def save_output_buffer(self, filename, width, height):
        ptr = self._host['images']['Output']['ctypes'].get('OfxImagePropData').value
        np_array = np.ctypeslib.as_array(ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte)), (height,width,4))
        im = ImageOps.flip(Image.fromarray(np_array))
        if filename.rsplit('.', 1)[1] in ['jpg', 'JPG']:
            im = im.convert('RGB')
        im.save(filename)

        return OFX_STATUS_OK

    def render(self, plugin_id, active_id, in_filename, out_filename, width, height):
        plugin = self._host['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        self.create_output_buffer(width, height)

        sequence_render_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxSequenceRenderAction'),
                                                  ctypes.c_char_p(active_id.encode('utf-8')))

        sequence_render_props = {'handle': sequence_render_handle,
                                 'ctypes': OfxSequenceRenderActionProperties()}

        self._host['render_sequences'][active_id] = sequence_render_props

        render_handle = CStructOfxHandle(ctypes.c_char_p(b'OfxRenderAction'),
                                         ctypes.c_char_p(active_id.encode('utf-8')))

        render_props = {'handle': render_handle,
                        'ctypes': OfxRenderActionProperties(width, height)}

        self._host['render_actions'][active_id] = render_props

        print('=== OfxImageEffectActionBeginSequenceRender')

        entry_point(ctypes.c_char_p(b'OfxImageEffectActionBeginSequenceRender'),
                    ctypes.pointer(self._host['active_plugins'][active_id]['handle']),
                    ctypes.pointer(sequence_render_handle),
                    0)

        print('=== OfxImageEffectActionRender')

        self.load_image(in_filename, width, height)

        entry_point(ctypes.c_char_p(b'OfxImageEffectActionRender'),
                    ctypes.pointer(self._host['active_plugins'][active_id]['handle']),
                    ctypes.pointer(render_handle),
                    0)

        self.save_output_buffer(out_filename, width, height)
        # delete source buffer

        print('=== OfxImageEffectActionEndSequenceRender')

        entry_point(ctypes.c_char_p(b'OfxImageEffectActionEndSequenceRender'),
                    ctypes.pointer(self._host['active_plugins'][active_id]['handle']),
                    ctypes.pointer(sequence_render_handle),
                    0)

        # delete render handle
        # delete sequence render handle
        # delete output buffer

        return OFX_STATUS_OK

    def destroy_plugin_instance(self, plugin_id, active_id):
        plugin = self._host['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        print('=== OfxActionDestroyInstance')

        entry_point(ctypes.c_char_p(b'OfxActionDestroyInstance'),
                    ctypes.pointer(self._host['active_plugins'][active_id]['handle']),
                    0,
                    0)

        # delete plugin instance

        print('=== OfxActionUnload')

        return OFX_STATUS_OK

    def unload_plugin(self, plugin_id):
        plugin = self._host['plugins'][plugin_id]
        entry_point = cfunc_plugin_entry_point(plugin['mainEntry'])

        entry_point(ctypes.c_char_p(b'OfxActionUnload'),
                    0,
                    0,
                    0)


        return OFX_STATUS_OK



