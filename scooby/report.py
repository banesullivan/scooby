"""The main module containing the `Report` class."""

import importlib
import sys
import time
from types import ModuleType

from .knowledge import (
    VERSION_ATTRIBUTES,
    VERSION_METHODS,
    get_filesystem_type,
    in_ipykernel,
    in_ipython,
)

MODULE_NOT_FOUND = 'Module not found'
MODULE_TROUBLE = 'Trouble importing'
VERSION_NOT_FOUND = 'Version unknown'


# Info classes
class PlatformInfo:
    """Internal helper class to access details about the computer platform."""

    @property
    def system(self):
        """Return the system/OS name.

        E.g. ``'Linux'``, ``'Windows'``, or ``'Java'``. An empty string is
        returned if the value cannot be determined.
        """
        return platform().system()

    @property
    def platform(self):
        """Return the platform."""
        return platform().platform()

    @property
    def machine(self):
        """Return the machine type, e.g. 'i386'.

        An empty string is returned if the value cannot be determined.
        """
        return platform().machine()

    @property
    def architecture(self):
        """Return the bit architecture used for the executable."""
        return platform().architecture()[0]

    @property
    def cpu_count(self):
        """Return the number of CPUs in the system."""
        if not hasattr(self, '_cpu_count'):
            import multiprocessing  # lazy-load see PR#85

            self._cpu_count = multiprocessing.cpu_count()
        return self._cpu_count

    @property
    def total_ram(self):
        """Return total RAM info.

        If not available, returns 'unknown'.
        """
        if not hasattr(self, '_total_ram'):

            try:
                import psutil  # lazy-load see PR#85

                tmem = psutil.virtual_memory().total
                self._total_ram = '{:.1f} GiB'.format(tmem / (1024.0**3))
            except ImportError:
                self._total_ram = 'unknown'

        return self._total_ram

    @property
    def mkl_info(self):
        """Return MKL info.

        If not available, returns 'unknown'.
        """
        if not hasattr(self, '_mkl_info'):
            try:
                import mkl  # lazy-load see PR#85

                mkl.get_version_string()
            except (ImportError, AttributeError):
                mkl = False

            try:
                import numexpr  # lazy-load see PR#85

            except ImportError:
                numexpr = False

            # Get mkl info from numexpr or mkl, if available
            if mkl:
                self._mkl_info = mkl.get_version_string()
            elif numexpr:
                self._mkl_info = numexpr.get_vml_version()
            else:
                self._mkl_info = None

        return self._mkl_info

    @property
    def date(self):
        """Return the date formatted as a string."""
        return time.strftime('%a %b %d %H:%M:%S %Y %Z')

    @property
    def filesystem(self):
        """Get the type of the file system at the path of the scooby package."""
        if not hasattr(self, '_filesystem'):
            self._filesystem = get_filesystem_type()
        return self._filesystem


class PythonInfo:
    """Internal helper class to access Python info and package versions."""

    def __init__(self, additional, core, optional, sort):
        """Initialize python info."""
        self._packages = {}  # Holds name of packages and their version
        self._sort = sort

        # Add packages in the following order:
        self._add_packages(additional)  # Provided by the user
        self._add_packages(core)  # Provided by a module dev
        self._add_packages(optional, optional=True)  # Optional packages

    def _add_packages(self, packages, optional=False):
        """Add all packages to list; optional ones only if available."""
        # Ensure arguments are a list
        if isinstance(packages, (str, ModuleType)):
            pckgs = [
                packages,
            ]
        elif packages is None or len(packages) < 1:
            pckgs = list()
        else:
            pckgs = list(packages)

        # Loop over packages
        for pckg in pckgs:
            name, version = get_version(pckg)
            if not (version == MODULE_NOT_FOUND and optional):
                self._packages[name] = version

    @property
    def sys_version(self):
        """Return the system version."""
        return sys.version

    @property
    def python_environment(self):
        """Return the python environment."""
        if in_ipykernel():
            return 'Jupyter'
        elif in_ipython():
            return 'IPython'
        return 'Python'

    @property
    def packages(self):
        """Return versions of all packages.

        Includes available and unavailable/unknown.

        """
        pckg_dict = dict(self._packages)
        if self._sort:
            packages = {}
            for name in sorted(pckg_dict.keys(), key=lambda x: x.lower()):
                packages[name] = pckg_dict[name]
            pckg_dict = packages
        return pckg_dict


# The main Report instance
class Report(PlatformInfo, PythonInfo):
    """Have Scooby report the active Python environment.

    Displays the system information when a ``__repr__`` method is called
    (through outputting or printing).

    Parameters
    ----------
    additional : list(ModuleType), list(str)
        List of packages or package names to add to output information.

    core : list(ModuleType), list(str)
        The core packages to list first.

    optional : list(ModuleType), list(str)
        A list of packages to list if they are available. If not available,
        no warnings or error will be thrown.
        Defaults to ``['numpy', 'scipy', 'IPython', 'matplotlib', 'scooby']``

    ncol : int, optional
        Number of package-columns in html table (no effect in text-version);
        Defaults to 3.

    text_width : int, optional
        The text width for non-HTML display modes.

    sort : bool, optional
        Sort the packages when the report is shown.

    extra_meta : tuple(str, str), optional
        Additional two component pairs of meta information to display.

    max_width : int, optional
        Max-width of html-table. By default None.

    """

    def __init__(
        self,
        additional=None,
        core=None,
        optional=None,
        ncol=4,
        text_width=80,
        sort=False,
        extra_meta=None,
        max_width=None,
    ):
        """Initialize report."""
        # Set default optional packages to investigate
        if optional is None:
            optional = ['numpy', 'scipy', 'IPython', 'matplotlib', 'scooby']

        PythonInfo.__init__(self, additional=additional, core=core, optional=optional, sort=sort)
        self.ncol = int(ncol)
        self.text_width = int(text_width)
        self.max_width = max_width

        if extra_meta is not None:
            if not isinstance(extra_meta, (list, tuple)):
                raise TypeError("`extra_meta` must be a list/tuple of " "key-value pairs.")
            if len(extra_meta) == 2 and isinstance(extra_meta[0], str):
                extra_meta = [extra_meta]
            for meta in extra_meta:
                if not isinstance(meta, (list, tuple)) or len(meta) != 2:
                    raise TypeError("Each chunk of meta info must have two values.")
        else:
            extra_meta = []
        self._extra_meta = extra_meta

    def __repr__(self):
        """Return Plain-text version information."""
        import textwrap  # lazy-load see PR#85

        # Width for text-version
        text = '\n' + self.text_width * '-' + '\n'

        # Date and time info as title
        date_text = '  Date: '
        mult = 0
        indent = len(date_text)
        for txt in textwrap.wrap(self.date, self.text_width - indent):
            date_text += ' ' * mult + txt + '\n'
            mult = indent
        text += date_text + '\n'

        # Get length of longest package: min of 18 and max of 40
        if self._packages:
            row_width = min(40, max(18, len(max(self._packages.keys(), key=len))))
        else:
            row_width = 18

        # Platform/OS details
        repr_dict = self.to_dict()
        for key in ['OS', 'CPU(s)', 'Machine', 'Architecture', 'RAM', 'Environment', 'File system']:
            if key in repr_dict:
                text += f'{key:>{row_width}} : {repr_dict[key]}\n'
        for key, value in self._extra_meta:
            text += f'{key:>{row_width}} : {value}\n'

        # Python details
        text += '\n'
        for txt in textwrap.wrap('Python ' + self.sys_version, self.text_width - 4):
            text += '  ' + txt + '\n'
        if self._packages:
            text += '\n'

        # Loop over packages
        for name, version in self._packages.items():
            text += f'{name:>{row_width}} : {version}\n'

        # MKL details
        if self.mkl_info:
            text += '\n'
            for txt in textwrap.wrap(self.mkl_info, self.text_width - 4):
                text += '  ' + txt + '\n'

        # Finish
        text += self.text_width * '-'

        return text

    def _repr_html_(self):
        """Return HTML-rendered version information."""
        # Define html-styles
        border = "border: 1px solid;'"

        def colspan(html, txt, ncol, nrow):
            r"""Print txt in a row spanning whole table."""
            html += "  <tr>\n"
            html += "     <td style='"
            if ncol == 1:
                html += "text-align: left; "
            else:
                html += "text-align: center; "
            if nrow == 0:
                html += "font-weight: bold; font-size: 1.2em; "
            html += border + " colspan='"
            html += f"{2 * ncol}'>{txt}</td>\n"
            html += "  </tr>\n"
            return html

        def cols(html, version, name, ncol, i):
            r"""Print package information in two cells."""
            # Check if we have to start a new row
            if i > 0 and i % ncol == 0:
                html += "  </tr>\n"
                html += "  <tr>\n"

            align = "left" if ncol == 1 else "right"
            html += f"    <td style='text-align: {align};"
            html += " " + border + ">%s</td>\n" % name

            html += "    <td style='text-align: left; "
            html += border + ">%s</td>\n" % version

            return html, i + 1

        # Start html-table
        html = "<table style='border: 1.5px solid;"
        if self.max_width:
            html += f" max-width: {self.max_width}px;"
        html += "'>\n"

        # Date and time info as title
        html = colspan(html, self.date, self.ncol, 0)

        # Platform/OS details
        html += "  <tr>\n"
        repr_dict = self.to_dict()
        i = 0
        for key in ['OS', 'CPU(s)', 'Machine', 'Architecture', 'RAM', 'Environment', "File system"]:
            if key in repr_dict:
                html, i = cols(html, repr_dict[key], key, self.ncol, i)
        for meta in self._extra_meta:
            html, i = cols(html, meta[1], meta[0], self.ncol, i)
        # Finish row
        html += "  </tr>\n"

        # Python details
        html = colspan(html, 'Python ' + self.sys_version, self.ncol, 1)
        html += "  <tr>\n"

        # Loop over packages
        i = 0  # Reset count for rows.
        for name, version in self.packages.items():
            html, i = cols(html, version, name, self.ncol, i)
        # Fill up the row
        while i % self.ncol != 0:
            html += "    <td style= " + border + "></td>\n"
            html += "    <td style= " + border + "></td>\n"
            i += 1
        # Finish row
        html += "  </tr>\n"

        # MKL details
        if self.mkl_info:
            html = colspan(html, self.mkl_info, self.ncol, 2)

        # Finish
        html += "</table>"

        return html

    def to_dict(self):
        """Return report as dict for storage."""
        out = {}

        # Date and time info
        out['Date'] = self.date

        # Platform/OS details
        out['OS'] = self.system
        out['CPU(s)'] = str(self.cpu_count)
        out['Machine'] = self.machine
        out['Architecture'] = self.architecture
        if self.filesystem:
            out['File system'] = self.filesystem
        if self.total_ram != 'unknown':
            out['RAM'] = self.total_ram
        out['Environment'] = self.python_environment
        for meta in self._extra_meta:
            out[meta[1]] = meta[0]

        # Python details
        out['Python'] = self.sys_version

        # Loop over packages
        for name, version in self._packages.items():
            out[name] = version

        # MKL details
        if self.mkl_info:
            out['MKL'] = self.mkl_info

        return out


# This functionaliy might also be of interest on its own.
def get_version(module):
    """Get the version of ``module`` by passing the package or it's name.

    Parameters
    ----------
    module : str or module
        Name of a module to import or the module itself.


    Returns
    -------
    name : str
        Package name

    version : str or None
        Version of module.
    """
    # module is (1) a string or (2) a module.
    # If (1), we have to load it, if (2), we have to get its name.
    if isinstance(module, str):  # Case 1: module is a string; import
        name = module  # The name is stored in module in this case.

        # Import module `name`; set to None if it fails.
        try:
            module = importlib.import_module(name)
        except ImportError:
            module = None
        except:  # noqa
            return name, MODULE_TROUBLE

    elif isinstance(module, ModuleType):  # Case 2: module is module; get name
        name = module.__name__

    else:  # If not str nor module raise error
        raise TypeError("Cannot fetch version from type " "({})".format(type(module)))

    # Now get the version info from the module
    if module is None:
        return name, MODULE_NOT_FOUND
    else:

        # Try common version names.
        for v_string in ('__version__', 'version'):
            try:
                return name, getattr(module, v_string)
            except AttributeError:
                pass

        # Try the VERSION_ATTRIBUTES library
        try:
            attr = VERSION_ATTRIBUTES[name]
            return name, getattr(module, attr)
        except (KeyError, AttributeError):
            pass

        # Try the VERSION_METHODS library
        try:
            method = VERSION_METHODS[name]
            return name, method()
        except (KeyError, ImportError):
            pass

        # If not found, return VERSION_NOT_FOUND
        return name, VERSION_NOT_FOUND


def platform():
    """Return platform as lazy load; see PR#85."""
    import platform

    return platform
