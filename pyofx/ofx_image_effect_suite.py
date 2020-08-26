#! /usr/bin/python3

import ctypes
import copy
import uuid
from ofx_ctypes import *
from ofx_property_sets import *
from ofx_status_codes import *

class OfxImageEffectSuite():
    def __init__(self, host):
        self._host = host

        self._get_property_set =              cfunc_get_property_set(self._get_property_set_callback)
        self._get_param_set =                 cfunc_get_param_set(self._get_param_set_callback)
        self._clip_define =                   cfunc_clip_define(self._clip_define_callback)
        self._clip_get_handle =               cfunc_clip_get_handle(self._clip_get_handle_callback)
        self._clip_get_property_set =         cfunc_clip_get_property_set(self._clip_get_property_set_callback)
        self._clip_get_image =                cfunc_clip_get_image(self._clip_get_image_callback)
        self._clip_release_image =            cfunc_clip_release_image(self._clip_release_image_callback)
        self._clip_get_region_of_definition = cfunc_clip_get_region_of_definition(self._clip_get_region_of_definition_callback)
        self._abort =                         cfunc_abort(self._abort_callback)
        self._image_memory_alloc =            cfunc_image_memory_alloc(self._image_memory_alloc_callback)
        self._image_memory_free =             cfunc_image_memory_free(self._image_memory_free_callback)
        self._image_memory_lock =             cfunc_image_memory_lock(self._image_memory_lock_callback)
        self._image_memory_unlock =           cfunc_image_memory_unlock(self._image_memory_unlock_callback)

        self._suite = CStructOfxImageEffectSuite(self._get_property_set,
                                                 self._get_param_set,
                                                 self._clip_define,
                                                 self._clip_get_handle,
                                                 self._clip_get_property_set,
                                                 self._clip_get_image,
                                                 self._clip_release_image,
                                                 self._clip_get_region_of_definition,
                                                 self._abort,
                                                 self._image_memory_alloc,
                                                 self._image_memory_free,
                                                 self._image_memory_lock,
                                                 self._image_memory_unlock)

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def create_clip_instance(self, clip_descriptor, instance_id):
        descriptor_id = clip_descriptor['handle'].id.decode("utf-8")
        descriptor_name = descriptor_id.rsplit('.', 1)[1]
        instance_clip_id = '%s.%s'%(instance_id, descriptor_name)

        clip_handle = CStructOfxHandle("OfxTypeClip".encode('utf-8'),
                                                  instance_clip_id.encode('utf-8'))

        return {'handle': clip_handle,
                'ctypes': copy.deepcopy(clip_descriptor['ctypes']) }

    def _decode_handle(self, ctype_handle):
        handle_structure = CStructOfxHandle.from_address(ctype_handle)
        handle_type = handle_structure.property_type.decode("utf-8")
        handle_id = handle_structure.id.decode("utf-8")

        return(handle_type, handle_id)

    def _get_property_set_callback(self, ctype_image_effect_handle, ctype_property_handle):
        ctype_property_handle.contents.value = ctype_image_effect_handle

        return OFX_STATUS_OK

    def _get_param_set_callback(self, ctype_image_effect_handle, ctype_param_set_handle):
        ctype_param_set_handle.contents.value = ctype_image_effect_handle

        return OFX_STATUS_OK

    def _clip_define_callback(self, ctype_image_effect_handle, ctype_name, ctype_property_handle):
        property_set = CStructOfxHandle.from_address(ctype_image_effect_handle)
        property_type = property_set.property_type.decode("utf-8")
        property_id = property_set.id.decode("utf-8")
        plugin_id = property_id.rsplit('.', 1)[0]
        context_id = property_id.rsplit('.', 1)[1]
        name = ctype_name.decode("utf-8")
        clip_id = "%s.%s"%(property_id, name)

        clip_handle = CStructOfxHandle("OfxTypeClip".encode('utf-8'),
                                       clip_id.encode('utf-8'))

        self._host['plugins'][plugin_id]['contexts'][context_id]['clips'][name] = {
            'handle': clip_handle,
            'ctypes': OfxClipProperties(clip_name=name)
            }

        ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(clip_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _clip_get_handle_callback(self, ctype_image_effect_handle, ctype_name, ctype_clip_handle, ctype_property_handle):
        image_effect_set = CStructOfxHandle.from_address(ctype_image_effect_handle)
        image_effect_type = image_effect_set.property_type.decode("utf-8")
        image_effect_id = image_effect_set.id.decode("utf-8")
        clip_name = ctype_name.decode("utf-8")

        clip_handle = self._host['active_plugins'][image_effect_id]['clips'][clip_name]['handle']

        ctype_clip_handle.contents.value = ctypes.cast(ctypes.pointer(clip_handle), ctypes.c_void_p).value

        if ctype_property_handle:
            ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(clip_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _clip_get_property_set_callback(self, ctype_clip_handle, ctype_prop_handle):
        ctype_prop_handle.contents.value = ctype_clip_handle

        return OFX_STATUS_OK

    def _clip_get_image_callback(self, ctype_clip_handle, ctype_time, ctype_region, ctype_image_handle):
        clip_set = CStructOfxHandle.from_address(ctype_clip_handle)
        clip_type = clip_set.property_type.decode("utf-8")
        clip_id = clip_set.id.decode("utf-8")
        active_id = clip_id.rsplit('.', 1)[0]
        clip_name = clip_id.rsplit('.', 1)[1]

        image_handle = self._host['images'][clip_name]['handle']

        ctype_image_handle.contents.value = ctypes.cast(ctypes.pointer(image_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _abort_callback(self, imageEffect):
        # Currently host has no abort state so just return OK
        return OFX_STATUS_OK

    def _image_memory_alloc_callback(self, ctype_instance_handle, ctype_n_bytes, ctype_memory_handle):
        # ignoring the ctype_instance_handle as it often NULL

        memory_buffer = (ctypes.c_byte * ctype_n_bytes)()
        memory_id = str(uuid.uuid1())
        memory_handle = CStructOfxHandle("OfxImageMemoryHandle".encode('utf-8'),
                                         memory_id.encode('utf-8'))

        self._host['memory'][memory_id] = {
            'handle': memory_handle,
            'buffer': memory_buffer,
            'pointer': ctypes.addressof(memory_buffer),
            'size': ctype_n_bytes
            }

        ctype_memory_handle.contents.value = ctypes.cast(ctypes.pointer(memory_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _image_memory_lock_callback(self, ctype_memory_handle, ctype_return_ptr):
        property_set = CStructOfxHandle.from_address(ctype_memory_handle)
        property_type = property_set.property_type.decode("utf-8")
        property_id = property_set.id.decode("utf-8")

        ctype_return_ptr.contents.value = self._host['memory'][property_id]['pointer']

        return OFX_STATUS_OK

    ##################################################################################################################
    #
    # PLACEHOLDERS
    #
    ##################################################################################################################

    def _clip_release_image_callback(self, imageHandle):
        print('PLACEHOLDER clipReleaseImage')
        return OFX_STATUS_FAILED

    def _clip_get_region_of_definition_callback(self, clip, time, bounds):
        print('PLACEHOLDER clipGetRegionOfDefinition')
        return OFX_STATUS_FAILED

    def _image_memory_free_callback(self, memoryHandle):
        print('PLACEHOLDER imageMemoryFree')
        return OFX_STATUS_FAILED

    def _image_memory_unlock_callback(self, memoryHandle):
        print('PLACEHOLDER imageMemoryUnlock')
        return OFX_STATUS_FAILED





