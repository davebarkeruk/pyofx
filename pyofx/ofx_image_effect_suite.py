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

        self._suite = CStructOfxImageEffectSuite(
            self._get_property_set,
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
            self._image_memory_unlock
        )

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def create_clip_instance(self, clip_descriptor, active_uid):
        handle = clip_descriptor['handle']

        clip_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeClipInstance'),
            handle.bundle,
            handle.plugin,
            handle.context,
            ctypes.c_char_p(active_uid.encode("utf-8")),
            handle.name
        )

        return {
            'handle': clip_handle,
            'image' : None,
            'ctypes': copy.deepcopy(clip_descriptor['ctypes'])
        }

    def _get_property_set_callback(self, ctype_image_effect_handle, ctype_property_handle):
        ctype_property_handle.contents.value = ctype_image_effect_handle

        return OFX_STATUS_OK

    def _get_param_set_callback(self, ctype_image_effect_handle, ctype_param_set_handle):
        ctype_param_set_handle.contents.value = ctype_image_effect_handle

        return OFX_STATUS_OK

    def _clip_define_callback(self, ctype_image_effect_handle, ctype_name, ctype_property_handle):
        handle = CStructOfxHandle.from_address(ctype_image_effect_handle)

        clip_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxTypeClip'),
            handle.bundle,
            handle.plugin,
            handle.context,
            handle.active_uid,
            ctype_name
        )

        bundle = handle.bundle.decode("utf-8")
        plugin = handle.plugin.decode("utf-8")
        context = handle.context.decode("utf-8")
        name = ctype_name.decode("utf-8")

        self._host['bundles'][bundle]['plugins'][plugin]['contexts'][context]['clips'][name] = {
            'handle': clip_handle,
            'ctypes': OfxClipProperties(clip_name=name)
        }

        ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(clip_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _clip_get_handle_callback(self, ctype_image_effect_handle, ctype_name, ctype_clip_handle, ctype_property_handle):
        handle = CStructOfxHandle.from_address(ctype_image_effect_handle)
        active_uid = handle.active_uid.decode("utf-8")
        name = ctype_name.decode("utf-8")

        clip_handle = self._host['active']['plugins'][active_uid]['clips'][name]['handle']

        ctype_clip_handle.contents.value = ctypes.cast(ctypes.pointer(clip_handle), ctypes.c_void_p).value

        if ctype_property_handle:
            ctype_property_handle.contents.value = ctypes.cast(ctypes.pointer(clip_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _clip_get_property_set_callback(self, ctype_clip_handle, ctype_prop_handle):
        ctype_prop_handle.contents.value = ctype_clip_handle

        return OFX_STATUS_OK

    def _clip_get_image_callback(self, ctype_clip_handle, ctype_time, ctype_region, ctype_image_handle):
        handle = CStructOfxHandle.from_address(ctype_clip_handle)
        active_uid = handle.active_uid.decode("utf-8")
        name = handle.name.decode("utf-8")

        clip = self._host['active']['plugins'][active_uid]['clips'][name]

        if clip['ctypes'].get('OfxImageClipPropConnected').value == 0:
            return OFX_STATUS_FAILED

        image_handle = clip['image']['handle']

        ctype_image_handle.contents.value = ctypes.cast(ctypes.pointer(image_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _clip_release_image_callback(self, imageHandle):
        # Currently only uses the one image that'll be caught by garbage collection on exit
        # Will need to be changed once more than one frame is rendered
        return OFX_STATUS_OK

    def _abort_callback(self, imageEffect):
        # Currently host has no abort state so just return OK
        return OFX_STATUS_OK

    def _image_memory_alloc_callback(self, ctype_instance_handle, ctype_n_bytes, ctype_memory_handle):
        buffer = (ctypes.c_byte * ctype_n_bytes)()
        pointer = ctypes.addressof(buffer)

        if ctype_instance_handle:
            handle = CStructOfxHandle.from_address(ctype_image_effect_handle)

            memory_handle = CStructOfxHandle(
                ctypes.c_char_p(b'OfxImageMemoryHandle'),
                handle.bundle,
                handle.plugin,
                handle.context,
                handle.active_uid,
                str(pointer).encode('utf-8')
            )
        else:
            memory_handle = CStructOfxHandle(
                ctypes.c_char_p(b'OfxImageMemoryHandle'),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(str(pointer).encode('utf-8'))
            )

        self._host['active']['memory'][str(pointer)] = {
            'handle':     memory_handle,
            'buffer':     buffer,
            'lock_count': 0,
            'pointer':    pointer,
            'size':       ctype_n_bytes
        }

        ctype_memory_handle.contents.value = ctypes.cast(ctypes.pointer(memory_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _image_memory_lock_callback(self, ctype_memory_handle, ctype_return_ptr):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode('utf-8')

        ctype_return_ptr.contents.value = self._host['active']['memory'][name]['pointer']
        self._host['active']['memory'][name]['lock_count'] += 1

        return OFX_STATUS_OK

    def _image_memory_free_callback(self, ctype_memory_handle):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode('utf-8')

        if self._host['active']['memory'][name]['lock_count'] < 1:
            del(self._host['active']['memory'][name])
        else:
            print('WARNING: Trying to delete imageMemory that is still locked')
            return OFX_STATUS_FAILED

        return OFX_STATUS_OK

    def _image_memory_unlock_callback(self, ctype_memory_handle):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode('utf-8')

        if self._host['active']['memory'][name]['lock_count'] > 0:
            self._host['active']['memory'][name]['lock_count'] -= 1

        return OFX_STATUS_OK

    ##################################################################################################################
    #
    # PLACEHOLDERS
    #
    ##################################################################################################################

    def _clip_get_region_of_definition_callback(self, clip, time, bounds):
        print('PLACEHOLDER clipGetRegionOfDefinition')
        return OFX_STATUS_FAILED







