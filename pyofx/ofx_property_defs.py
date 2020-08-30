#! /usr/bin/python3
#
# Copyright 2020 by David Barker.
# All rights reserved.
# This file is part of pyofx the Python3 based OpenFX plugin render host,
# and is released under the "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

OFX_PROPERTY_DEFS = {
    'OfxImageClipPropConnected': {
        'param_type':   'int',
        'dimensions':   1, 
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageClipPropContinuousSamples': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageClipPropFieldExtraction': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxImageFieldDoubled',
        'valid_values': [
            'OfxImageFieldBoth',
            'OfxImageFieldSingle',
            'OfxImageFieldDoubled'
            ]
    },
    'OfxImageClipPropFieldOrder': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxImageFieldNone',
        'valid_values': [
            'OfxImageFieldNone',
            'OfxImageFieldLower',
            'OfxImageFieldUpper'
            ]
    },
    'OfxImageClipPropIsMask': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageClipPropOptional': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageClipPropUnmappedComponents': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageComponentNone',
            'OfxImageComponentRGBA',
            'OfxImageComponentRGB',
            'OfxImageComponentAlpha'
            ]
    },
    'OfxImageClipPropUnmappedPixelDepth': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxBitDepthNone',
            'OfxBitDepthByte',
            'OfxBitDepthShort',
            'OfxBitDepthHalf',
            'OfxBitDepthFloat'
            ]
    },
    'OfxImageEffectFrameVarying': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectHostPropIsBackground': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectHostPropNativeOrigin': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageEffectHostPropNativeOriginBottomLeft',
            'OfxImageEffectHostPropNativeOriginTopLeft',
            'OfxImageEffectHostPropNativeOriginCenter'
            ]
    },
    'OfxImageEffectInstancePropEffectDuration': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectInstancePropSequentialRender': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1, 2]
    },
    'OfxImageEffectPluginPropFieldRenderTwiceAlways': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPluginPropGrouping': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      '',
        'valid_values': None
    },
    'OfxImageEffectPluginPropHostFrameThreading': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPluginPropOverlayInteractV1': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxImageEffectPluginPropSingleInstance': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPluginRenderThreadSafety': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxImageEffectRenderInstanceSafe',
        'valid_values': [
            'OfxImageEffectRenderUnsafe',
            'OfxImageEffectRenderInstanceSafe',
            'OfxImageEffectRenderFullySafe'
            ]
    },
    'OfxImageEffectPropClipPreferencesSlaveParam': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropComponents': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageComponentNone',
            'OfxImageComponentRGBA',
            'OfxImageComponentRGB',
            'OfxImageComponentAlpha'
            ]
    },
    'OfxImageEffectPropContext': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageEffectContextGenerator',
            'OfxImageEffectContextFilter',
            'OfxImageEffectContextTransition',
            'OfxImageEffectContextPaint',
            'OfxImageEffectContextGeneral',
            'OfxImageEffectContextRetimer'
            ]
    },
    'OfxImageEffectPropFieldToRender': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageFieldNone',
            'OfxImageFieldBoth',
            'OfxImageFieldLower',
            'OfxImageFieldUpper'
            ]
    },
    'OfxImageEffectPropFrameRange': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropFrameRate': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropFrameStep': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropInteractiveRenderStatus': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropOpenGLEnabled': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropOpenGLRenderSupported': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'false',
        'valid_values': [
            'false',
            'true',
            'needed'
            ]
    },
    'OfxImageEffectPropOpenGLTextureIndex': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropOpenGLTextureTarget': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropPixelDepth': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxBitDepthNone',
            'OfxBitDepthByte',
            'OfxBitDepthShort',
            'OfxBitDepthHalf',
            'OfxBitDepthFloat'
            ]
    },
    'OfxImageEffectPropPluginHandle': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxImageEffectPropPreMultiplication': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageOpaque',
            'OfxImagePreMultiplied',
            'OfxImageUnPreMultiplied'
            ]
    },
    'OfxImageEffectPropProjectExtent': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropProjectOffset': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropPixelAspectRatio': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropProjectSize': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropRegionOfDefinition': {
        'param_type':  'dbl',
        'dimensions':   4,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropRegionOfInterest': {
        'param_type':  'dbl',
        'dimensions':   4,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropRenderQualityDraft': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropRenderScale': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropRenderWindow': {
        'param_type':  'dbl',
        'dimensions':   4,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropSequentialRenderStatus': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropSetableFielding': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropSetableFrameRate': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropSupportedComponents': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': [
            'OfxImageComponentNone',
            'OfxImageComponentRGBA',
            'OfxImageComponentRGB',
            'OfxImageComponentAlpha'
            ]
    },
    'OfxImageEffectPropSupportedContexts': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': [
            'OfxImageEffectContextGenerator',
            'OfxImageEffectContextFilter',
            'OfxImageEffectContextTransition',
            'OfxImageEffectContextPaint',
            'OfxImageEffectContextGeneral',
            'OfxImageEffectContextRetimer'
            ]
    },
    'OfxImageEffectPropSupportedPixelDepths': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': [
            'OfxBitDepthNone',
            'OfxBitDepthByte',
            'OfxBitDepthShort',
            'OfxBitDepthHalf',
            'OfxBitDepthFloat'
            ]
    },
    'OfxImageEffectPropSupportsMultiResolution': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropMultipleClipDepths': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropSupportsMultipleClipPARs': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropSupportsOverlays': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropSupportsTiles': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropTemporalClipAccess': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxImageEffectPropUnmappedFrameRange': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxImageEffectPropUnmappedFrameRate': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImagePropBounds': {
        'param_type':  'int',
        'dimensions':   4,
        'default':      None,
        'valid_values': None
    },
    'OfxImagePropData': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxImagePropField': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxImageFieldNone',
            'OfxImageFieldBoth',
            'OfxImageFieldLower',
            'OfxImageFieldUpper'
            ]
    },
    'OfxImagePropPixelAspectRatio': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImagePropRegionOfDefinition': {
        'param_type':  'int',
        'dimensions':   4,
        'default':      None,
        'valid_values': None
    },
    'OfxImagePropRowBytes': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxImagePropUniqueIdentifier': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropBackgroundColour': {
        'param_type':  'dbl',
        'dimensions':   3,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropBitDepth': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropHasAlpha': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxInteractPropPenPosition': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropPenPressure': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropPenViewportPosition': {
        'param_type':  'int',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropPixelScale': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropSlaveToParam': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': None
    },
    'OfxInteractPropSuggestedColour': {
        'param_type':  'dbl',
        'dimensions':   3,
        'default':      [1.0, 1.0, 1.0],
        'valid_values': None
    },
    'OfxOpenGLPropPixelDepth': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': [
            'OfxBitDepthNone',
            'OfxBitDepthByte',
            'OfxBitDepthShort',
            'OfxBitDepthHalf',
            'OfxBitDepthFloat'
            ]
    },
    'OfxParamHostPropMaxPages': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxParamHostPropMaxParameters': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxParamHostPropPageRowColumnCount': {
        'param_type':  'int',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxParamHostPropSupportsBooleanAnimation': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamHostPropSupportsChoiceAnimation': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamHostPropSupportsCustomAnimation': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamHostPropSupportsCustomInteract': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamHostPropSupportsParametricAnimation': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamHostPropSupportsStringAnimation': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamPropAnimates': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropCacheInvalidation': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxParamInvalidateValueChange',
        'valid_values': [
            'OfxParamInvalidateValueChange',
            'OfxParamInvalidateValueChangeToEnd',
            'OfxParamInvalidateAll'
            ]
    },
    'OfxParamPropCanUndo': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropChoiceOption': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropCustomCallbackV1': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxParamPropCustomValue': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropDataPtr': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxParamPropDefault': {
        'param_type':  ['int', 'dbl', 'str'],
        'dimensions':   0,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropDefaultCoordinateSystem': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxParamCoordinatesCanonical',
        'valid_values': [
            'OfxParamCoordinatesCanonical',
            'OfxParamCoordinatesNormalised'
            ]
    },
    'OfxParamPropDigits': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      2,
        'valid_values': None
    },
    'OfxParamPropDimensionLabel': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropDisplayMax': {
        'param_type':  ['int', 'dbl'],
        'dimensions':   0,
        'default':      [9999999999],
        'valid_values': None
    },
    'OfxParamPropDisplayMin': {
        'param_type':  ['int', 'dbl'],
        'dimensions':   0,
        'default':      [-9999999999],
        'valid_values': None
    },
    'OfxParamPropDoubleType': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxParamDoubleTypePlain',
        'valid_values': [
            'OfxParamDoubleTypePlain',
            'OfxParamDoubleTypeAngle',
            'OfxParamDoubleTypeScale',
            'OfxParamDoubleTypeTime',
            'OfxParamDoubleTypeAbsoluteTime'
            ]
    },
    'OfxParamPropEnabled': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropEvaluateOnChange': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropGroupOpen': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropHasHostOverlayHandle': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamPropHint': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      '',
        'valid_values': None
    },
    'OfxParamPropIncrement': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      1,
        'valid_values': None
    },
    'OfxParamPropInteractMinimumSize': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      [10, 10],
        'valid_values': None
    },
    'OfxParamPropInteractPreferedSize': {
        'param_type':  'int',
        'dimensions':   2,
        'default':      [10, 10],
        'valid_values': None
    },
    'OfxParamPropInteractSize': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropInteractSizeAspect': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      1,
        'valid_values': None
    },
    'OfxParamPropInteractV1': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxParamPropInterpolationAmount': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropInterpolationTime': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropIsAnimating': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamPropIsAutoKeying': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'OfxParamPropMax': {
        'param_type':  ['int', 'dbl'],
        'dimensions':   0,
        'default':      [9999999999],
        'valid_values': None
    },
    'OfxParamPropMin': {
        'param_type':  ['int', 'dbl'],
        'dimensions':   0,
        'default':      [-9999999999],
        'valid_values': None
    },
    'OfxParamPropPageChild': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      [''],
        'valid_values': None
    },
    'OfxParamPropParametricDimension': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': None
    },
    'OfxParamPropParametricInteractBackground': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxParamPropParametricRange': {
        'param_type':  'dbl',
        'dimensions':   2,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropParametricUIColour': {
        'param_type':  'dbl',
        'dimensions':   3,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropParent': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      '',
        'valid_values': None
    },
    'OfxParamPropPersistant': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropPluginMayWrite': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxParamPropScriptName': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxParamPropSecret': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxParamPropShowTimeMarker': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxParamPropStringFilePathExists': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      1,
        'valid_values': [0, 1]
    },
    'OfxParamPropStringMode': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      'OfxParamStringIsSingleLine',
        'valid_values': [
            'OfxParamStringIsSingleLine',
            'OfxParamStringIsMultiLine',
            'OfxParamStringIsFilePath',
            'OfxParamStringIsDirectoryPath',
            'OfxParamStringIsLabel',
            'OfxParamStringIsRichTextFormat'
            ]
    },
    'OfxParamPropType': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
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
            'OfxParamTypeGroup',
            'OfxParamTypePage',
            'OfxParamTypePushButton'
            ]
    },
    'kOfxParamPropUseHostOverlayHandle': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxPluginPropFilePath': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxPluginPropParamPageOrder': {
        'param_type':  'str',
        'dimensions':   0,
        'default':      [''],
        'valid_values': None
    },
    'OfxPropAPIVersion': {
        'param_type':  'int',
        'dimensions':   0,
        'default':      None,
        'valid_values': None
    },
    'OfxPropChangeReason': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxChangeUserEdited',
            'OfxChangePluginEdited',
            'OfxChangeTime'
            ]
    },
    'OfxPropEffectInstance': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxPropHostOSHandle': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxPropIcon': {
        'param_type':  'str',
        'dimensions':   2,
        'default':      ['', ''],
        'valid_values': None
    },
    'OfxPropInstanceData': {
        'param_type':  'ptr',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxPropIsInteractive': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': [0, 1]
    },
    'kOfxPropKeyString': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'kOfxPropKeySym': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxPropLabel': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxPropLongLabel': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxPropName': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxPropParamSetNeedsSyncing': {
        'param_type':  'int',
        'dimensions':   1,
        'default':      0,
        'valid_values': [0, 1]
    },
    'OfxPropPluginDescription': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      '',
        'valid_values': None
    },
    'OfxPropShortLabel': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    },
    'OfxPropTime': {
        'param_type':  'dbl',
        'dimensions':   1,
        'default':      0,
        'valid_values': None
    },
    'OfxPropType': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': [
            'OfxTypeImageEffectHost',
            'OfxTypeImageEffect',
            'OfxTypeImageEffectInstance',
            'OfxTypeParameter',
            'OfxTypeParameterInstance',
            'OfxTypeClip',
            'OfxTypeImage'
            ]
    },
    'OfxPropVersion': {
        'param_type':  'int',
        'dimensions':   0,
        'default':      [0],
        'valid_values': None
    },
    'OfxPropVersionLabel': {
        'param_type':  'str',
        'dimensions':   1,
        'default':      None,
        'valid_values': None
    }
}


