#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import copy
from ofx_ctypes import *
from ofx_property_sets import *
from ofx_status_codes import *

class OfxParameterSuite(object):
    def __init__(self, host):
        self._host = host

        self._param_define =               cfunc_param_define(self._param_define_callback)
        self._param_get_handle =           cfunc_param_get_handle(self._param_get_handle_callback)
        self._param_set_get_property_set = cfunc_param_set_get_property_set(self._param_set_get_property_set_callback)
        self._param_get_property_set =     cfunc_param_get_property_set(self._param_get_property_set_callback)
        self._param_get_value =            cfunc_param_get_value(self._param_get_value_callback)
        self._param_get_value_at_time =    cfunc_param_get_value_at_time(self._param_get_value_at_time_callback)
        self._param_get_derivative =       cfunc_param_get_derivative(self._param_get_derivative_callback)
        self._param_get_integral =         cfunc_param_get_integral(self._param_get_integral_callback)
        self._param_set_value =            cfunc_param_set_value(self._param_set_value_callback)
        self._param_set_value_at_time =    cfunc_param_set_value_at_time(self._param_set_value_at_time_callback)
        self._param_get_num_keys =         cfunc_param_get_num_keys(self._param_get_num_keys_callback)
        self._param_get_key_time =         cfunc_param_get_key_time(self._param_get_key_time_callback)
        self._param_get_key_index =        cfunc_param_get_key_index(self._param_get_key_index_callback)
        self._param_delete_key =           cfunc_param_delete_key(self._param_delete_key_callback)
        self._param_delete_all_keys =      cfunc_param_delete_all_keys(self._param_delete_all_keys_callback)
        self._param_copy =                 cfunc_param_copy(self._param_copy_callback)
        self._param_edit_begin =           cfunc_param_edit_begin(self._param_edit_begin_callback)
        self._param_edit_end =             cfunc_param_edit_end(self._param_edit_end_callback)

        self._suite = CStructOfxParameterSuite(self._param_define,
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
                                               self._param_edit_end)

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def create_parameter_instance(self, parameter_descriptor, instance_id):
        descriptor_id = parameter_descriptor['handle'].id.decode("utf-8")
        descriptor_name = descriptor_id.rsplit('.', 1)[1]
        instance_param_id = '%s.%s'%(instance_id, descriptor_name)

        parameter_handle = CStructOfxHandle("OfxTypeParameterInstance".encode('utf-8'),
                                                       instance_param_id.encode('utf-8'))

        if parameter_descriptor['ctypes'].contains('OfxParamPropDefault'):
            value = copy.deepcopy(parameter_descriptor['ctypes'].get('OfxParamPropDefault'))
        else:
            value = None

        return {'handle': parameter_handle,
                'value':  value,
                'ctypes': copy.deepcopy(parameter_descriptor['ctypes']) }

    def _decode_handle(self, ctype_handle):
        handle_structure = CStructOfxHandle.from_address(ctype_handle)
        handle_type = handle_structure.property_type.decode("utf-8")
        handle_id = handle_structure.id.decode("utf-8")

        return(handle_type, handle_id)

    def _param_define_callback(self, ctype_image_effect_handle, ctype_param_type, ctype_name, ctype_property_handle):
        (property_type, property_id) = self._decode_handle(ctype_image_effect_handle)
        param_type = ctype_param_type.decode("utf-8")

        plugin_id = property_id.rsplit('.', 1)[0]
        context_id = property_id.rsplit('.', 1)[1]
        param_name = ctype_name.decode("utf-8")
        param_id = "%s.%s"%(property_id, param_name)

        param_handle = CStructOfxHandle("OfxTypeParameter".encode('utf-8'),
                                        param_id.encode('utf-8'))

        self._host['plugins'][plugin_id]['contexts'][context_id]['parameters'][param_name] = {
            'handle': param_handle,
            'ctypes': OfxParameterProperties(param_name, param_type)
            }

        ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(param_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _param_get_handle_callback(self, ctype_image_effect_handle, ctype_name, ctype_param_handle, ctype_property_handle):
        (image_effect_type, image_effect_id) = self._decode_handle(ctype_image_effect_handle)
        param_name = ctype_name.decode("utf-8")

        param_handle = self._host['active_plugins'][image_effect_id]['parameters'][param_name]['handle']

        ctype_param_handle.contents.value = ctypes.cast(ctypes.pointer(param_handle), ctypes.c_void_p).value

        if ctype_property_handle:
            ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(param_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _param_set_get_property_set_callback(self, ctype_param_handle, ctype_property_handle):
        ctype_property_handle.contents.value = ctype_param_handle

        return OFX_STATUS_OK

    def _param_get_property_set_callback(self, ctype_param_handle, ctype_property_handle):
        ctype_property_handle.contents.value = ctype_param_handle

        return OFX_STATUS_OK

    def _get_double_type_string(self, param_object):
        return ctypes.cast(param_object['ctypes'].get('OfxParamPropDoubleType'), ctypes.c_char_p).value.decode('utf-8')

    # This is a horrendous hack to deal with variadic args in function call.
    # Seems to work on Linux, may crash spectacularly on other platforms 
    def _param_get_value_callback(self, ctype_param_handle, vargs):
        (param_type, param_id) = self._decode_handle(ctype_param_handle)

        active_id = param_id.rsplit('.', 1)[0]
        param_name = param_id.rsplit('.', 1)[1]

        param_ctypes = self._host['active_plugins'][active_id]['parameters'][param_name]['ctypes']
        ofx_property_type = ctypes.cast(param_ctypes.get('OfxParamPropType'), ctypes.c_char_p).value.decode('utf-8')
 
        if ofx_property_type == 'OfxParamTypeInteger':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
        elif ofx_property_type == 'OfxParamTypeDouble':
            double_type_string = self._get_double_type_string(self._host['active_plugins'][active_id]['parameters'][param_name])
            v1 = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = v1
        elif ofx_property_type == 'OfxParamTypeBoolean':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
        elif ofx_property_type == 'OfxParamTypeChoice':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
        elif ofx_property_type == 'OfxParamTypeRGBA':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            va_list[1] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1].value
            va_list[2] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2].value
            va_list[3] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][3].value
        elif ofx_property_type == 'OfxParamTypeRGB':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            va_list[1] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1].value
            va_list[2] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2].value
        elif ofx_property_type == 'OfxParamTypeDouble2D':
            double_type_string = self._get_double_type_string(self._host['active_plugins'][active_id]['parameters'][param_name])
            v1 = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            v2 = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1].value
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = v1
            va_list[1] = v2
        elif ofx_property_type == 'OfxParamTypeInteger2D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            va_list[1] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1].value
        elif ofx_property_type == 'OfxParamTypeDouble3D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_double))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            va_list[1] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1].value
            va_list[2] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2].value
        elif ofx_property_type == 'OfxParamTypeInteger3D':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
            va_list[1] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1].value
            va_list[2] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2].value
        elif ofx_property_type == 'OfxParamTypeString':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_char_p))
            print('PLACEHOLDER: paramGetValue for a OfxParamTypeString')
        elif ofx_property_type == 'OfxParamTypePushButton':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_int))
            va_list[0] = self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0].value
        else:
            print('ERROR {} is not a valid type for paramGetValue')
            return OFX_STATUS_FAILED

        return OFX_STATUS_OK

    def _param_get_value_at_time_callback(self, ctype_param_handle, ctype_time, vargs):
        # Currently parameters don't animate so we just send back paramGetValue
        return self._param_get_value_callback(ctype_param_handle, vargs)

    # This is a horrendous hack to deal with variadic args in function call.
    # Seems to work on Linux, may crash spectacularly on other platforms 
    def _param_set_value_callback(self, ctype_param_handle, d_arg_1, d_arg_2, d_arg_3, d_arg_4, i_arg_1, i_arg_2, i_arg_3, i_arg_4):
        (param_type, param_id) = self._decode_handle(ctype_param_handle)

        active_id = param_id.rsplit('.', 1)[0]
        param_name = param_id.rsplit('.', 1)[1]

        param_ctypes = self._host['active_plugins'][active_id]['parameters'][param_name]['ctypes']
        ofx_property_type = ctypes.cast(param_ctypes.get('OfxParamPropType'), ctypes.c_char_p).value.decode('utf-8')

        if ofx_property_type == 'OfxParamTypeInteger':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_int(i_arg_1)
        elif ofx_property_type == 'OfxParamTypeDouble':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_double(d_arg_1)
        elif ofx_property_type == 'OfxParamTypeBoolean':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_int(i_arg_1)
        elif ofx_property_type == 'OfxParamTypeChoice':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_int(i_arg_1)
        elif ofx_property_type == 'OfxParamTypeRGBA':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_double(d_arg_1)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1] = ctypes.c_double(d_arg_2)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2] = ctypes.c_double(d_arg_3)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][3] = ctypes.c_double(d_arg_4)
        elif ofx_property_type == 'OfxParamTypeRGB':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_double(d_arg_1)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1] = ctypes.c_double(d_arg_2)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2] = ctypes.c_double(d_arg_3)
        elif ofx_property_type == 'OfxParamTypeDouble2D':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_double(d_arg_1)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1] = ctypes.c_double(d_arg_2)
        elif ofx_property_type == 'OfxParamTypeInteger2D':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_int(i_arg_1)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1] = ctypes.c_int(i_arg_2)
        elif ofx_property_type == 'OfxParamTypeDouble3D':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_double(d_arg_1)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1] = ctypes.c_double(d_arg_2)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2] = ctypes.c_double(d_arg_3)
        elif ofx_property_type == 'OfxParamTypeInteger3D':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_int(i_arg_1)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][1] = ctypes.c_int(i_arg_2)
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][2] = ctypes.c_int(i_arg_3)
        elif ofx_property_type == 'OfxParamTypeString':
            va_list = ctypes.cast(vargs, ctypes.POINTER(ctypes.c_char_p))
            print('PLACEHOLDER: paramGetValue for a OfxParamTypeString')
        elif ofx_property_type == 'OfxParamTypePushButton':
            self._host['active_plugins'][active_id]['parameters'][param_name]['value'][0] = ctypes.c_int(i_arg_1)
        else:
            print('ERROR {} is not a valid type for paramGetValue'.format(ofx_property_type))
            return OFX_STATUS_FAILED

        return OFX_STATUS_OK

    def _param_set_value_at_time_callback(self, ctype_param_handle, ctype_time, d_arg_1, d_arg_2, d_arg_3, d_arg_4, i_arg_1, i_arg_2, i_arg_3, i_arg_4):
        # Currently parameters don't animate so we just send back paramSetValue
        return self._param_set_value_callback(ctype_param_handle, d_arg_1, d_arg_2, d_arg_3, d_arg_4, i_arg_1, i_arg_2, i_arg_3, i_arg_4)

    ##################################################################################################################
    #
    # PLACEHOLDERS
    #
    ##################################################################################################################

    def _param_get_derivative_callback(self, paramHandle, time, vargs):
        print('PLACEHOLDER paramGetDerivative')
        return OFX_STATUS_FAILED

    def _param_get_integral_callback(self, paramHandle, time1,  time2, vargs):
        print('PLACEHOLDER paramGetIntegral')
        return OFX_STATUS_FAILED

    def _param_get_num_keys_callback(self, paramHandle, numberOfKeys):
        print('PLACEHOLDER paramGetNumKeys')
        return OFX_STATUS_FAILED

    def _param_get_key_time_callback(self,paramHandle, nthKey, time):
        print('PLACEHOLDER paramGetKeyTime')
        return OFX_STATUS_FAILED

    def _param_get_key_index_callback(self,paramHandle, time, direction, index):
        print('PLACEHOLDER paramGetKeyIndex')
        return OFX_STATUS_FAILED

    def _param_delete_key_callback(self, paramHandle, time):
        print('PLACEHOLDER paramDeleteKey')
        return OFX_STATUS_FAILED

    def _param_delete_all_keys_callback(self, paramHandle):
        print('PLACEHOLDER paramDeleteAllKeys')
        return OFX_STATUS_FAILED

    def _param_copy_callback(self, paramTo, paramFrom, dstOffset, frameRange):
        print('PLACEHOLDER paramCopy')
        return OFX_STATUS_FAILED

    def _param_edit_begin_callback(self, paramSet, name):
        print('PLACEHOLDER paramEditBegin')
        return OFX_STATUS_FAILED

    def _param_edit_end_callback(self,paramSet):
        print('PLACEHOLDER paramEditEnd')
        return OFX_STATUS_FAILED






