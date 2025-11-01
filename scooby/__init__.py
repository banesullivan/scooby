"""Scooby.

Great Dane turned Python environment detective
==============================================

A lightweight toolset to easily report your Python environment's package
versions and hardware resources.

History
-------
The scooby reporting is derived from the versioning-scripts created by Dieter
Werthmüller for ``empymod``, ``emg3d``, and the ``SimPEG`` framework
(https://empymod.github.io; https://simpeg.xyz). It was heavily inspired by
``ipynbtools.py`` from ``qutip`` (https://github.com/qutip) and
``watermark.py`` from https://github.com/rasbt/watermark.
"""

from __future__ import annotations

from scooby.knowledge import (
    get_standard_lib_modules,
    in_ipykernel,
    in_ipython,
    meets_version,  # noqa: F401
    version_tuple,  # noqa: F401
)
from scooby.report import AutoReport, Report, get_version
from scooby.tracker import TrackedReport, track_imports, untrack_imports

doo = Report

__all__ = [
    'AutoReport',
    'Report',
    'TrackedReport',
    'doo',
    'get_standard_lib_modules',
    'get_version',
    'in_ipykernel',
    'in_ipython',
    'track_imports',
    'untrack_imports',
]


__author__ = 'Dieter Werthmüller, Bane Sullivan, Alex Kaszynski, and contributors'
__license__ = 'MIT'
__copyright__ = '2019, Dieter Werthmüller & Bane Sullivan'
try:
    from scooby.version import version as __version__
except ImportError:  # Only happens if not properly installed.
    from datetime import datetime, timezone

    __version__ = 'unknown-' + datetime.now(timezone.utc).strftime('%Y%m%d')
