"""The knowledge base.

Knowledge
=========

It contains, for instance, known odd locations of version information for
particular modules (``VERSION_ATTRIBUTES``, ``VERSION_METHODS``)

"""

from __future__ import annotations

from pathlib import Path
import sys
import sysconfig
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable

PACKAGE_ALIASES = {
    'vtkmodules': 'vtk',
    'vtkmodules.all': 'vtk',
}

# Define unusual version locations
VERSION_ATTRIBUTES = {
    'PyQt5': 'Qt.PYQT_VERSION_STR',
    'sip': 'SIP_VERSION_STR',
}


def get_pyqt5_version() -> str:
    """Return the PyQt5 version."""
    try:
        from PyQt5.Qt import PYQT_VERSION_STR
    except ImportError:
        return 'Version unknown'

    return PYQT_VERSION_STR


VERSION_METHODS: dict[str, Callable[[], str]] = {
    'PyQt5': get_pyqt5_version,
}


# Check the environments
def in_ipython() -> bool:
    """Check if we are in a IPython environment.

    Returns
    -------
    bool : True
        ``True`` when in an IPython environment.

    """
    try:
        __IPYTHON__  # noqa: B018
    except NameError:
        return False
    else:
        return True


def in_ipykernel() -> bool:
    """Check if in a ipykernel (most likely Jupyter) environment.

    Warning:
    -------
    There is no way to tell if the code is being executed in a notebook
    (Jupyter Notebook or Jupyter Lab) or a kernel is used but executed in a
    QtConsole, or in an IPython console, or any other frontend GUI. However, if
    `in_ipykernel` returns True, you are most likely in a Jupyter Notebook/Lab,
    just keep it in mind that there are other possibilities.

    Returns:
    -------
    bool : True if using an ipykernel

    """
    ipykernel = False
    if in_ipython():
        try:
            ipykernel: bool = type(get_ipython()).__module__.startswith('ipykernel.')
        except NameError:
            pass
    return ipykernel


def get_standard_lib_modules() -> set[str]:
    """Return a set of the names of all modules in the standard library."""
    site_path = Path(sysconfig.get_path('stdlib'))
    if getattr(sys, 'frozen', False):  # within pyinstaller
        lib_path = site_path / '..'
        if lib_path.is_dir():
            names = lib_path.iterdir()
            stdlib_pkgs = {p.stem for p in names if p.suffix == '.py'}
        else:
            stdlib_pkgs = {}

    else:
        names = site_path.iterdir()
        stdlib_pkgs = {p.stem if p.suffix == '.py' else p.name for p in names}

    return {
        'python',
        'sys',
        '__builtin__',
        '__builtins__',
        'builtins',
        'session',
        'math',
        'itertools',
        'binascii',
        'array',
        'atexit',
        'fcntl',
        'errno',
        'gc',
        'time',
        'unicodedata',
        'mmap',
    }.union(stdlib_pkgs)


def version_tuple(v: str) -> tuple[int, ...]:
    """Convert a version string to a tuple containing ints.

    Non-numeric version strings will be converted to 0.  For example:
    ``'0.28.0dev0'`` will be converted to ``'0.28.0'``

    Returns
    -------
    ver_tuple : tuple
        Length 3 tuple representing the major, minor, and patch
        version.

    """
    split_v = v.split('.')
    while len(split_v) < 3:
        split_v.append('0')

    if len(split_v) > 3:
        msg = 'Version strings containing more than three parts cannot be parsed'
        raise ValueError(msg)

    vals: list[int] = []
    for item in split_v:
        if item.isnumeric():
            vals.append(int(item))
        else:
            vals.append(0)

    return tuple(vals)


def meets_version(version: str, meets: str) -> bool:
    """Check if a version string meets a minimum version.

    This is a simplified way to compare version strings. For a more robust
    tool, please check out the ``packaging`` library:

    https://github.com/pypa/packaging

    Parameters
    ----------
    version : str
        Version string.  For example ``'0.25.1'``.

    meets : str
        Version string.  For example ``'0.25.2'``.

    Returns
    -------
    newer : bool
        True if version ``version`` is greater or equal to version ``meets``.

    Examples
    --------
    >>> meets_version('0.25.1', '0.25.2')
    False

    >>> meets_version('0.26.0', '0.25.2')
    True

    """
    va = version_tuple(version)
    vb = version_tuple(meets)

    if len(va) != len(vb):
        msg = 'Versions are not comparable.'
        raise AssertionError(msg)

    for i in range(len(va)):
        if va[i] > vb[i]:
            return True
        if va[i] < vb[i]:
            return False

    # Arrived here if same version
    return True


def get_filesystem_type() -> str | Literal[False]:
    """Get the type of the file system at the path of the scooby package."""
    try:
        import psutil  # lazy-load see PR#85
    except ImportError:
        psutil = False
    from pathlib import Path  # lazy-load see PR#85
    import platform  # lazy-load see PR#85

    # Skip Windows due to https://github.com/banesullivan/scooby/issues/75
    fs_type: str | Literal[False]
    if psutil and platform.system() != 'Windows':
        # Code by https://stackoverflow.com/a/35291824/10504481
        my_path = str(Path(__file__).resolve())
        best_match = ''
        fs_type = ''
        for part in psutil.disk_partitions():
            if my_path.startswith(part.mountpoint) and len(best_match) < len(part.mountpoint):
                fs_type = part.fstype
                best_match = part.mountpoint
    else:
        fs_type = False
    return fs_type
