import builtins

from scooby.report import Report
from scooby.knowledge import get_standard_lib_modules


CLASSIC_IMPORT = builtins.__import__

# The variable we track all imports in
TRACKED_IMPORTS = []


STDLIB_PKGS = get_standard_lib_modules()

def scooby_import(name, globals=None, locals=None, fromlist=(), level=0):
    """A custom override of the import method to track package names"""
    m = CLASSIC_IMPORT(name, globals=globals, locals=locals, fromlist=fromlist, level=level)
    name = name.split(".")[0]
    if level == 0 and len(name) > 0 and name not in STDLIB_PKGS:
        TRACKED_IMPORTS.append(name)
    return m


def track_imports():
    """Track all imported modules for the remainder of this session."""
    builtins.__import__ = scooby_import
    return


def untrack_imports():
    """Stop tracking imports and return to the builtin import method. This will
    also clear the tracked imports"""
    builtins.__import__ = CLASSIC_IMPORT
    TRACKED_IMPORTS.clear()
    return



class TrackedReport(Report):
    """A class to inspect the active environment and generate a report based
    on all imported modules. Simply pass the ``globals()`` dictionary.
    """
    def __init__(self, additional=None, ncol=3, text_width=80, sort=False):
        if len(TRACKED_IMPORTS) < 1:
            raise RuntimeError("There are no tracked imports, please use "
                               "`scooby.track_imports()` before running your "
                               "code.")

        Report.__init__(self, additional=additional, core=TRACKED_IMPORTS,
                        ncol=ncol, text_width=text_width, sort=sort,
                        optional=[])
