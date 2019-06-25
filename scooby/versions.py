import importlib
import logging
import multiprocessing
import platform
import sys
import textwrap
import time
from types import ModuleType

from scooby.knowledge import VERSION_ATTRIBUTES

try:
    import mkl
except ImportError:
    mkl = False

# Get mkl info, if available
if mkl:
    mklinfo = mkl.get_version_string()
else:
    mklinfo = False


class Versions:
    r"""Print date, time, and version information.

    Print date, time, and package version information in any environment
    (Jupyter notebook, IPython console, Python console, QT console), either as
    html-table (notebook) or as plain text (anywhere).

    Always shown are the OS, number of CPU(s), ``numpy``, ``scipy``,
    ``sys.version``, and time/date.

    Additionally shown are, if they can be imported, ``IPython`` and
    ``matplotlib``. It also shows MKL information, if available.

    All modules provided in ``add_pckg`` are also shown. They have to be
    imported before ``versions`` is called.

    This script was heavily inspired by:

        - ipynbtools.py from qutip https://github.com/qutip
        - watermark.py from https://github.com/rasbt/watermark


    Parameters
    ----------
    core : list(ModuleType), list(str)
        The core packages to list first.

    optional : list(ModuleType), list(str)
        A list of packages to list if they are available. If not available,
        no warnings or error will be thrown.

    additional : list(ModuleType), list(str)
        List of packages or package names to add to output information.

    ncol : int, optional
        Number of package-columns in html table; only has effect if
        ``mode='HTML'`` or ``mode='html'``. Defaults to 3.

    text_width : int, optional
        The text width for non-HTML display modes

    """

    def __init__(self, core=('numpy', 'scipy',),
                       optional=('IPython', 'matplotlib',),
                       additional=None,
                       ncol=4, text_width=54):
        """Initiate and add packages and number of columns to self."""
        self.ncol = int(ncol)
        self.text_width = text_width

        # Mandatory packages
        self._packages = {}

        # MAke sure arguments are good
        def safety(x):
            if x is None or len(x) < 1:
                return []
            elif isinstance(x, str):
                return [x,]
            else:
                return list(x)
        core = safety(core)
        optional = safety(optional)
        additional = safety(additional)

        # Update packages
        self.add_packages(core)
        # Optional packages
        self.add_packages(optional, optional=True)
        # Additional packages
        self.add_packages(additional)


    @staticmethod
    def _safe_import_by_name(name, optional=False):
        try:
            module = importlib.import_module(name)
        except ImportError:
            if not optional:
                logging.warning('Could not import module `{}`. This will be ignored.'.format(name))
            module = None
        return module


    def _add_package(self, module, name=None, optional=False):
        """Internal helper to update the packages dictionary with a module
        """
        if name is None or not isinstance(name, str):
            name = module.__name__
        if not isinstance(module, ModuleType):
            if optional:
                return
            raise TypeError('Module passed is not a module.')
        self._packages[name] = module
        return


    def _add_package_by_name(self, name, optional=False):
        """Internal helper to add a module to the internal list of packages.
        Returns True if succesful, false if unsuccesful."""
        module = Versions._safe_import_by_name(name, optional=optional)
        if module is not None:
            self._add_package(module, name, optional=optional)
            return True
        return False


    def add_packages(self, packages, optional=False):
        if not isinstance(packages, (list, tuple)):
            raise TypeError('You must pass a list of packages or package names.')
        for pckg in packages:
            if isinstance(pckg, str):
                self._add_package_by_name(pckg, optional=optional)
            elif isinstance(pckg, ModuleType):
                self._add_package(pckg, optional=optional)
            elif pckg is None:
                pass
            elif not optional:
                raise TypeError('Cannot add package from type ({})'.format(type(pckg)))

    @property
    def platform(self):
        """Returns the system/OS name, e.g. ``'Linux'``, ``'Windows'``, or
        ``'Java'``. An empty string is returned if the value cannot be
        determined."""
        return platform.system()


    @property
    def cpu_count(self):
        """Return the number of CPUs in the system. May raise
        ``NotImplementedError``."""
        return multiprocessing.cpu_count()


    @property
    def sys_version(self):
        text = '\n'
        for txt in textwrap.wrap(sys.version, self.text_width-4):
            text += '  '+txt+'\n'
        return text


    def get_version(self, pckg):
        """Get the version of a package by passing the package or it's name"""
        # First, fetch the module and its name
        if isinstance(pckg, str):
            name = pckg
            try:
                module = self._packages[name]
            except KeyError:
                # This could raise an error if module not found
                module = Versions._safe_import_by_name(pckg)
        elif isinstance(pckg, ModuleType):
            name = pckg.__name__
            module = pckg
        else:
            raise TypeError('Cannot fetch version from type ({})'.format(type(pckg)))
        # Now get the version info from the module
        try:
            attr = VERSION_ATTRIBUTES[name]
            version = getattr(module, attr)
        except (KeyError, AttributeError):
            try:
                version = module.__version__
            except AttributeError:
                logging.warning('Varsion attribute for `{}` is unknown.'.format(name))
                version = 'unknown'
        return version


    def __repr__(self):
        r"""Plain-text version information."""

        # Width for text-version
        text = '\n' + self.text_width*'-' + '\n'

        # Date and time info as title
        text += time.strftime('  %a %b %d %H:%M:%S %Y %Z\n\n')

        # OS and CPUs
        text += '{:>15}'.format(self.platform)+' : OS\n'
        text += '{:>15}'.format(self.cpu_count)+' : CPU(s)\n'

        # Loop over packages
        for name in self._packages.keys():
            text += '{:>15} : {}\n'.format(self.get_version(name), name)

        # sys.version
        text += self.sys_version

        # mkl version
        if mklinfo:
            text += '\n'
            for txt in textwrap.wrap(mklinfo, self.text_width-4):
                text += '  '+txt+'\n'

        # Finish
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
        html = colspan(html, time.strftime('%a %b %d %H:%M:%S %Y %Z'),
                       self.ncol, 0)

        # OS and CPUs
        html += "  <tr>\n"
        html, i = cols(html, self.platform, 'OS', self.ncol, 0)
        html, i = cols(html, self.cpu_count, 'CPU(s)',
                       self.ncol, i)

        # Loop over packages
        for name in self._packages.keys():
            html, i = cols(html, self.get_version(name), name, self.ncol, i)
        # Fill up the row
        while i % self.ncol != 0:
            html += "    <td style= " + border + "></td>\n"
            html += "    <td style= " + border + "></td>\n"
            i += 1
        # Finish row
        html += "  </tr>\n"

        # sys.version
        html = colspan(html, sys.version, self.ncol, 1)

        # mkl version
        if mklinfo:
            html = colspan(html, mklinfo, self.ncol, 2)

        # Finish table
        html += "</table>"

        return html
