#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import ofx_ctypes
import ofx_status_codes

class OfxMemorySuite(object):
    def __init__(self, host):
        self._host = {}

        self._memory_alloc = ofx_ctypes.cfunc_memory_alloc(self._memory_alloc_callback)
        self._memory_free =  ofx_ctypes.cfunc_memory_free(self._memory_free_callback)

        self._suite = ofx_ctypes.CStructOfxMemorySuite(
            self._memory_alloc,
            self._memory_free
        )

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def _memory_alloc_callback(self, ctype_instance_handle, ctype_n_bytes, ctype_memory_pointer):
        buffer = (ctypes.c_byte * ctype_n_bytes)()
        pointer = ctypes.addressof(buffer)

        if ctype_instance_handle:
            handle = ofx_ctypes.CStructOfxHandle.from_address(ctype_instance_handle)

            memory_handle = ofx_ctypes.CStructOfxHandle(
                ctypes.c_char_p(b'OfxImageMemoryHandle'),
                handle.bundle,
                handle.plugin,
                handle.context,
                handle.active_uid,
                ctypes.c_char_p(str(pointer).encode('utf-8'))
            )
        else:
            memory_handle = ofx_ctypes.CStructOfxHandle(
                ctypes.c_char_p(b'OfxImageMemoryHandle'),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(b''),
                ctypes.c_char_p(str(pointer).encode('utf-8'))
            )

        self._host['active']['memory'][str(pointer)] = {
            'handle': memory_handle,
            'buffer': buffer,
            'lock_count': 0,
            'pointer': pointer,
            'size': ctype_n_bytes
        }

        ctype_memory_pointer.contents.value = pointer

        return ofx_status_codes.OFX_STATUS_OK

    def _memory_free_callback(self, ctype_memory_pointer):
        if ctype_memory_pointer in self._host['active']['memory']:
            del(self._host['active']['memory'][ctype_memory_pointer])
            return ofx_status_codes.OFX_STATUS_OK
        else:
            return ofx_status_codes.OFX_STATUS_ERR_BAD_HANDLE



