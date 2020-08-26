#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import re
from ofx_ctypes import *
from ofx_status_codes import *

class OfxPropertySuite():
    def __init__(self, host):
        self._host = host

        self._prop_set_pointer =   cfunc_prop_set_pointer(self._prop_set_pointer_callback)
        self._prop_set_string =    cfunc_prop_set_string(self._prop_set_string_callback)
        self._prop_set_double =    cfunc_prop_set_double(self._prop_set_double_callback)
        self._prop_set_int =       cfunc_prop_set_int(self._prop_set_int_callback)
        self._prop_set_pointer_n = cfunc_prop_set_pointer_n(self._prop_set_pointer_n_callback)
        self._prop_set_string_n =  cfunc_prop_set_string_n(self._prop_set_string_n_callback)
        self._prop_set_double_n =  cfunc_prop_set_double_n(self._prop_set_double_n_callback)
        self._prop_set_int_n =     cfunc_prop_set_int_n(self._prop_set_int_n_callback)
        self._prop_get_pointer =   cfunc_prop_get_pointer(self._prop_get_pointer_callback)
        self._prop_get_string =    cfunc_prop_get_string(self._prop_get_string_callback)
        self._prop_get_double =    cfunc_prop_get_double(self._prop_get_double_callback)
        self._prop_get_int =       cfunc_prop_get_int(self._prop_get_int_callback)
        self._prop_get_pointer_n = cfunc_prop_get_pointer_n(self._prop_get_pointer_n_callback)
        self._prop_get_string_n =  cfunc_prop_get_string_n(self._prop_get_string_n_callback)
        self._prop_get_double_n =  cfunc_prop_get_double_n(self._prop_get_double_n_callback)
        self._prop_get_int_n =     cfunc_prop_get_int_n(self._prop_get_int_n_callback)
        self._prop_reset =         cfunc_prop_reset(self._prop_reset_callback)
        self._prop_get_dimension = cfunc_prop_get_dimension(self._prop_get_dimension_callback)

        self._suite = CStructOfxPropertySuite(self._prop_set_pointer,
                                              self._prop_set_string,
                                              self._prop_set_double,
                                              self._prop_set_int,
                                              self._prop_set_pointer_n,
                                              self._prop_set_string_n,
                                              self._prop_set_double_n,
                                              self._prop_set_int_n,
                                              self._prop_get_pointer,
                                              self._prop_get_string,
                                              self._prop_get_double,
                                              self._prop_get_int,
                                              self._prop_get_pointer_n,
                                              self._prop_get_string_n,
                                              self._prop_get_double_n,
                                              self._prop_get_int_n,
                                              self._prop_reset,
                                              self._prop_get_dimension)

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def _decode_handle(self, ctype_handle):
        handle_structure = CStructOfxHandle.from_address(ctype_handle)
        handle_type = handle_structure.property_type.decode("utf-8")
        handle_id = handle_structure.id.decode("utf-8")

        return(handle_type, handle_id)

    def _get_property_object(self, ctype_handle):
        (property_type, property_id) = self._decode_handle(ctype_handle)

        regex_pattern = re.compile('fx\_\d\d\d\d\d\.')
        active_property_set = regex_pattern.match(property_id) is not None

        if property_type == 'OfxTypeImageEffectHost':
            return self._host['ctypes']

        if property_type == 'OfxImageEffectPropContext':
            plugin_id = property_id.rsplit('.', 1)[0]
            context_id = property_id.rsplit('.', 1)[1]
            if (plugin_id in self._host['plugins'] and
                context_id in self._host['plugins'][plugin_id]['contexts']):
                return self._host['plugins'][plugin_id]['contexts'][context_id]['ctypes']

        if property_type == 'OfxTypeImageEffect':
            if property_id in self._host['plugins']:
                return self._host['plugins'][property_id]['ctypes']

        if property_type == 'OfxTypeImageEffectInstance':
            if property_id in self._host['active_plugins']:
                return self._host['active_plugins'][property_id]['ctypes']

        if property_type == 'OfxTypeClip' and active_property_set:
            active_id = property_id.rsplit('.', 1)[0]
            clip_id = property_id.rsplit('.', 1)[1]
            if (active_id in self._host['active_plugins'] and
                clip_id in self._host['active_plugins'][active_id]['clips']):
                return self._host['active_plugins'][active_id]['clips'][clip_id]['ctypes']
        elif property_type == 'OfxTypeClip':
            plugin_id = property_id.rsplit('.', 2)[0]
            context_id = property_id.rsplit('.', 2)[1]
            clip_id = property_id.rsplit('.', 2)[2]
            if (plugin_id in self._host['plugins'] and
                context_id in self._host['plugins'][plugin_id]['contexts'] and
                clip_id in self._host['plugins'][plugin_id]['contexts'][context_id]['clips']):
                return self._host['plugins'][plugin_id]['contexts'][context_id]['clips'][clip_id]['ctypes']

        if property_type == 'OfxTypeParameter':
            plugin_id = property_id.rsplit('.', 2)[0]
            context_id = property_id.rsplit('.', 2)[1]
            param_id = property_id.rsplit('.', 2)[2]
            if (plugin_id in self._host['plugins'] and
                context_id in self._host['plugins'][plugin_id]['contexts'] and
                param_id in self._host['plugins'][plugin_id]['contexts'][context_id]['parameters']):
                return self._host['plugins'][plugin_id]['contexts'][context_id]['parameters'][param_id]['ctypes']

        if property_type == 'OfxTypeParameterInstance' and active_property_set:
            active_id = property_id.rsplit('.', 1)[0]
            param_id = property_id.rsplit('.', 1)[1]
            if (active_id in self._host['active_plugins'] and
                param_id in self._host['active_plugins'][active_id]['parameters']):
                return self._host['active_plugins'][active_id]['parameters'][param_id]['ctypes']

        if property_type == 'OfxRenderAction':
            return self._host['render_actions'][property_id]['ctypes']

        if property_type == 'OfxSequenceRenderAction':
            return self._host['render_sequences'][property_id]['ctypes']

        if property_type == 'OfxImage':
            return self._host['images'][property_id]['ctypes']

        return None

    ##################################################################################################################
    #
    # SET CALLBACK FUNTIONS
    #
    ##################################################################################################################

    def _prop_set_string_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propSetString, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetString, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value.decode('utf-8'), 'str', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_double_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propSetDouble, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetDouble, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value, 'dbl', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_int_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propSetInt, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetInt, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value, 'int', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_pointer_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propSetPointer, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetPointer, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value, 'ptr', ctype_index)

        return OFX_STATUS_OK

    ##################################################################################################################
    #
    # GET CALLBACK FUNTIONS
    #
    ##################################################################################################################

    def _prop_get_string_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetInt, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetInt, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.ptr(ctype_string.decode('utf-8'), ctype_index)

        return OFX_STATUS_OK

    def _prop_get_double_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetDouble, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetDouble, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.get(ctype_string.decode('utf-8'), ctype_index).value

        return OFX_STATUS_OK

    def _prop_get_int_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetInt, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetInt, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.get(ctype_string.decode('utf-8'), ctype_index).value

        return OFX_STATUS_OK

    def _prop_get_pointer_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetPointer, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetPointer, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.get(ctype_string.decode('utf-8'), ctype_index).value

        return OFX_STATUS_OK

    def _prop_get_double_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetDoubleN, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetDoubleN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_double))
        for index in range(0, ctype_count):
            ctype_value_ptr[index] = float(property_obj.get(ctype_string.decode('utf-8'), index).value)

        return OFX_STATUS_OK

    def _prop_get_int_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetIntN, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetIntN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_int))
        for index in range(0, ctype_count):
            ctype_value_ptr[index] = int(property_obj.get(ctype_string.decode('utf-8'), index).value)

        return OFX_STATUS_OK

    def _prop_get_dimension_callback(self, ctype_handle, ctype_string, ctype_count):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            (property_type, property_id) = self._decode_handle(ctype_handle)
            print('ERROR: propGetDimension, unknown handle {} {}'.format(property_type, property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            (property_type, property_id) = self._decode_handle(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetDimension, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_count.contents.value = property_obj.length(ctype_string.decode('utf-8'))

        return OFX_STATUS_OK

    ##################################################################################################################
    #
    # PLACEHOLDERS
    #
    ##################################################################################################################

    def _prop_get_pointer_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        print('PLACEHOLDER propGetPointerN')
        return OFX_STATUS_FAILED

    def _prop_get_string_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        print('PLACEHOLDER propGetStringN')
        return OFX_STATUS_FAILED

    def _prop_set_pointer_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        print('PLACEHOLDER propSetPointerN')
        return OFX_STATUS_FAILED

    def _prop_set_string_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        print('PLACEHOLDER propSetStringN')
        return OFX_STATUS_FAILED

    def _prop_set_double_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        print('PLACEHOLDER propSetDoubleN')
        return OFX_STATUS_FAILED

    def _prop_set_int_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        print('PLACEHOLDER propSetIntN')
        return OFX_STATUS_FAILED

    def _prop_reset_callback(self, ctype_handle, ctype_string):
        print('PLACEHOLDER propReset')
        return OFX_STATUS_FAILED




