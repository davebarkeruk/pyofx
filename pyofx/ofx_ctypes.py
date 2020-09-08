#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes

########################################################################################
#
# CTYPE GetPlugin Function defs
#
########################################################################################

cfunc_fetch_suite =        ctypes.CFUNCTYPE(ctypes.c_void_p,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int)

cfunc_plugin_entry_point = ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_char_p,
                                            ctypes.c_void_p,
                                            ctypes.c_void_p,
                                            ctypes.c_void_p)

########################################################################################
#
# CTYPE Structure defs
#
########################################################################################

class CStructOfxHandle(ctypes.Structure):
     _fields_ = [('property_type', ctypes.c_char_p),
                 ('bundle',        ctypes.c_char_p),
                 ('plugin',        ctypes.c_char_p),
                 ('context',       ctypes.c_char_p),
                 ('active_uid',    ctypes.c_char_p),
                 ('name',          ctypes.c_char_p)]

class CStructOfxHost(ctypes.Structure):
     _fields_ = [("host",       ctypes.POINTER(CStructOfxHandle)),
                 ("fetchSuite", cfunc_fetch_suite)]

class CStructOfxPlugin(ctypes.Structure):
     _fields_ = [("pluginApi",          ctypes.c_char_p),
                 ("apiVersion",         ctypes.c_int),
                 ("pluginIdentifier",   ctypes.c_char_p),
                 ("pluginVersionMajor", ctypes.c_uint),
                 ("pluginVersionMinor", ctypes.c_uint),
                 ("setHost",            ctypes.c_void_p),
                 ("mainEntry",          ctypes.c_void_p)]

class CStructOfxRangeI(ctypes.Structure):
     _fields_ = [('min', ctypes.c_int),
                 ('max', ctypes.c_int)]

class CStructOfxRangeD(ctypes.Structure):
     _fields_ = [('min', ctypes.c_double),
                 ('max', ctypes.c_double)]

class CStructOfxPointI(ctypes.Structure):
     _fields_ = [('x', ctypes.c_int),
                 ('y', ctypes.c_int)]

class CStructOfxPointD(ctypes.Structure):
     _fields_ = [('x', ctypes.c_double),
                 ('y', ctypes.c_double)]

class CStructOfxRectI(ctypes.Structure):
     _fields_ = [('x1', ctypes.c_int),
                 ('y1', ctypes.c_int),
                 ('x2', ctypes.c_int),
                 ('y2', ctypes.c_int)]

class CStructOfxRectD(ctypes.Structure):
     _fields_ = [('x1', ctypes.c_double),
                 ('y1', ctypes.c_double),
                 ('x2', ctypes.c_double),
                 ('y2', ctypes.c_double)]

########################################################################################
#
# CTYPE Host function defs
#
########################################################################################

cfunc_set_host = ctypes.CFUNCTYPE(None, ctypes.POINTER(CStructOfxHost))

########################################################################################
#
# CTYPE Property Suite functions and structure
#
########################################################################################

cfunc_prop_set_pointer =   ctypes.CFUNCTYPE(ctypes.c_int, 
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.c_void_p)

cfunc_prop_set_string =    ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.c_char_p)

cfunc_prop_set_double =    ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.c_double)

cfunc_prop_set_int =       ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.c_int)

cfunc_prop_set_pointer_n = ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_void_p))

cfunc_prop_set_string_n =  ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_char_p))

cfunc_prop_set_double_n =  ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_double))

cfunc_prop_set_int_n =     ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int))

cfunc_prop_get_pointer =   ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_void_p))

cfunc_prop_get_string =    ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_char_p))

cfunc_prop_get_double =    ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_double))

cfunc_prop_get_int =       ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int))

cfunc_prop_get_pointer_n = ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_void_p))

cfunc_prop_get_string_n =  ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_char_p))

cfunc_prop_get_double_n =  ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_double))

cfunc_prop_get_int_n =     ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_int))

cfunc_prop_reset =         ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p)

cfunc_prop_get_dimension = ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.c_void_p,
                                            ctypes.c_char_p,
                                            ctypes.POINTER(ctypes.c_int))


class CStructOfxPropertySuite(ctypes.Structure):
     _fields_ = [('propSetPointer',   cfunc_prop_set_pointer),
                 ('propSetString',    cfunc_prop_set_string),
                 ('propSetDouble',    cfunc_prop_set_double),
                 ('propSetInt',       cfunc_prop_set_int),
                 ('propSetPointerN',  cfunc_prop_set_pointer_n),
                 ('propSetStringN',   cfunc_prop_set_string_n),
                 ('propSetDoubleN',   cfunc_prop_set_double_n),
                 ('propSetIntN',      cfunc_prop_set_int_n),
                 ('propGetPointer',   cfunc_prop_get_pointer),
                 ('propGetString',    cfunc_prop_get_string),
                 ('propGetDouble',    cfunc_prop_get_double),
                 ('propGetInt',       cfunc_prop_get_int),
                 ('propGetPointerN',  cfunc_prop_get_pointer_n),
                 ('propGetStringN',   cfunc_prop_get_string_n),
                 ('propGetDoubleN',   cfunc_prop_get_double_n),
                 ('propGetIntN',      cfunc_prop_get_int_n),
                 ('propReset',        cfunc_prop_reset),
                 ('propGetDimension', cfunc_prop_get_dimension)]


########################################################################################
#
# CTYPE Parameter Suite functions and structure
#
########################################################################################

cfunc_param_define =               ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_char_p,
                                                    ctypes.c_char_p,
                                                    ctypes.POINTER(ctypes.c_void_p))

cfunc_param_get_handle =           ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_char_p,
                                                    ctypes.POINTER(ctypes.c_void_p),
                                                    ctypes.POINTER(ctypes.c_void_p))

cfunc_param_set_get_property_set = ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.POINTER(ctypes.c_void_p))

cfunc_param_get_property_set =     ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.POINTER(ctypes.c_void_p))

cfunc_param_get_value =            ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p)

cfunc_param_get_value_at_time =    ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_void_p)

cfunc_param_get_derivative =       ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_void_p)

cfunc_param_get_integral =         ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_void_p)

cfunc_param_set_value =            ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int)

cfunc_param_set_value_at_time =    ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_double,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int)

cfunc_param_get_num_keys =         ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.POINTER(ctypes.c_uint))

cfunc_param_get_key_time =         ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_uint,
                                                    ctypes.POINTER(ctypes.c_double))

cfunc_param_get_key_index =        ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.c_int,
                                                    ctypes.POINTER(ctypes.c_int))

cfunc_param_delete_key =           ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double)

cfunc_param_delete_all_keys =      ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p)

cfunc_param_copy =                 ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_void_p,
                                                    ctypes.c_double,
                                                    ctypes.POINTER(ctypes.c_int))

cfunc_param_edit_begin =           ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p,
                                                    ctypes.c_char_p)

cfunc_param_edit_end =             ctypes.CFUNCTYPE(ctypes.c_int,
                                                    ctypes.c_void_p)

class CStructOfxParameterSuite(ctypes.Structure):
     _fields_ = [('paramDefine',            cfunc_param_define),
                 ('paramGetHandle',         cfunc_param_get_handle),
                 ('paramSetGetPropertySet', cfunc_param_set_get_property_set),
                 ('paramGetPropertySet',    cfunc_param_get_property_set),
                 ('paramGetValue',          cfunc_param_get_value),
                 ('paramGetValueAtTime',    cfunc_param_get_value_at_time),
                 ('paramGetDerivative',     cfunc_param_get_derivative),
                 ('paramGetIntegral',       cfunc_param_get_integral),
                 ('paramSetValue',          cfunc_param_set_value),
                 ('paramSetValueAtTime',    cfunc_param_set_value_at_time),
                 ('paramGetNumKeys',        cfunc_param_get_num_keys),
                 ('paramGetKeyTime',        cfunc_param_get_key_time),
                 ('paramGetKeyIndex',       cfunc_param_get_key_index),
                 ('paramDeleteKey',         cfunc_param_delete_key),
                 ('paramDeleteAllKeys',     cfunc_param_delete_all_keys),
                 ('paramCopy',              cfunc_param_copy),
                 ('paramEditBegin',         cfunc_param_edit_begin),
                 ('paramEditEnd',           cfunc_param_edit_end)]

########################################################################################
#
# CTYPE Image Effect Suite functions and structure
#
########################################################################################

cfunc_get_property_set =              ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_get_param_set =                 ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_clip_define =                   ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.c_char_p,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_clip_get_handle =               ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.c_char_p,
                                                       ctypes.POINTER(ctypes.c_void_p),
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_clip_get_property_set =         ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_clip_get_image =                ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.c_double,
                                                       ctypes.c_void_p,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_clip_release_image =            ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p)

cfunc_clip_get_region_of_definition = ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.c_double,
                                                       ctypes.c_void_p)

cfunc_abort =                         ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p)

cfunc_image_memory_alloc =            ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.c_int,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_image_memory_free =             ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p)

cfunc_image_memory_lock =             ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p,
                                                       ctypes.POINTER(ctypes.c_void_p))

cfunc_image_memory_unlock =           ctypes.CFUNCTYPE(ctypes.c_int,
                                                       ctypes.c_void_p)

class CStructOfxImageEffectSuite(ctypes.Structure):
     _fields_ = [('getPropertySet',            cfunc_get_property_set),
                 ('getParamSet',               cfunc_get_param_set),
                 ('clipDefine',                cfunc_clip_define),
                 ('clipGetHandle',             cfunc_clip_get_handle),
                 ('clipGetPropertySet',        cfunc_clip_get_property_set),
                 ('clipGetImage',              cfunc_clip_get_image),
                 ('clipReleaseImage',          cfunc_clip_release_image),
                 ('clipGetRegionOfDefinition', cfunc_clip_get_region_of_definition),
                 ('abort',                     cfunc_abort),
                 ('imageMemoryAlloc',          cfunc_image_memory_alloc),
                 ('imageMemoryFree',           cfunc_image_memory_free),
                 ('imageMemoryLock',           cfunc_image_memory_lock),
                 ('imageMemoryUnlock',         cfunc_image_memory_unlock)]

########################################################################################
#
# CTYPE Memory Suite functions and structure
#
########################################################################################

cfunc_memory_alloc = ctypes.CFUNCTYPE(ctypes.c_int,
                                      ctypes.c_void_p,
                                      ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_void_p))

cfunc_memory_free =  ctypes.CFUNCTYPE(ctypes.c_int,
                                      ctypes.c_void_p)

class CStructOfxMemorySuite(ctypes.Structure):
     _fields_ = [('memoryAlloc', cfunc_memory_alloc),
                 ('memoryFree',  cfunc_memory_free)]

########################################################################################
#
# CTYPE Thread Suite functions and structure
#
########################################################################################

cfunc_thread_function = ctypes.CFUNCTYPE(ctypes.c_int,
                                         ctypes.c_uint,
                                         ctypes.c_uint,
                                         ctypes.c_void_p)

cfunc_multi_thread =  ctypes.CFUNCTYPE(ctypes.c_int,
                                       ctypes.c_void_p,
                                       ctypes.c_uint,
                                       ctypes.c_void_p)

cfunc_multi_thread_num_cpus = ctypes.CFUNCTYPE(ctypes.c_int,
                                               ctypes.POINTER(ctypes.c_uint))

cfunc_multi_thread_index = ctypes.CFUNCTYPE(ctypes.c_int,
                                            ctypes.POINTER(ctypes.c_uint)) 

cfunc_multi_thread_is_spawned_thread = ctypes.CFUNCTYPE(ctypes.c_int)

cfunc_mutex_create = ctypes.CFUNCTYPE(ctypes.c_int,
                                      ctypes.POINTER(ctypes.c_void_p),
                                      ctypes.c_int)

cfunc_mutex_destroy = ctypes.CFUNCTYPE(ctypes.c_int,
                                       ctypes.c_void_p)

cfunc_mutex_lock = ctypes.CFUNCTYPE(ctypes.c_int,
                                    ctypes.c_void_p)

cfunc_mutex_unlock = ctypes.CFUNCTYPE(ctypes.c_int,
                                      ctypes.c_void_p)

cfunc_mutex_try_lock = ctypes.CFUNCTYPE(ctypes.c_int,
                                        ctypes.c_void_p)

class CStructOfxMultiThreadSuite(ctypes.Structure):
     _fields_ = [('multiThread', cfunc_multi_thread),
                 ('multiThreadNumCPUs', cfunc_multi_thread_num_cpus),
                 ('multiThreadIndex', cfunc_multi_thread_index),
                 ('multiThreadIsSpawnedThread', cfunc_multi_thread_is_spawned_thread),
                 ('mutexCreate)(OfxMutexHandle', cfunc_mutex_create),
                 ('mutexDestroy', cfunc_mutex_destroy),
                 ('mutexLock', cfunc_mutex_lock),
                 ('mutexUnLock', cfunc_mutex_unlock),
                 ('mutexTryLock', cfunc_mutex_try_lock)]

########################################################################################
#
# CTYPE Message Suite functions and structure
#
########################################################################################

cfunc_message = ctypes.CFUNCTYPE(ctypes.c_int,
                                 ctypes.c_void_p,
                                 ctypes.c_char_p,
                                 ctypes.c_char_p)

cfunc_set_persistent_message =  ctypes.CFUNCTYPE(ctypes.c_int,
                                                 ctypes.c_void_p,
                                                 ctypes.c_char_p,
                                                 ctypes.c_char_p)

cfunc_clear_persistent_message = ctypes.CFUNCTYPE(ctypes.c_int,
                                                  ctypes.c_void_p)

class CStructOfxMessageSuite(ctypes.Structure):
     _fields_ = [('message', cfunc_message),
                 ('setPersistentMessage', cfunc_set_persistent_message),
                 ('clearPersistentMessage', cfunc_clear_persistent_message)]




