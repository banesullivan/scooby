"""
A module for storing the path to a version string/variable for many of the
common packages in the Python stack.
"""

VERSION_ATTRIBUTES = {
    'numpy' : '__version__',
    'scipy' : '__version__',
    'pyvista' : '__version__',
    'vtk' : 'VTK_VERSION',
    'vtkmodules.all' : 'VTK_VERSION',

}
