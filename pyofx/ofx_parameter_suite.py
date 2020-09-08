#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import copy
import logging
import platform
import ofx_ctypes
import ofx_property_sets
import ofx_status_codes

class OfxParameterSuite(object):
    def __init__(self, host):
        self._host = host

        self._param_define =               ofx_ctypes.cfunc_param_define(self._param_define_callback)
        self._param_get_handle =           ofx_ctypes.cfunc_param_get_handle(self._param_get_handle_callback)
        self._param_set_get_property_set = ofx_ctypes.cfunc_param_set_get_property_set(self._param_set_get_property_set_callback)
        self._param_get_property_set =     ofx_ctypes.cfunc_param_get_property_set(self._param_get_property_set_callback)
        self._param_get_value =            ofx_ctypes.cfunc_param_get_value(self._param_get_value_callback)
        self._param_get_value_at_time =    ofx_ctypes.cfunc_param_get_value_at_time(self._param_get_value_at_time_callback)
        self._param_get_derivative =       ofx_ctypes.cfunc_param_get_derivative(self._param_get_derivative_callback)
        self._param_get_integral =         ofx_ctypes.cfunc_param_get_integral(self._param_get_integral_callback)
        self._param_set_value =            ofx_ctypes.cfunc_param_set_value(self._param_set_value_callback)
        self._param_set_value_at_time =    ofx_ctypes.cfunc_param_set_value_at_time(self._param_set_value_at_time_callback)
        self._param_get_num_keys =         ofx_ctypes.cfunc_param_get_num_keys(self._param_get_num_keys_callback)
        self._param_get_key_time =         ofx_ctypes.cfunc_param_get_key_time(self._param_get_key_time_callback)
        self._param_get_key_index =        ofx_ctypes.cfunc_param_get_key_index(self._param_get_key_index_callback)
        self._param_delete_key =           ofx_ctypes.cfunc_param_delete_key(self._param_delete_key_callback)
        self._param_delete_all_keys =      ofx_ctypes.cfunc_param_delete_all_keys(self._param_delete_all_keys_callback)
        self._param_copy =                 ofx_ctypes.cfunc_param_copy(self._param_copy_callback)
        self._param_edit_begin =           ofx_ctypes.cfunc_param_edit_begin(self._param_edit_begin_callback)
        self._param_edit_end =             ofx_ctypes.cfunc_param_edit_end(self._param_edit_end_callback)

        self._suite = ofx_ctypes.CStructOfxParameterSuite(
            self._param_define,
            self._param_get_handle,
            self._param_set_get_property_set,
            self._param_get_property_set,
            self._param_get_value,
            self._param_get_value_at_time,
            self._param_get_derivative,
            self._param_get_integral,
            self._param_set_value,
            self._param_set_value_at_time,
            self._param_get_num_keys,
            self._param_get_key_time,
            self._param_get_key_index,
            self._param_delete_key,
            self._param_delete_all_keys,
            self._param_copy,
            self._param_edit_begin,
            self._param_edit_end
        )

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def create_parameter_instance(self, parameter_descriptor, active_uid):
        handle = parameter_descriptor['handle']

        parameter_handle = ofx_ctypes.CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeParameterInstance'),
            handle.bundle,
            handle.plugin,
            handle.context,
            ctypes.c_char_p(active_uid.encode("utf-8")),
            handle.name
        )

        if parameter_descriptor['ctypes'].contains('OfxParamPropDefault'):
            value = copy.deepcopy(parameter_descriptor['ctypes'].get('OfxParamPropDefault'))
        else:
            value = None

        return {
            'handle': parameter_handle,
            'value':  value,
            'ctypes': copy.deepcopy(parameter_descriptor['ctypes'])
        }


    def _param_define_callback(self, ctype_image_effect_handle, ctype_param_type, ctype_name, ctype_property_handle):
        handle = ofx_ctypes.CStructOfxHandle.from_address(ctype_image_effect_handle)

        bundle = handle.bundle.decode("utf-8")
        plugin = handle.plugin.decode("utf-8")
        context = handle.context.decode("utf-8")
        name = ctype_name.decode("utf-8")
        param_type = ctype_param_type.decode("utf-8")

        param_handle = ofx_ctypes.CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeParameter'),
            handle.bundle,
            handle.plugin,
            handle.context,
            ctypes.c_char_p(b''),
            ctype_name
        )

        self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['parameters'][name] = {
            'handle': param_handle,
            'ctypes': ofx_property_sets.OfxParameterProperties(name, param_type)
        }

        ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(param_handle), ctypes.c_void_p).value

        return ofx_status_codes.OFX_STATUS_OK

    def _param_get_handle_callback(self, ctype_image_effect_handle, ctype_name, ctype_param_handle, ctype_property_handle):
        handle = ofx_ctypes.CStructOfxHandle.from_address(ctype_image_effect_handle)

        active_uid = handle.active_uid.decode("utf-8")
        name = ctype_name.decode("utf-8")

        if name not in self._host['active']['plugins'][active_uid]['parameters']:
            return ofx_status_codes.OFX_STATUS_ERR_UNKNOWN

        param_handle = self._host['active']['plugins'][active_uid]['parameters'][name]['handle']

        ctype_param_handle.contents.value = ctypes.cast(ctypes.pointer(param_handle), ctypes.c_void_p).value

        if ctype_property_handle:
            ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(param_handle), ctypes.c_void_p).value

        return ofx_status_codes.OFX_STATUS_OK

    def _param_set_get_property_set_callback(self, ctype_param_handle, ctype_property_handle):
        ctype_property_handle.contents.value = ctype_param_handle

        return ofx_status_codes.OFX_STATUS_OK

    def _param_get_property_set_callback(self, ctype_param_handle, ctype_property_handle):
        ctype_property_handle.contents.value = ctype_param_handle

        return ofx_status_codes.OFX_STATUS_OK

    # This is a horrendous hack to deal with variadic args in function call.
    # Seems to work on Linux, may crash spectacularly on other platforms 
    def _param_get_value_callback(self, ctype_param_handle, vargs):
        handle = ofx_ctypes.CStructOfxHandle.from_address(ctype_param_handle)

        active_uid = handle.active_uid.decode("utf-8")
        name = handle.name.decode("utf-8")

        param = self._host['active']['plugins'][active_uid]['parameters'][name]

        ofx_property_type = ctypes.cast(param['ctypes'].get('OfxParamPropType'), ctypes.c_char_p).value.decode('utf-8')
 
        if ofx_property_type == 'OfxParamTypeInteger':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = param['value'][0].value
        elif ofx_property_type == 'OfxParamTypeDouble':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = param['value'][0].value
        elif ofx_property_type == 'OfxParamTypeBoolean':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = param['value'][0].value
        elif ofx_property_type == 'OfxParamTypeChoice':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = param['value'][0].value
        elif ofx_property_type == 'OfxParamTypeRGBA':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = param['value'][0].value
            va_list[1] = param['value'][1].value
            va_list[2] = param['value'][2].value
            va_list[3] = param['value'][3].value
        elif ofx_property_type == 'OfxParamTypeRGB':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = param['value'][0].value
            va_list[1] = param['value'][1].value
            va_list[2] = param['value'][2].value
        elif ofx_property_type == 'OfxParamTypeDouble2D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = param['value'][0].value
            va_list[1] = param['value'][1].value
        elif ofx_property_type == 'OfxParamTypeInteger2D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = param['value'][0].value
            va_list[1] = param['value'][1].value
        elif ofx_property_type == 'OfxParamTypeDouble3D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = param['value'][0].value
            va_list[1] = param['value'][1].value
            va_list[2] = param['value'][2].value
        elif ofx_property_type == 'OfxParamTypeInteger3D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = param['value'][0].value
            va_list[1] = param['value'][1].value
            va_list[2] = param['value'][2].value
        elif ofx_property_type == 'OfxParamTypePushButton':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = param['value'][0].value
        elif ofx_property_type == 'OfxParamTypeCustom':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_char_p))
            va_list[0] = param['value'][0].value
        elif ofx_property_type == 'OfxParamTypeString':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_char_p))
            va_list[0] = param['value'][0].value
        else:
            logging.error('{} is not a valid type for paramGetValue ({})'.format(ofx_property_type, name))
            return ofx_status_codes.OFX_STATUS_FAILED

        return ofx_status_codes.OFX_STATUS_OK

    def _param_get_value_at_time_callback(self, ctype_param_handle, ctype_time, vargs):
        # Currently parameters don't animate so we just send back paramGetValue
        return self._param_get_value_callback(ctype_param_handle, vargs)

    # This is a horrendous hack to deal with variadic args in function call.
    # Seems to work on Linux, may crash spectacularly on other platforms 
    def _param_set_value_callback(self, ctype_param_handle, d_arg_1, d_arg_2, d_arg_3, d_arg_4,
                                                            p_arg_1, p_arg_2, p_arg_3, p_arg_4,
                                                            i_arg_1, i_arg_2, i_arg_3, i_arg_4):
        handle = ofx_ctypes.CStructOfxHandle.from_address(ctype_param_handle)

        active_uid = handle.active_uid.decode("utf-8")
        name = handle.name.decode("utf-8")

        param = self._host['active']['plugins'][active_uid]['parameters'][name]

        ofx_property_type = ctypes.cast(param['ctypes'].get('OfxParamPropType'), ctypes.c_char_p).value.decode('utf-8')

        if ofx_property_type == 'OfxParamTypeInteger':
            if platform.system() == 'Windows':
                param['value'][0] = ctypes.c_int(i_arg_1)
            else:
                param['value'][0] = ctypes.c_int(p_arg_1)
        elif ofx_property_type == 'OfxParamTypeDouble':
            param['value'][0] = ctypes.c_double(d_arg_1)
        elif ofx_property_type == 'OfxParamTypeBoolean':
            if platform.system() == 'Windows':
                param['value'][0] = ctypes.c_int(i_arg_1)
            else:
                param['value'][0] = ctypes.c_int(p_arg_1)
        elif ofx_property_type == 'OfxParamTypeChoice':
            if platform.system() == 'Windows':
                param['value'][0] = ctypes.c_int(i_arg_1)
            else:
                param['value'][0] = ctypes.c_int(p_arg_1)
        elif ofx_property_type == 'OfxParamTypeRGBA':
            param['value'][0] = ctypes.c_double(d_arg_1)
            param['value'][1] = ctypes.c_double(d_arg_2)
            param['value'][2] = ctypes.c_double(d_arg_3)
            param['value'][3] = ctypes.c_double(d_arg_4)
        elif ofx_property_type == 'OfxParamTypeRGB':
            param['value'][0] = ctypes.c_double(d_arg_1)
            param['value'][1] = ctypes.c_double(d_arg_2)
            param['value'][2] = ctypes.c_double(d_arg_3)
        elif ofx_property_type == 'OfxParamTypeDouble2D':
            param['value'][0] = ctypes.c_double(d_arg_1)
            param['value'][1] = ctypes.c_double(d_arg_2)
        elif ofx_property_type == 'OfxParamTypeInteger2D':
            if platform.system() == 'Windows':
                param['value'][0] = ctypes.c_int(i_arg_1)
                param['value'][1] = ctypes.c_int(i_arg_2)
            else:
                param['value'][0] = ctypes.c_int(p_arg_1)
                param['value'][0] = ctypes.c_int(p_arg_2)
        elif ofx_property_type == 'OfxParamTypeDouble3D':
            param['value'][0] = ctypes.c_double(d_arg_1)
            param['value'][1] = ctypes.c_double(d_arg_2)
            param['value'][2] = ctypes.c_double(d_arg_3)
        elif ofx_property_type == 'OfxParamTypeInteger3D':
            if platform.system() == 'Windows':
                param['value'][0] = ctypes.c_int(i_arg_1)
                param['value'][1] = ctypes.c_int(i_arg_2)
                param['value'][2] = ctypes.c_int(i_arg_3)
            else:
                param['value'][0] = ctypes.c_int(p_arg_1)
                param['value'][0] = ctypes.c_int(p_arg_2)
                param['value'][0] = ctypes.c_int(p_arg_3)
        elif ofx_property_type == 'OfxParamTypePushButton':
            if platform.system() == 'Windows':
                param['value'][0] = ctypes.c_int(i_arg_1)
            else:
                param['value'][0] = ctypes.c_int(p_arg_1)
        elif ofx_property_type == 'OfxParamTypeCustom':
            param['value'][0] = ctypes.create_string_buffer(ctypes.c_char_p(p_arg_1).value)
        elif ofx_property_type == 'OfxParamTypeString':
            param['value'][0] = ctypes.create_string_buffer(ctypes.c_char_p(p_arg_1).value)
        else:
            logging.error('{} is not a valid type for paramSetValue ({})'.format(ofx_property_type, name))
            return ofx_status_codes.OFX_STATUS_FAILED

        return ofx_status_codes.OFX_STATUS_OK

    def _param_set_value_at_time_callback(self, ctype_param_handle, ctype_time, d_arg_1, d_arg_2, d_arg_3, d_arg_4,
                                                                                p_arg_1, p_arg_2, p_arg_3, p_arg_4,
                                                                                i_arg_1, i_arg_2, i_arg_3, i_arg_4):
        # Currently parameters don't animate so we just send back paramSetValue
        return self._param_set_value_callback(ctype_param_handle, d_arg_1, d_arg_2, d_arg_3, d_arg_4,
                                                                  p_arg_1, p_arg_2, p_arg_3, p_arg_4,
                                                                  i_arg_1, i_arg_2, i_arg_3, i_arg_4)

    def _param_get_derivative_callback(self, ctype_param_handle, ctype_time, ctype_vargs):
        # Parametric parameters are not supported
        return ofx_status_codes.OFX_STATUS_FAILED

    def _param_get_integral_callback(self, ctype_param_handle, ctype_time1, ctype_time2, ctype_vargs):
        # Parametric parameters are not supported
        return ofx_status_codes.OFX_STATUS_FAILED

    def _param_get_num_keys_callback(self, ctype_param_handle, ctype_number_of_keys):
        # Nothing animates so always 0 keys
        ctype_number_of_keys.contents.value = 0
        return ofx_status_codes.OFX_STATUS_OK

    def _param_get_key_time_callback(self, ctype_param_handle, ctype_keys, ctype_time):
        # Nothing animates so always time 0
        ctype_time.contents.value = 0
        return ofx_status_codes.OFX_STATUS_OK

    def _param_get_key_index_callback(self, ctype_param_handle, ctype_time, ctype_direction, ctype_index):
        # No keys to return
        ctype_index.contents.value = -1
        return ofx_status_codes.OFX_STATUS_OK

    def _param_delete_key_callback(self, paramHandle, time):
        # No keys to delete
        return ofx_status_codes.OFX_STATUS_OK

    def _param_delete_all_keys_callback(self, paramHandle):
        # No keys to delete
        return ofx_status_codes.OFX_STATUS_OK

    def _param_copy_callback(self, paramTo, paramFrom, dstOffset, frameRange):
        # No UI so this shouldn't get called
        return ofx_status_codes.OFX_STATUS_OK

    def _param_edit_begin_callback(self, paramSet, name):
        # No undo/redo so this is not needed
        return ofx_status_codes.OFX_STATUS_OK

    def _param_edit_end_callback(self,paramSet):
        # No undo/redo so this is not needed
        return ofx_status_codes.OFX_STATUS_OK

