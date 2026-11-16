"""Launch Services integration for the bundled macOS application."""
import ctypes
from pathlib import Path
import sys

BUNDLE_ID = 'org.velqora.pdf'
PDF_TYPE = 'com.adobe.pdf'
VIEWER_ROLE = 2
ALL_ROLES = 0xFFFFFFFF
UTF8 = 0x08000100


def app_bundle():
    if sys.platform != 'darwin' or not getattr(sys, 'frozen', False):
        return None
    bundle = Path(sys.executable).resolve().parents[2]
    return bundle if bundle.suffix == '.app' else None


def pdf_handler(make_default=False):
    """Return whether Velqora is the current PDF opener."""
    if app_bundle() is None:
        raise RuntimeError('Open the installed Velqora PDF app to change the default.')
    launch = ctypes.CDLL('/System/Library/Frameworks/CoreServices.framework/CoreServices')
    cf = ctypes.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
    ref = ctypes.c_void_p

    cf.CFStringCreateWithCString.argtypes = [ref, ctypes.c_char_p, ctypes.c_uint32]
    cf.CFStringCreateWithCString.restype = ref
    cf.CFEqual.argtypes = [ref, ref]
    cf.CFEqual.restype = ctypes.c_ubyte
    cf.CFRelease.argtypes = [ref]
    cf.CFRelease.restype = None
    launch.LSCopyDefaultRoleHandlerForContentType.argtypes = [ref, ctypes.c_uint32]
    launch.LSCopyDefaultRoleHandlerForContentType.restype = ref
    launch.LSSetDefaultRoleHandlerForContentType.argtypes = [ref, ctypes.c_uint32, ref]
    launch.LSSetDefaultRoleHandlerForContentType.restype = ctypes.c_int32

    references = []
    try:
        for value in (PDF_TYPE, BUNDLE_ID):
            string = cf.CFStringCreateWithCString(None, value.encode('utf-8'), UTF8)
            if not string:
                raise RuntimeError('Could not allocate a Launch Services string.')
            references.append(string)
        pdf_type, bundle_id = references
        if make_default:
            status = launch.LSSetDefaultRoleHandlerForContentType(pdf_type, ALL_ROLES, bundle_id)
            if status:
                raise RuntimeError(f'macOS returned Launch Services error {status}.')
        current = launch.LSCopyDefaultRoleHandlerForContentType(pdf_type, VIEWER_ROLE)
        if current:
            references.append(current)
            return bool(cf.CFEqual(current, bundle_id))
        return False
    finally:
        for item in references:
            cf.CFRelease(item)
