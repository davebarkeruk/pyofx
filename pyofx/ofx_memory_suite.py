#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
from ofx_ctypes import *
from ofx_property_sets import *
from ofx_status_codes import *

class OfxMemorySuite(object):
    def __init__(self):
        self._active_memory = {}

        self._memory_alloc = cfunc_memory_alloc(self._memory_alloc_callback)
        self._memory_free =  cfunc_memory_free(self._memory_free_callback)

        self._suite = CStructOfxMemorySuite(self._memory_alloc,
                                            self._memory_free)

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def _memory_alloc_callback(self, ctype_instance_handle, ctype_n_bytes, ctype_memory_pointer):
        # ignoring the ctype_instance_handle as it often NULL

        buffer = (ctypes.c_byte * ctype_n_bytes)()
        pointer = ctypes.addressof(buffer)

        self._active_memory[pointer] = {
            'buffer': buffer,
            'size': ctype_n_bytes
            }

        ctype_memory_pointer.contents.value = pointer

        return OFX_STATUS_OK

    def _memory_free_callback(self, ctype_memory_pointer):
        if ctype_memory_pointer in self._active_memory:
            del(self._active_memory[ctype_memory_pointer])
            return OFX_STATUS_OK
        else:
            return OFX_STATUS_ERR_BAD_HANDLE



