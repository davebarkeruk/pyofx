#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import uuid
import threading
from ofx_ctypes import *
from ofx_property_sets import *
from ofx_status_codes import *

class OfxMultiThreadSuite(object):
    def __init__(self):
        self._active_mutex = {}

        self._multi_thread = cfunc_multi_thread(self._multi_thread_callback)
        self._multi_thread_num_cpus = cfunc_multi_thread_num_cpus(self._multi_thread_num_cpus_callback)
        self._multi_thread_index = cfunc_multi_thread_index(self._multi_thread_index_callback)
        self._multi_thread_is_spawned_thread = cfunc_multi_thread_is_spawned_thread(self._multi_thread_is_spawned_thread_callback)
        self._mutex_create = cfunc_mutex_create(self._mutex_create_callback)
        self._mutex_destroy = cfunc_mutex_destroy(self._mutex_destroy_callback)
        self._mutex_lock = cfunc_mutex_lock(self._mutex_lock_callback)
        self._mutex_unlock = cfunc_mutex_unlock(self._mutex_unlock_callback)
        self._mutex_try_lock = cfunc_mutex_try_lock(self._mutex_try_lock_callback)

        self._suite = CStructOfxMultiThreadSuite(
            self._multi_thread,
            self._multi_thread_num_cpus,
            self._multi_thread_index,
            self._multi_thread_is_spawned_thread,
            self._mutex_create,
            self._mutex_destroy,
            self._mutex_lock,
            self._mutex_unlock,
            self._mutex_try_lock
        )

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def _multi_thread_callback(self, ctype_function, ctype_n_threads, ctype_args):
        thread_func = cfunc_thread_function(ctype_function)

        thread_func(
            ctypes.c_uint(0),
            ctypes.c_uint(1),
            ctypes.c_void_p(ctype_args)
        )

        return OFX_STATUS_OK

    def _multi_thread_num_cpus_callback(self, ctype_n_cpus):
        ctype_n_cpus.contents.value = 1

        return OFX_STATUS_OK

    def _multi_thread_index_callback(self, ctype_index):
        ctype_index.contents.value = 0

        return OFX_STATUS_OK

    def _multi_thread_is_spawned_thread_callback(self):
        return 0

    def _mutex_create_callback(self, ctype_mutex_handle, ctype_lock_count):
        uid = str(uuid.uuid1())
        mutex_handle = CStructOfxHandle(
            ctypes.c_char_p(b'OfxMutex'),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(b''),
            ctypes.c_char_p(uid.encode('utf-8'))
        )

        mutex_semaphore = threading.Semaphore(ctype_lock_count)

        self._active_mutex[uid] = {
            'handle': mutex_handle,
            'semaphore': mutex_semaphore
        }

        ctype_mutex_handle.contents.value = ctypes.cast(ctypes.pointer(mutex_handle), ctypes.c_void_p).value

        return OFX_STATUS_OK

    def _mutex_destroy_callback(self, ctype_mutex_handle):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode("utf-8")

        if mutex_id in self._active_mutex:
            del(self._active_mutex[name])
            return OFX_STATUS_OK
        else:
            return OFX_STATUS_ERR_BAD_HANDLE

    def _mutex_lock_callback(self, ctype_mutex_handle):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode("utf-8")

        if mutex_id in self._active_mutex:
            self._active_mutex[name]['semaphore'].acquire()
            return OFX_STATUS_OK
        else:
            return OFX_STATUS_ERR_BAD_HANDLE

    def _mutex_unlock_callback(self, ctype_mutex_handle):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode("utf-8")

        if mutex_id in self._active_mutex:
            self._active_mutex[name]['semaphore'].release()
            return OFX_STATUS_OK
        else:
            return OFX_STATUS_ERR_BAD_HANDLE

    def _mutex_try_lock_callback(self, ctype_mutex_handle):
        handle = CStructOfxHandle.from_address(ctype_memory_handle)
        name = handle.name.decode("utf-8")

        if mutex_id in self._active_mutex:
            if self._active_mutex[name]['semaphore'].acquire(blocking=False):
                return OFX_STATUS_OK
            else:
                return OFX_STATUS_FAILED
        else:
            return OFX_STATUS_ERR_BAD_HANDLE



