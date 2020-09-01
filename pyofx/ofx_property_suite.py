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

        self._suite = CStructOfxPropertySuite(
            self._prop_set_pointer,
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
            self._prop_get_dimension
        )

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def _get_handle_type(self, ctype_handle):
        handle = CStructOfxHandle.from_address(ctype_handle)
        return handle.property_type.decode("utf-8")

    def _get_property_object(self, ctype_handle):
        handle = CStructOfxHandle.from_address(ctype_handle)
        property_type = handle.property_type.decode("utf-8")
        bundle = handle.bundle.decode("utf-8")
        plugin = handle.plugin.decode("utf-8")
        context = handle.context.decode("utf-8")
        active_uid = handle.active_uid.decode("utf-8")
        name = handle.name.decode("utf-8")

        if property_type == 'OfxTypeImageEffectHost':
            return self._host['ctypes']

        if property_type == 'OfxTypeImageEffect':
            if plugin in self._host['bundles'][bundle]['plugins']:
                return self._host['bundles'][bundle]['plugins'][plugin]['ctypes']

        if property_type == 'OfxImageEffectPropContext':
            if plugin in self._host['bundles'][bundle]['plugins']:
                if context in self._host['bundles'][bundle]['plugins'][plugin]['contexts']:
                    return self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['ctypes']

        if property_type == 'OfxTypeClip':
            if plugin in self._host['bundles'][bundle]['plugins']:
                if context in self._host['bundles'][bundle]['plugins'][plugin]['contexts']:
                    if name in self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['clips']:
                        return self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['clips'][name]['ctypes']

        if property_type == 'OfxTypeParameter':
            if plugin in self._host['bundles'][bundle]['plugins']:
                if context in self._host['bundles'][bundle]['plugins'][plugin]['contexts']:
                    if name in self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['parameters']:
                        return self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['parameters'][name]['ctypes']

        if property_type == 'OfxTypeImageEffectInstance':
            if active_uid in self._host['active']['plugins']:
                return self._host['active']['plugins'][active_uid]['ctypes']

        if property_type == 'OfxTypeClipInstance':
            if active_uid in self._host['active']['plugins']:
                if name in self._host['active']['plugins'][active_uid]['clips']:
                    return self._host['active']['plugins'][active_uid]['clips'][name]['ctypes']

        if property_type == 'OfxTypeParameterInstance':
            if active_uid in self._host['active']['plugins']:
                if name in self._host['active']['plugins'][active_uid]['parameters']:
                    return self._host['active']['plugins'][active_uid]['parameters'][name]['ctypes']

        if property_type == 'OfxRenderAction':
            if active_uid in self._host['active']['plugins']:
                return self._host['active']['plugins'][active_uid]['render']['action']['ctypes']

        if property_type == 'OfxSequenceRenderAction':
            if active_uid in self._host['active']['plugins']:
                return self._host['active']['plugins'][active_uid]['render']['sequence']['ctypes']

        if property_type == 'OfxImage':
            if active_uid in self._host['active']['plugins']:
                if name in self._host['active']['plugins'][active_uid]['clips']:
                    return self._host['active']['plugins'][active_uid]['clips'][name]['image']['ctypes']

        return None

    ##################################################################################################################
    #
    # SET CALLBACK FUNCTIONS
    #
    ##################################################################################################################

    def _prop_set_string_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetString, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetString, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value.decode('utf-8'), 'str', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_double_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetDouble, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetDouble, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value, 'dbl', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_int_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetInt, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetInt, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        property_obj.update(ctype_string.decode('utf-8'), ctype_value, 'int', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_pointer_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetPointer, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetPointer, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        if ctype_value:
            property_obj.update(ctype_string.decode('utf-8'), ctype_value, 'ptr', ctype_index)
        else:
            property_obj.update(ctype_string.decode('utf-8'), 0, 'ptr', ctype_index)

        return OFX_STATUS_OK

    def _prop_set_pointer_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetPointerN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetPointerN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_int))
        for index in range(0, ctype_count):
            property_obj.update(ctype_string.decode('utf-8'), ctype_value_ptr[index], 'ptr', index)

        return OFX_STATUS_OK

    def _prop_set_string_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetStringN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetStringN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_char_p))
        for index in range(0, ctype_count):
            value_as_string = ctype_value_ptr[index].decode('utf-8')
            property_obj.update(ctype_string.decode('utf-8'), value_as_string, 'ptr', index)

        return OFX_STATUS_OK

    def _prop_set_double_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetDoubleN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetDoubleN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_double))
        for index in range(0, ctype_count):
            property_obj.update(ctype_string.decode('utf-8'), ctype_value_ptr[index], 'dbl', index)

        return OFX_STATUS_OK

    def _prop_set_int_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propSetIntN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propSetIntN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_int))
        for index in range(0, ctype_count):
            property_obj.update(ctype_string.decode('utf-8'), ctype_value_ptr[index], 'int', index)

        return OFX_STATUS_OK

    ##################################################################################################################
    #
    # GET CALLBACK FUNCTIONS
    #
    ##################################################################################################################

    def _prop_get_string_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetInt, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetInt, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.ptr(ctype_string.decode('utf-8'), ctype_index)

        return OFX_STATUS_OK

    def _prop_get_double_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetDouble, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetDouble, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.get(ctype_string.decode('utf-8'), ctype_index).value

        return OFX_STATUS_OK

    def _prop_get_int_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetInt, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetInt, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.get(ctype_string.decode('utf-8'), ctype_index).value

        return OFX_STATUS_OK

    def _prop_get_pointer_callback(self, ctype_handle, ctype_string, ctype_index, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetPointer, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetPointer, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value.contents.value = property_obj.get(ctype_string.decode('utf-8'), ctype_index).value

        return OFX_STATUS_OK

    def _prop_get_double_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetDoubleN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
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
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetIntN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetIntN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_int))
        for index in range(0, ctype_count):
            ctype_value_ptr[index] = int(property_obj.get(ctype_string.decode('utf-8'), index).value)

        return OFX_STATUS_OK

    def _prop_get_pointer_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetPointerN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetPointerN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_void_p))
        for index in range(0, ctype_count):
            ctype_value_ptr[index] = int(property_obj.get(ctype_string.decode('utf-8'), index).value)

        return OFX_STATUS_OK

    def _prop_get_string_n_callback(self, ctype_handle, ctype_string, ctype_count, ctype_value):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetStringN, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetStringN, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_value_ptr = ctypes.cast(ctype_value, ctypes.POINTER(ctypes.c_char_p))
        for index in range(0, ctype_count):
            ctype_value_ptr[index] = int(property_obj.get(ctype_string.decode('utf-8'), index).value)

        return OFX_STATUS_OK

    def _prop_get_dimension_callback(self, ctype_handle, ctype_string, ctype_count):
        property_obj = self._get_property_object(ctype_handle)

        if property_obj is None:
            property_type = self._get_handle_type(ctype_handle)
            print('ERROR: propGetDimension, unknown handle {}'.format(property_type)) 
            return OFX_STATUS_ERR_BAD_HANDLE

        if not property_obj.contains(ctype_string.decode('utf-8')):
            property_type = self._get_handle_type(ctype_handle)
            property_string = ctype_string.decode('utf-8')
            print('WARNING: propGetDimension, property {} not in {}'.format(property_string, property_type)) 
            return OFX_STATUS_ERR_UNKNOWN

        ctype_count.contents.value = property_obj.length(ctype_string.decode('utf-8'))

        return OFX_STATUS_OK

    ##################################################################################################################
    #
    # UTILITY CALLBACK FUNCTIONS
    #
    ##################################################################################################################

    def _prop_reset_callback(self, ctype_handle, ctype_string):
        # As there is no UI this callback should never get called.
        return OFX_STATUS_OK
