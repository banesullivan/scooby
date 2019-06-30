import importlib
import multiprocessing
import platform
import sys
import textwrap
import time
from types import ModuleType

from scooby.extras import MKL_INFO, TOTAL_RAM, sort_dictionary
from scooby.knowledge import get_from_knowledge_base
from scooby.mysteries import in_ipykernel, in_ipython


class PlatformInfo:
    """Internal helper class to access details about the computer platform."""

    @property
    def system(self):
        """Returns the system/OS name.
        E.g. ``'Linux'``, ``'Windows'``, or ``'Java'``. An empty string is
        returned if the value cannot be determined.
        """
        return platform.system()

    @property
    def platform(self):
        return platform.platform()

    @property
    def machine(self):
        """Returns the machine type, e.g. 'i386'
        An empty string is returned if the value cannot be determined.
        """
        return platform.machine()

    @property
    def architecture(self):
        """bit architecture used for the executable"""
        return platform.architecture()[0]

    @property
    def cpu_count(self):
        """Return the number of CPUs in the system.
        """
        return multiprocessing.cpu_count()

    @property
    def total_ram(self):
        """Return total RAM info.

        If not available, returns 'unknown'.
        """
        if TOTAL_RAM:
            return TOTAL_RAM
        return 'unknown'

    @property
    def date(self):
        return time.strftime('%a %b %d %H:%M:%S %Y %Z')


class PythonInfo:
    """Internal helper class to access Python info and package versions."""

    def __init__(self, additional, core, optional, sort):
        self._packages = {}  # Holds name of packages and their version
        self._sort = sort

        # Add packages in the following order:
        self.add_packages(additional)               # Provided by the user
        self.add_packages(core)                     # Provided by a module dev
        self.add_packages(optional, optional=True)  # Optional packages

    def add_packages(self, packages, optional=False):
        """Add all packages to list; optional ones only if available."""

        # Ensure arguments are a list
        if isinstance(packages, (str, ModuleType)):
            pckgs = [packages, ]
        elif packages is None or len(packages) < 1:
            pckgs = list()
        else:
            pckgs = list(packages)

        # Loop over packages
        for pckg in pckgs:
            self.get_version(pckg, optional)

    def get_version(self, pckg, optional):
        """Get the version of a package by passing the package or it's name"""

        if isinstance(pckg, str):  # Case 1: pckg is a string; import it
            name = pckg
            pckg = self._safe_import_by_name(pckg)

            # Return if we cannot load the module and it is an optional one
            if pckg is None and optional:
                return

        elif isinstance(pckg, ModuleType):  # Case 2: pckg is module; get name

            # Get the name of the package.
            try:
                name = pckg.__name__
            except AttributeError:
                name = str(pckg).split("'")[1]

        else:
            raise TypeError("Cannot fetch version from type "
                            "({})".format(type(pckg)))

        # Now get the version info from the module
        if pckg is None:
            version = 'Could not import'
        else:
            version = get_from_knowledge_base(pckg, name=name)
            if version is None:
                try:
                    version = pckg.__version__
                except AttributeError:
                    version = 'Version unknown'

        # Add the version to the package reference
        self._packages[name] = version

    def _safe_import_by_name(self, name, optional=False):
        """Import module `name`; returns None if it fails."""
        try:
            module = importlib.import_module(name)
        except ImportError:
            module = None
        return module

    @property
    def sys_version(self):
        return sys.version

    @property
    def python_environment(self):
        if in_ipykernel():
            return 'Jupyter'
        elif in_ipython():
            return 'IPython'
        return 'Python'

    @property
    def packages(self):
        """Return versions of all packages
        (available and unavailable/unknown)
        """
        packages = dict(self._packages)
        if self._sort:
            packages = sort_dictionary(packages)
        return packages


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
        Defaults to ['numpy', 'scipy', 'IPython', 'matplotlib', 'scooby']

    ncol : int, optional
        Number of package-columns in html table; only has effect if
        ``mode='HTML'`` or ``mode='html'``. Defaults to 3.

    text_width : int, optional
        The text width for non-HTML display modes

    sort : bool, optional
        Sort the packages when the report is shown

    """
    def __init__(self, additional=None, core=None, optional=None, ncol=3,
                 text_width=80, sort=False,):

        # Set default optional packages to investigate
        if optional is None:
            optional = ['numpy', 'scipy', 'IPython', 'matplotlib', 'scooby']

        PythonInfo.__init__(self, additional=additional, core=core,
                            optional=optional, sort=sort)
        self.ncol = int(ncol)
        self.text_width = int(text_width)

    def __repr__(self):
        """Plain-text version information."""

        # Width for text-version
        text = '\n' + self.text_width*'-' + '\n'

        # Date and time info as title
        date_text = '  Date: '
        mult = 0
        indent = len(date_text)
        for txt in textwrap.wrap(self.date, self.text_width-indent):
            date_text += ' '*mult + txt + '\n'
            mult = indent
        text += date_text+'\n'

        # ########## Platform/OS details ############
        text += '{:>18}'.format(self.system)+' : OS\n'
        text += '{:>18}'.format(self.cpu_count)+' : CPU(s)\n'
        text += '{:>18}'.format(self.machine)+' : Machine\n'
        text += '{:>18}'.format(self.architecture)+' : Architecture\n'
        if TOTAL_RAM:
            text += '{:>18}'.format(self.total_ram)+' : RAM\n'
        text += '{:>18}'.format(self.python_environment)+' : Environment\n'

        # ########## Python details ############
        text += '\n'
        for txt in textwrap.wrap(
                'Python '+self.sys_version, self.text_width-4):
            text += '  '+txt+'\n'
        text += '\n'

        # Loop over packages
        if self._sort:
            packages = sort_dictionary(self._packages)
        else:
            packages = self._packages
        for name, version in packages.items():
            text += '{:>18} : {}\n'.format(version, name)

        # ########## MKL details ############
        if MKL_INFO:
            text += '\n'
            for txt in textwrap.wrap(MKL_INFO, self.text_width-4):
                text += '  '+txt+'\n'

        # ########## Finish ############
        text += self.text_width*'-'

        return text

    def _repr_html_(self):
        """HTML-rendered version information."""

        # Define html-styles
        border = "border: 2px solid #fff;'"

        def colspan(html, txt, ncol, nrow):
            r"""Print txt in a row spanning whole table."""
            html += "  <tr>\n"
            html += "     <td style='text-align: center; "
            if nrow == 0:
                html += "font-weight: bold; font-size: 1.2em; "
            elif nrow % 2 == 0:
                html += "background-color: #ddd;"
            html += border + " colspan='"
            html += str(2*ncol)+"'>%s</td>\n" % txt
            html += "  </tr>\n"
            return html

        def cols(html, version, name, ncol, i):
            r"""Print package information in two cells."""

            # Check if we have to start a new row
            if i > 0 and i % ncol == 0:
                html += "  </tr>\n"
                html += "  <tr>\n"

            html += "    <td style='text-align: right; background-color: #ccc;"
            html += " " + border + ">%s</td>\n" % version

            html += "    <td style='text-align: left; "
            html += border + ">%s</td>\n" % name

            return html, i+1

        # Start html-table
        html = "<table style='border: 3px solid #ddd;'>\n"

        # Date and time info as title
        html = colspan(html, self.date,
                       self.ncol, 0)

        # ########## Platform/OS details ############
        html += "  <tr>\n"
        html, i = cols(html, self.system, 'OS', self.ncol, 0)
        html, i = cols(html, self.cpu_count, 'CPU(s)', self.ncol, i)
        html, i = cols(html, self.machine, 'Machine', self.ncol, i)
        html, i = cols(html, self.architecture, 'Architecture', self.ncol, i)
        if TOTAL_RAM:
            html, i = cols(html, self.total_ram, 'RAM', self.ncol, i)
        html, i = cols(
                html, self.python_environment, 'Environment', self.ncol, i)
        # Finish row
        html += "  </tr>\n"

        # ########## Python details ############
        html = colspan(html, 'Python '+self.sys_version, self.ncol, 1)

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

        # ########## MKL details ############
        if MKL_INFO:
            html = colspan(html, MKL_INFO, self.ncol, 2)

        # ########## Finish ############
        html += "</table>"

        return html
