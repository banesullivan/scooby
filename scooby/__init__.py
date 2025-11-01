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

from scooby.knowledge import get_standard_lib_modules
from scooby.knowledge import in_ipykernel
from scooby.knowledge import in_ipython
from scooby.knowledge import meets_version  # noqa: F401
from scooby.knowledge import version_tuple  # noqa: F401
from scooby.report import AutoReport
from scooby.report import Report
from scooby.report import get_version
from scooby.tracker import TrackedReport
from scooby.tracker import track_imports
from scooby.tracker import untrack_imports

doo = Report

__all__ = [
    'AutoReport',
    'Report',
    'TrackedReport',
    'doo',
    'get_standard_lib_modules',
    'in_ipython',
    'in_ipykernel',
    'get_version',
    'track_imports',
    'untrack_imports',
]


__author__ = 'Dieter Werthmüller, Bane Sullivan, Alex Kaszynski, and contributors'
__license__ = 'MIT'
__copyright__ = '2019, Dieter Werthmüller & Bane Sullivan'
try:
    from scooby.version import version as __version__
except ImportError:  # Only happens if not properly installed.
    from datetime import datetime
    from datetime import timezone

    __version__ = 'unknown-' + datetime.now(timezone.utc).strftime('%Y%m%d')
