#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import ctypes
import logging
import ofx_property_defs

class OfxPropertySet(object):
    def __init__(self):
        self._data = {}

    def ptr(self, key, index=None):
        if key in self._data:
            if isinstance(self._data[key], list) and index is not None:
                if 0 <= index < len(self._data[key]):
                    return ctypes.addressof(self._data[key][index])
                else:
                    logging.error('Index {} out of range in {}'.format(index, key))
                    return None
            else:
                return ctypes.addressof(self._data[key])
        else:
            logging.error('{} not in property set'.format(key))
            return None

    def length(self, key):
        if key in self._data:
            field = self._data[key]
            if isinstance(field, list):
                return len(field)
            else:
                return 1
        else:
            logging.error('{} not in property set'.format(key))
            return None

    def update(self, key, property_value, property_type, index=None):
        if property_type == 'int':
            new_value = ctypes.c_int(int(property_value))
        elif property_type == 'dbl':
            new_value = ctypes.c_double(float(property_value))
        elif property_type == 'str':
            new_value = ctypes.create_string_buffer(property_value.encode('utf-8'))
        elif property_type == 'ptr':
            new_value = ctypes.c_ulonglong(int(property_value))
        else:
            logging.error('{} invalid type'.format(property_type))
            return False

        if key in self._data:
            if isinstance(self._data[key], list) and index is not None:
                if 0 <= index < len(self._data[key]):
                    self._data[key][index] = new_value
                else:
                    self._data[key].append(new_value)
            else:
                self._data[key] = new_value

            return True
        else:
            logging.error('{} not in property set'.format(key))
            return False

    def get(self, key, index=None):
        if key in self._data:
            if isinstance(self._data[key], list) and index is not None:
                if 0 <= index < len(self._data[key]):
                    return self._data[key][index]
                else:
                    logging.error('Index {} out of range in {}'.format(index, key))
                    return None
            else:
                return self._data[key]
        else:
            logging.error('{} not in property set'.format(key))
            return None

    def value_as_string(self, key, index=None):
        if key in self._data:
            if isinstance(self._data[key], list) and index is not None:
                if 0 <= index < len(self._data[key]):
                    if 'c_char_Array' in str(type(self._data[key][index])):
                        return ctypes.cast(self._data[key][index].value, ctypes.c_char_p).value.decode('utf-8')
                    else:
                        return str(self._data[key][index].value)
                else:
                    logging.error('Index {} out of range in {}'.format(index, key))
                    return None
            else:
                if 'c_char_Array' in str(type(self._data[key])):
                    return ctypes.cast(self._data[key].value, ctypes.c_char_p).value.decode('utf-8')
                else:
                    return str(self._data[key].value)
        else:
            logging.error('{} not in property set'.format(key))
            return None

    def contains(self, key):
        return key in self._data

    def add(self, key, property_value=None, property_type=None, replace=False):
        if key in self._data and not replace:
            logging.error('{} already in property set'.format(key))
            return False

        if key not in ofx_property_defs.OFX_PROPERTY_DEFS:
            logging.error('{} not a supported OFX property'.format(key))
            return False

        if ofx_property_defs.OFX_PROPERTY_DEFS[key]['default'] is None and property_value is None:
            logging.error('{} requires property_value to be supplied'.format(key))
            return False
        elif property_value is None:
            new_value = ofx_property_defs.OFX_PROPERTY_DEFS[key]['default']
        else:
            new_value = property_value

        if isinstance(ofx_property_defs.OFX_PROPERTY_DEFS[key]['param_type'], list):
            if property_type is None:
                logging.error('{} requires property_type to be supplied'.format(key))
                return False
            if property_type not in ofx_property_defs.OFX_PROPERTY_DEFS[key]['param_type']:
                logging.error('{} does not support property_type {}'.format(key, property_type))
                return False
            new_type = property_type
        else:
            new_type = ofx_property_defs.OFX_PROPERTY_DEFS[key]['param_type']

        if isinstance(new_value, list) and ofx_property_defs.OFX_PROPERTY_DEFS[key]['dimensions'] == 1:
            logging.error('{} does not support list objects'.format(key))
            return False

        if not isinstance(new_value, list) and ofx_property_defs.OFX_PROPERTY_DEFS[key]['dimensions'] != 1:
            logging.error('{} requires a list object'.format(key))
            return False

        if ofx_property_defs.OFX_PROPERTY_DEFS[key]['dimensions'] > 1:
            if ofx_property_defs.OFX_PROPERTY_DEFS[key]['dimensions'] != len(new_value):
                logging.error('len does not match dimensions for {} property'.format(key))
                return False

        if ofx_property_defs.OFX_PROPERTY_DEFS[key]['valid_values'] is not None:
            if isinstance(new_value, list):
                for i in new_value:
                    if i not in ofx_property_defs.OFX_PROPERTY_DEFS[key]['valid_values']:
                        logging.error('{} not a valid value for {} property'.format(i, key))
                        return False
            else:
                if new_value not in ofx_property_defs.OFX_PROPERTY_DEFS[key]['valid_values']:
                    logging.error('{} not a valid value for {} property'.format(new_value, key))
                    return False

        if isinstance(new_value, list):
            if new_type == 'int':
                self._data[key] = [ctypes.c_int(int(i)) for i in new_value]
            elif new_type == 'dbl':
                self._data[key] = [ctypes.c_double(float(i)) for i in new_value]
            elif new_type == 'str':
                self._data[key] = [ctypes.create_string_buffer(i.encode('utf-8')) for i in new_value]
            else:
                logging.error('{} invalid type for multi dimensional property'.format(new_type))
                return False
        else:
            if new_type == 'int':
                self._data[key] = ctypes.c_int(int(new_value))
            elif new_type == 'dbl':
                self._data[key] = ctypes.c_double(float(new_value))
            elif new_type == 'str':
                self._data[key] = ctypes.create_string_buffer(new_value.encode('utf-8'))
            elif new_type == 'ptr':
                self._data[key] = ctypes.c_ulonglong(int(new_value))
            else:
                logging.error('{} invalid type for single dimension property'.format(new_type))
                return False

        return True

class OfxHostProperties(OfxPropertySet):
    def __init__(self):
        super().__init__()

        self.add('OfxPropType', 'OfxTypeImageEffectHost'),
        self.add('OfxImageEffectPropSupportedComponents', ['OfxImageComponentRGBA', 'OfxImageComponentRGB'])
        self.add('OfxImageEffectPropSupportedContexts', ['OfxImageEffectContextFilter','OfxImageEffectContextGeneral'])
        self.add('OfxParamHostPropPageRowColumnCount', [10, 20])
        self.add('OfxPropName', 'pyOfx')
        self.add('OfxPropLabel', 'pyOfx')
        self.add('OfxPropVersion', [0,1])
        self.add('OfxPropVersionLabel', '0.1')
        self.add('OfxPropAPIVersion', [1,4])
        self.add('OfxImageEffectHostPropIsBackground', 0)
        self.add('OfxImageEffectPropSupportsOverlays', 0)
        self.add('OfxImageEffectPropSupportsMultiResolution')
        self.add('OfxImageEffectPropSupportsTiles')
        self.add('OfxImageEffectPropTemporalClipAccess')
        self.add('OfxImageEffectPropMultipleClipDepths', 0)
        self.add('OfxImageEffectPropSupportsMultipleClipPARs')
        self.add('OfxImageEffectPropSetableFrameRate', 0)
        self.add('OfxImageEffectPropSetableFielding', 0)
        self.add('OfxParamHostPropSupportsCustomInteract', 0)
        self.add('OfxParamHostPropSupportsStringAnimation', 0)
        self.add('OfxParamHostPropSupportsChoiceAnimation', 0)
        self.add('OfxParamHostPropSupportsBooleanAnimation', 0)
        self.add('OfxParamHostPropSupportsCustomAnimation', 0)
        self.add('OfxParamHostPropMaxParameters', -1)
        self.add('OfxParamHostPropMaxPages', -1)
        self.add('OfxPropHostOSHandle')
        self.add('OfxParamHostPropSupportsParametricAnimation', 0)
        self.add('OfxImageEffectInstancePropSequentialRender')
        self.add('OfxImageEffectPropOpenGLRenderSupported')
        self.add('OfxImageEffectPropRenderQualityDraft')
        self.add('OfxImageEffectHostPropNativeOrigin', 'OfxImageEffectHostPropNativeOriginBottomLeft')


class OfxEffectProperties(OfxPropertySet):
    def __init__(self, plugin_id):
        super().__init__()

        self.add('OfxPropType', 'OfxTypeImageEffect')
        self.add('OfxPropLabel', plugin_id)
        self.add('OfxPropShortLabel', plugin_id)
        self.add('OfxPropLongLabel', plugin_id)
        self.add('OfxPropVersion', [0,1])
        self.add('OfxPropVersionLabel', '0.1')
        self.add('OfxPropPluginDescription')
        self.add('OfxImageEffectPropSupportedContexts', [])
        self.add('OfxImageEffectPluginPropGrouping')
        self.add('OfxImageEffectPluginPropSingleInstance')
        self.add('OfxImageEffectPluginRenderThreadSafety')
        self.add('OfxImageEffectPluginPropHostFrameThreading')
        self.add('OfxImageEffectPluginPropOverlayInteractV1')
        self.add('OfxImageEffectPropSupportsMultiResolution')
        self.add('OfxImageEffectPropSupportsTiles')
        self.add('OfxImageEffectPropTemporalClipAccess')
        self.add('OfxImageEffectPropSupportedPixelDepths', [])
        self.add('OfxImageEffectPluginPropFieldRenderTwiceAlways')
        self.add('OfxImageEffectPropMultipleClipDepths')
        self.add('OfxImageEffectPropSupportsMultipleClipPARs')
        self.add('OfxImageEffectPropClipPreferencesSlaveParam', [])
        self.add('OfxImageEffectPropOpenGLRenderSupported')
        self.add('OfxPluginPropFilePath', '/path/to/plugin')

class OfxEffectContextProperties(OfxPropertySet):
    def __init__(self, context_string):
        super().__init__()

        self.add('OfxImageEffectPropContext', context_string)

class OfxEffectInstanceProperties(OfxPropertySet):
    def __init__(self, context, width, height):
        super().__init__()

        self.add('OfxPropType', 'OfxTypeImageEffectInstance')
        self.add('OfxImageEffectPropContext', context)
        self.add('OfxPropInstanceData')
        self.add('OfxImageEffectPropProjectSize', [width, height])
        self.add('OfxImageEffectPropProjectOffset', [0.0, 0.0])
        self.add('OfxImageEffectPropProjectExtent', [width, height])
        self.add('OfxImageEffectPropPixelAspectRatio', 1.0)
        self.add('OfxImageEffectInstancePropEffectDuration', 1.0)
        self.add('OfxImageEffectInstancePropSequentialRender')
        self.add('OfxImageEffectPropSupportsTiles')
        self.add('OfxImageEffectPropOpenGLRenderSupported')
        self.add('OfxImageEffectPropFrameRate', 29.97)
        self.add('OfxPropIsInteractive', 0)

class OfxClipProperties(OfxPropertySet):
    def brief_details(self):
        clip_is_optional = int(self._data['OfxImageClipPropOptional'].value) != 0
        return '{:20} {}'.format(
            self.value_as_string('OfxPropName'),
            'Optional' if  clip_is_optional else 'Required'
            )

    def __init__(self, clip_name):
        super().__init__()

        self.add('OfxPropType', 'OfxTypeClip')
        self.add('OfxPropName', clip_name)
        self.add('OfxPropLabel', clip_name)
        self.add('OfxPropShortLabel', clip_name)
        self.add('OfxPropLongLabel', clip_name)
        self.add('OfxImageEffectPropSupportedComponents', [])
        self.add('OfxImageEffectPropTemporalClipAccess')
        self.add('OfxImageClipPropOptional', 0)
        self.add('OfxImageClipPropFieldExtraction')
        self.add('OfxImageClipPropIsMask')
        self.add('OfxImageEffectPropSupportsTiles')

    def add_instance_properties(self):
        self.add('OfxImageEffectPropPixelDepth', 'OfxBitDepthByte')
        self.add('OfxImageEffectPropComponents', 'OfxImageComponentRGBA')
        self.add('OfxImageClipPropUnmappedPixelDepth', 'OfxBitDepthByte')
        self.add('OfxImageClipPropUnmappedComponents', 'OfxImageComponentRGBA')
        self.add('OfxImageEffectPropPreMultiplication', 'OfxImageUnPreMultiplied')
        self.add('OfxImagePropPixelAspectRatio', 1.0)
        self.add('OfxImageEffectPropFrameRate', 29.97),
        self.add('OfxImageEffectPropFrameRange', [1.0, 10.0])
        self.add('OfxImageClipPropFieldOrder', 'OfxImageFieldNone')
        self.add('OfxImageClipPropConnected', 0)
        self.add('OfxImageEffectPropUnmappedFrameRange', [1.0, 10.0])
        self.add('OfxImageEffectPropUnmappedFrameRate', 29.97)
        self.add('OfxImageClipPropContinuousSamples', 0)

class OfxImageProperties(OfxPropertySet):
    def __init__(self, unique_id, data_ptr, width, height):
        super().__init__()

        self.add('OfxPropType', 'OfxTypeImage')
        self.add('OfxImageEffectPropPixelDepth', 'OfxBitDepthByte')
        self.add('OfxImageEffectPropComponents', 'OfxImageComponentRGBA')
        self.add('OfxImageEffectPropPreMultiplication', 'OfxImageUnPreMultiplied')
        self.add('OfxImageEffectPropRenderScale', [1.0, 1.0])
        self.add('OfxImagePropPixelAspectRatio', 1.0)
        self.add('OfxImagePropData', data_ptr)
        self.add('OfxImagePropBounds', [0, 0, width, height])
        self.add('OfxImagePropRegionOfDefinition', [0, 0, width, height])
        self.add('OfxImagePropRowBytes', width * 4)
        self.add('OfxImagePropField', 'OfxImageFieldNone')
        self.add('OfxImagePropUniqueIdentifier', unique_id)

class OfxParameterSetProperties(OfxPropertySet):
    def __init__(self):
        super().__init__()

        self.add('OfxPropParamSetNeedsSyncing', 0)

class OfxParameterProperties(OfxPropertySet):
    _value_param_types = [
        'OfxParamTypeInteger',
        'OfxParamTypeDouble',
        'OfxParamTypeBoolean',
        'OfxParamTypeChoice',
        'OfxParamTypeRGBA',
        'OfxParamTypeRGB',
        'OfxParamTypeDouble2D',
        'OfxParamTypeInteger2D',
        'OfxParamTypeDouble3D',
        'OfxParamTypeInteger3D',
        'OfxParamTypeString',
        'OfxParamTypeCustom',
        'OfxParamTypePushButton'
        ]

    def _is_value_param(self):
        param_type = self.value_as_string('OfxParamPropType')
        return param_type in OfxParameterProperties._value_param_types

    def as_tuple(self):
        if not self._is_value_param():
            return (None, None)

        if self._data['OfxParamPropSecret'].value == 1:
            return (None, None)

        param_type = self.value_as_string('OfxParamPropType')

        if param_type == 'OfxParamTypeInteger':
            return (self.value_as_string('OfxParamPropScriptName'),
                    int(self._data['OfxParamPropDefault'][0].value)
                   )
        elif param_type == 'OfxParamTypeDouble':
            return (self.value_as_string('OfxParamPropScriptName'),
                    float(self._data['OfxParamPropDefault'][0].value)
                   )
        elif param_type == 'OfxParamTypeBoolean':
            return (self.value_as_string('OfxParamPropScriptName'),
                    int(self._data['OfxParamPropDefault'][0].value)
                   )
        elif param_type == 'OfxParamTypeChoice':
            return (self.value_as_string('OfxParamPropScriptName'),
                    int(self._data['OfxParamPropDefault'][0].value)
                   )
        elif param_type == 'OfxParamTypeRGBA':
            return (self.value_as_string('OfxParamPropScriptName'),
                    [float(self._data['OfxParamPropDefault'][0].value),
                     float(self._data['OfxParamPropDefault'][1].value),
                     float(self._data['OfxParamPropDefault'][2].value),
                     float(self._data['OfxParamPropDefault'][3].value)
                    ]
                   )
        elif param_type == 'OfxParamTypeRGB':
            return (self.value_as_string('OfxParamPropScriptName'),
                    [float(self._data['OfxParamPropDefault'][0].value),
                     float(self._data['OfxParamPropDefault'][1].value),
                     float(self._data['OfxParamPropDefault'][2].value)
                    ]
                   )
        elif param_type == 'OfxParamTypeDouble2D':
            return (self.value_as_string('OfxParamPropScriptName'),
                    [float(self._data['OfxParamPropDefault'][0].value),
                     float(self._data['OfxParamPropDefault'][1].value)
                    ]
                   )
        elif param_type == 'OfxParamTypeInteger2D':
            return (self.value_as_string('OfxParamPropScriptName'),
                    [int(self._data['OfxParamPropDefault'][0].value),
                     int(self._data['OfxParamPropDefault'][1].value)
                    ]
                   )
        elif param_type == 'OfxParamTypeDouble3D':
             return (self.value_as_string('OfxParamPropScriptName'),
                     [float(self._data['OfxParamPropDefault'][0].value),
                      float(self._data['OfxParamPropDefault'][1].value),
                      float(self._data['OfxParamPropDefault'][2].value)
                     ]
                    )
        elif param_type == 'OfxParamTypeInteger3D':
             return (self.value_as_string('OfxParamPropScriptName'),
                     [int(self._data['OfxParamPropDefault'][0].value),
                      int(self._data['OfxParamPropDefault'][1].value),
                      int(self._data['OfxParamPropDefault'][2].value)
                     ]
                    )
        elif param_type == 'OfxParamTypeString':
            return (self.value_as_string('OfxParamPropScriptName'),
                    self.value_as_string('OfxParamPropDefault', 0)
                   )

        return (None, None)

    def brief_details(self):
        if not self._is_value_param():
            return None

        if self._data['OfxParamPropSecret'].value == 1:
            return None

        param_type = self.value_as_string('OfxParamPropType')

        if param_type == 'OfxParamTypeInteger':
            return '{:20} {:10} {:>10}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Integer',
                int(self._data['OfxParamPropDefault'][0].value)
                )
        elif param_type == 'OfxParamTypeDouble':
            return '{:20} {:10} {:>14.3f}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Double',
                float(self._data['OfxParamPropDefault'][0].value)
                )
        elif param_type == 'OfxParamTypeBoolean':
            return '{:20} {:10} {:>10}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Boolean',
                int(self._data['OfxParamPropDefault'][0].value),
                )
        elif param_type == 'OfxParamTypeChoice':
            number_of_choices = len(self._data['OfxParamPropChoiceOption'])
            active_choice = int(self._data['OfxParamPropDefault'][0].value)
            desc_string = '{:20} {:10} {:>10}'.format(
                          self.value_as_string('OfxParamPropScriptName'),
                          'Choice',
                          active_choice)
            for choice in range(0, number_of_choices):
                desc_string += '\n{:>43} {}'.format(
                                '->' if choice == active_choice else '  ',
                                self.value_as_string('OfxParamPropChoiceOption', choice)
                                )
            return desc_string
        elif param_type == 'OfxParamTypeRGBA':
            return '{:20} {:10} {:>14.3f}\n{:>46.3f}\n{:>46.3f}\n{:>46.3f}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'RGBA',
                float(self._data['OfxParamPropDefault'][0].value),
                float(self._data['OfxParamPropDefault'][1].value),
                float(self._data['OfxParamPropDefault'][2].value),
                float(self._data['OfxParamPropDefault'][3].value)
                )
        elif param_type == 'OfxParamTypeRGB':
            return '{:20} {:10} {:>14.3f}\n{:>46.3f}\n{:>46.3f}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'RGB',
                float(self._data['OfxParamPropDefault'][0].value),
                float(self._data['OfxParamPropDefault'][1].value),
                float(self._data['OfxParamPropDefault'][2].value)
                )
        elif param_type == 'OfxParamTypeDouble2D':
            return '{:20} {:10} {:>14.3f}\n{:>46.3f}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Double 2D',
                float(self._data['OfxParamPropDefault'][0].value),
                float(self._data['OfxParamPropDefault'][1].value)
                )
        elif param_type == 'OfxParamTypeInteger2D':
            return '{:20} {:10} {:>10}\n{:>42}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Integer 2D',
                int(self._data['OfxParamPropDefault'][0].value),
                int(self._data['OfxParamPropDefault'][1].value)
                )
        elif param_type == 'OfxParamTypeDouble3D':
             return '{:20} {:10} {:>14.3f}\n{:>46.3f}\n{:>46.3f}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Double 3D',
                float(self._data['OfxParamPropDefault'][0].value),
                float(self._data['OfxParamPropDefault'][1].value),
                float(self._data['OfxParamPropDefault'][2].value)
                )
        elif param_type == 'OfxParamTypeInteger3D':
             return '{:20} {:10} {:>10}\n{:>42}\n{:>42}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'Integer 3D',
                int(self._data['OfxParamPropDefault'][0].value),
                int(self._data['OfxParamPropDefault'][1].value),
                int(self._data['OfxParamPropDefault'][2].value)
                )
        elif param_type == 'OfxParamTypeString':
            return '{:20} {:10}        {}'.format(
                self.value_as_string('OfxParamPropScriptName'),
                'String',
                self.value_as_string('OfxParamPropDefault', 0)
                )

        return None

    def __init__(self, param_name, param_type):
        super().__init__()

        self.add('OfxPropType', 'OfxTypeParameter')
        self.add('OfxPropName', param_name)
        self.add('OfxPropLabel', param_name)
        self.add('OfxPropShortLabel', param_name)
        self.add('OfxPropLongLabel', param_name)
        self.add('OfxParamPropType', param_type)
        self.add('OfxParamPropSecret')
        self.add('OfxParamPropHint')
        self.add('OfxParamPropScriptName', param_name)
        self.add('OfxParamPropParent')
        self.add('OfxParamPropEnabled')
        self.add('OfxParamPropDataPtr')
        self.add('OfxPropIcon')

        if param_type == 'OfxParamTypeInteger':
            self._not_group_or_page_params()
            self._value_params(1, 'int')
            self._numeric_params(1, 'int')
        elif param_type == 'OfxParamTypeDouble':
            self._not_group_or_page_params()
            self._value_params(1, 'dbl')
            self._numeric_params(1, 'dbl')
            self._double_params()
            self._double_1d_params()
            self._double_non_normalised_spatial_params()
        elif param_type == 'OfxParamTypeBoolean':
            self._not_group_or_page_params()
            self._value_params(1, 'int')
            self._numeric_params(1, 'int')
        elif param_type == 'OfxParamTypeChoice':
            self._not_group_or_page_params()
            self._value_params(1, 'int')
            self._choice_params()
        elif param_type == 'OfxParamTypeRGBA':
            self._not_group_or_page_params()
            self._value_params(4, 'dbl')
            self._numeric_params(4, 'dbl', 0, 1)
            self._double_params()
        elif param_type == 'OfxParamTypeRGB':
            self._not_group_or_page_params()
            self._value_params(3, 'dbl')
            self._numeric_params(3, 'dbl', 0, 1)
            self._double_params()
        elif param_type == 'OfxParamTypeDouble2D':
            self._not_group_or_page_params()
            self._value_params(2, 'dbl')
            self._numeric_params(2, 'dbl')
            self._double_params()
            self._double_2d_3d_params()
            self._double_non_normalised_spatial_params()
        elif param_type == 'OfxParamTypeInteger2D':
            self._not_group_or_page_params()
            self._value_params(2, 'int') 
            self._numeric_params(2, 'int')
            self._int_2d_3d_params()
        elif param_type == 'OfxParamTypeDouble3D':
            self._not_group_or_page_params()
            self._value_params(3, 'dbl') 
            self._numeric_params(3, 'dbl')
            self._double_params()
            self._double_2d_3d_params()
        elif param_type == 'OfxParamTypeInteger3D':
            self._not_group_or_page_params()
            self._value_params(3, 'int')
            self._numeric_params(3, 'int')
            self._int_2d_3d_params()
        elif param_type == 'OfxParamTypeString':
            self._not_group_or_page_params()
            self._value_params(1, 'str')
            self._string_params()
        elif param_type == 'OfxParamTypeCustom':
            self._not_group_or_page_params()
            self._value_params(1, 'str')
            self._custom_params()
        elif param_type == 'OfxParamTypePushButton':
            self._not_group_or_page_params()
            self._value_params(1, 'int')
        elif param_type == 'OfxParamTypeGroup':
            self._group_params()
        elif param_type == 'OfxParamTypePage':
            self._page_params()
        else:
            logging.error('{} invalid type for parameter'.format(param_type))

    def _group_params(self):
        self.add('OfxParamPropGroupOpen')
        return

    def _not_group_or_page_params(self):
        self.add('OfxParamPropInteractV1')
        self.add('OfxParamPropInteractSize', [0.0, 0.0])
        self.add('OfxParamPropInteractSizeAspect', 1.0)
        self.add('OfxParamPropInteractMinimumSize')
        self.add('OfxParamPropInteractPreferedSize')
        self.add('OfxParamPropHasHostOverlayHandle', 0)
        self.add('kOfxParamPropUseHostOverlayHandle')
        return

    def _value_params(self, param_dimensions, param_type):
        if param_type == 'str':
            param_default = ['none']
        else:
            param_default = [0 for i in range(0, param_dimensions)]

        self.add('OfxParamPropDefault', param_default, param_type)
        self.add('OfxParamPropAnimates')
        self.add('OfxParamPropIsAnimating', 0)
        self.add('OfxParamPropIsAutoKeying', 0)
        self.add('OfxParamPropPersistant')
        self.add('OfxParamPropEvaluateOnChange')
        self.add('OfxParamPropPluginMayWrite')
        self.add('OfxParamPropCacheInvalidation', 'OfxParamInvalidateValueChange')
        self.add('OfxParamPropCanUndo')
        return

    def _numeric_params(self, param_dimensions, param_type, param_min=-99999, param_max=99999):
        min_list = [param_min for i in range(0, param_dimensions)]
        max_list = [param_max for i in range(0, param_dimensions)]

        self.add('OfxParamPropMin', min_list, param_type)
        self.add('OfxParamPropMax', max_list, param_type)
        self.add('OfxParamPropDisplayMin', min_list, param_type)
        self.add('OfxParamPropDisplayMax', max_list, param_type)
        return

    def _double_params(self):
        self.add('OfxParamPropIncrement')
        self.add('OfxParamPropDigits')
        return

    def _double_1d_params(self):
        self.add('OfxParamPropShowTimeMarker')
        self.add('OfxParamPropDoubleType')
        return

    def _double_2d_3d_params(self):
        self.add('OfxParamPropDoubleType', 'OfxParamDoubleTypePlain')
        return

    def _double_non_normalised_spatial_params(self):
        self.add('OfxParamPropDefaultCoordinateSystem')
        return

    def _int_2d_3d_params(self):
        self.add('OfxParamPropDimensionLabel', 'x')
        return

    def _string_params(self):
        self.add('OfxParamPropStringMode')
        self.add('OfxParamPropStringFilePathExists')
        return

    def _choice_params(self):
        self.add('OfxParamPropChoiceOption', [])
        return

    def _custom_params(self):
        self.add('OfxParamPropCustomCallbackV1')
        return

    def _page_params(self):
        self.add('OfxParamPropPageChild')
        return

class OfxSequenceRenderActionProperties(OfxPropertySet):
    def __init__(self):
        super().__init__()

        self.add('OfxImageEffectPropFrameRange', [0.0, 1.0])
        self.add('OfxImageEffectPropFrameStep', 1.0)
        self.add('OfxPropIsInteractive', 0)
        self.add('OfxImageEffectPropRenderScale', [1.0, 1.0])
        self.add('OfxImageEffectPropSequentialRenderStatus', 1)
        self.add('OfxImageEffectPropInteractiveRenderStatus', 0)
        self.add('OfxImageEffectPropOpenGLEnabled', 0)
        self.add('OfxImageEffectPropOpenGLTextureIndex', 0)
        self.add('OfxImageEffectPropOpenGLTextureTarget', 0)

class OfxRenderActionProperties(OfxPropertySet):
    def __init__(self, width, height):
        super().__init__()

        self.add('OfxPropTime', 25)
        self.add('OfxImageEffectPropFieldToRender', 'OfxImageFieldNone')
        self.add('OfxImageEffectPropRenderWindow', [0, 0, width, height])
        self.add('OfxImageEffectPropRenderScale', [1.0, 1.0])
        self.add('OfxImageEffectPropSequentialRenderStatus', 1)
        self.add('OfxImageEffectPropInteractiveRenderStatus', 0)
        self.add('OfxImageEffectPropRenderQualityDraft')
        self.add('OfxImageEffectPropOpenGLEnabled', 0)
        self.add('OfxImageEffectPropOpenGLTextureIndex', 0)
        self.add('OfxImageEffectPropOpenGLTextureTarget', 0)
















