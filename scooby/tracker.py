"""Track imports."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scooby.knowledge import get_standard_lib_modules
from scooby.report import Report

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from types import ModuleType


TRACKING_SUPPORTED = False
SUPPORT_MESSAGE = (
    'Tracking is not supported for this version of Python. Try using a modern version of Python.'
)
try:
    import builtins

    CLASSIC_IMPORT = builtins.__import__
    TRACKING_SUPPORTED = True
except (ImportError, AttributeError):
    pass

# The variable we track all imports in
TRACKED_IMPORTS: list[str | ModuleType] = ['scooby']

MODULES_TO_IGNORE = {
    'pyMKL',
    'mkl',
    'vtkmodules',
    'mpl_toolkits',
}


STDLIB_PKGS: set[str] = set()


def _criterion(name: str) -> bool:
    return (
        len(name) > 0
        and name not in STDLIB_PKGS
        and not name.startswith('_')
        and name not in MODULES_TO_IGNORE
    )


if TRACKING_SUPPORTED:

    def scooby_import(
        name: str,
        globals: Mapping[str, object] | None = None,  # noqa: A002
        locals: Mapping[str, object] | None = None,  # noqa: A002
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> ModuleType:
        """Override of the import method to track package names."""
        m = CLASSIC_IMPORT(name, globals=globals, locals=locals, fromlist=fromlist, level=level)
        name = name.split('.')[0]
        if level == 0 and _criterion(name):
            TRACKED_IMPORTS.append(name)
        return m


def track_imports() -> None:
    """Track all imported modules for the remainder of this session."""
    if not TRACKING_SUPPORTED:
        raise RuntimeError(SUPPORT_MESSAGE)
    global STDLIB_PKGS
    STDLIB_PKGS = get_standard_lib_modules()
    builtins.__import__ = scooby_import


def untrack_imports() -> None:
    """Stop tracking imports and return to the builtin import method.

    This will also clear the tracked imports.
    """
    if not TRACKING_SUPPORTED:
        raise RuntimeError(SUPPORT_MESSAGE)
    builtins.__import__ = CLASSIC_IMPORT
    TRACKED_IMPORTS.clear()
    TRACKED_IMPORTS.append('scooby')


class TrackedReport(Report):
    """A class to inspect the active environment and generate a report.

    Generates a report based on all imported modules. Simply pass the
    ``globals()`` dictionary.
    """

    def __init__(
        self,
        additional: list[str | ModuleType] | None = None,
        ncol: int = 3,
        text_width: int = 80,
        sort: bool = False,
    ) -> None:
        """Initialize."""
        if not TRACKING_SUPPORTED:
            raise RuntimeError(SUPPORT_MESSAGE)
        if len(TRACKED_IMPORTS) < 2:
            msg = (
                'There are no tracked imports, please use '
                '`scooby.track_imports()` before running your '
                'code.'
            )
            raise RuntimeError(
                msg,
            )

        Report.__init__(
            self,
            additional=additional,
            core=TRACKED_IMPORTS,
            ncol=ncol,
            text_width=text_width,
            sort=sort,
            optional=[],
        )
