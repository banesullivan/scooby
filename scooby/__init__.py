# coding=utf-8

# These are our default optional packages to investigate
SCOOBY_PACKAGES = ['numpy', 'scipy', 'IPython', 'matplotlib']

from scooby.extras import MKL_INFO, TOTAL_RAM, sort_dictionary
from scooby.knowledge import VERSION_ATTRIBUTES
from scooby.mysteries import in_ipython, in_ipykernel
from scooby.report import Report


def investigate(core=None,
                optional=SCOOBY_PACKAGES,
                additional=None,
                ncol=3, text_width=54, sort=False):
    """
    Have Scooby investigate the active Python environment. This returns a
    :class:`scooby.Report` object which displays the system information
    when a ``__repr__`` method is called (through outputting or printing).

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

    sort : bool, optional
        Sort the packages when the report is shown

    """
    versions = Report(core=core, optional=optional, additional=additional,
                        ncol=ncol, text_width=text_width, sort=sort)
    return versions


__author__ = 'Dieter Werthmüller & Bane Sullivan'
__license__ = 'MIT'
__copyright__ = '2019, Dieter Werthmüller & Bane Sullivan'
__version__ = '0.2.1'
