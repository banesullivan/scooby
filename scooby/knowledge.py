"""
A module for storing the path to a version string/variable for many of the
common packages in the Python stack that have something other than a
``__version__`` attribute.
"""
try:
    import psutil
except ImportError:
    psutil = False

try:
    import mkl
except ImportError:
    mkl = False

try:
    import numexpr
except ImportError:
    numexpr = False

# Get available RAM, if available
if psutil:
    tmem = psutil.virtual_memory().total
    TOTAL_RAM = '{:.1f} GB'.format(tmem / (1024.0 ** 3))
else:
    TOTAL_RAM = False

# Get mkl info from numexpr or mkl, if available
if mkl:
    MKL_INFO = mkl.get_version_string()
elif numexpr:
    MKL_INFO = numexpr.get_vml_version()
else:
    MKL_INFO = False


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
