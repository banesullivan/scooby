"""
A module for storing the path to a version string/variable for many of the
common packages in the Python stack that have something other than a
``__version__`` attribute.
"""

VERSION_ATTRIBUTES = {
    'vtk' : 'VTK_VERSION',
    'vtkmodules.all' : 'VTK_VERSION',
}
