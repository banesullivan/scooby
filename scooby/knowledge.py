"""
A module for storing the path to a version string/variable for many of the
common packages in the Python stack that have something other than a
``__version__`` attribute.
"""

VERSION_ATTRIBUTES = {
    'vtk': 'VTK_VERSION',
    'vtkmodules.all': 'VTK_VERSION',
    'PyQt5': 'Qt.PYQT_VERSION_STR',
}


def get_pyqt5_version():
    """Returns the PyQt5 version"""
    from PyQt5.Qt import PYQT_VERSION_STR
    return PYQT_VERSION_STR


VERSION_METHODS = {
    'PyQt5': get_pyqt5_version,
}


def get_from_knowledge_base(module, name=None):
    """Get version info from a known, different place than __version__."""
    if name is None:
        name = module.__name__
    try:
        attr = VERSION_ATTRIBUTES[name]
        return getattr(module, attr)
    except (KeyError, AttributeError):
        pass
    try:
        method = VERSION_METHODS[name]
        return method()
    except (KeyError, ImportError):
        pass
    return None
