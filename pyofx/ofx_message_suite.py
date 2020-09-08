#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# NOTE: Because of the variadic args in function calls we can't process the messages.
#       All we can do it send notifications that they arrived.

import ctypes
import logging
import ofx_ctypes
import ofx_status_codes

class OfxMessageSuite(object):
    OFX_MESSAGE_FATAL =    "OfxMessageFatal"
    OFX_MESSAGE_ERROR =    "OfxMessageError"
    OFX_MESSAGE_WARNING =  "OfxMessageWarning"
    OFX_MESSAGE_MESSAGE =  "OfxMessageMessage"
    OFX_MESSAGE_LOG =      "OfxMessageLog"
    OFX_MESSAGE_QUESTION = "OfxMessageQuestion"

    def __init__(self):
        self._message =                  ofx_ctypes.cfunc_message(self._message_callback)
        self._set_persistant_message =   ofx_ctypes.cfunc_set_persistent_message(self._set_persistant_message_callback)
        self._clear_persistant_message = ofx_ctypes.cfunc_clear_persistent_message(self._clear_persistant_message_callback)

        self._suite = ofx_ctypes.CStructOfxMessageSuite(
            self._message,
            self._set_persistant_message,
            self._clear_persistant_message
        )

    def get_pointer_as_int(self):
        return ctypes.cast(ctypes.pointer(self._suite), ctypes.c_void_p).value

    def _display_message(self, message_type, handle_id=None):
        if handle_id is not None:
            handle_string = '({})'.format(handle_id)
        else:
            handle_string = ''

        if message_type == OfxMessageSuite.OFX_MESSAGE_FATAL:
            logging.critical('Message from plugin {}'.format(handle_string))
            return ofx_status_codes.OFX_STATUS_OK
        elif message_type == OfxMessageSuite.OFX_MESSAGE_ERROR:
            logging.error('Message from plugin {}'.format(handle_string))
            return ofx_status_codes.OFX_STATUS_OK
        elif message_type == OfxMessageSuite.OFX_MESSAGE_WARNING:
            logging.warning('Message from plugin {}'.format(handle_string))
            return ofx_status_codes.OFX_STATUS_OK
        elif message_type == OfxMessageSuite.OFX_MESSAGE_LOG:
            logging.info('Log message from plugin {}'.format(handle_string))
            return ofx_status_codes.OFX_STATUS_OK
        elif message_type == OfxMessageSuite.OFX_MESSAGE_MESSAGE:
            print('Message from plugin {}'.format(handle_string))
            return ofx_status_codes.OFX_STATUS_OK
        elif message_type == OfxMessageSuite.OFX_MESSAGE_QUESTION:
            print('Question from plugin {} default answer Yes'.format(handle_string))
            return ofx_status_codes.OFX_STATUS_REPLY_YES

        return ofx_status_codes.OFX_STATUS_FAILED

    def _message_callback(self, ctype_handle, ctype_message_type, ctype_message_id, ctype_format):
        # ignoring the ctype_handle as it often NULL

        message_type = ctype_message_type.decode("utf-8")
        return self._display_message(message_type)

    def _set_persistant_message_callback(self, ctype_handle, ctype_message_type, ctype_message_id, ctype_format):
        handle = ofx_ctypes.CStructOfxHandle.from_address(ctype_handle)
        name = handle.name.decode("utf-8")

        message_type = ctype_message_type.decode("utf-8")
        return self._display_message(message_type, name)

    def _clear_persistant_message_callback(self, ctype_handle):
        return ofx_status_codes.OFX_STATUS_OK


