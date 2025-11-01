"""The main module containing the `Report` class."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib
from importlib.metadata import (
    PackageNotFoundError,
    distribution,
    distributions,
    version as importlib_version,
)
import json
import re
import sys
from types import ModuleType
from typing import Any, Literal, cast

from .knowledge import (
    PACKAGE_ALIASES,
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

    def __init__(self) -> None:
        """Initialize."""
        self._mkl_info: str | None  # for typing purpose
        self._filesystem: str | Literal[False]

    @property
    def system(self) -> str:
        """Return the system/OS name.

        E.g. ``'Linux (name version)'``, ``'Windows'``, or ``'Darwin'``. An empty string is
        returned if the value cannot be determined.
        """
        s = platform().system()
        if s == 'Linux':
            try:
                s += (
                    f' ({platform().freedesktop_os_release()["NAME"]} '
                    f'{platform().freedesktop_os_release()["VERSION_ID"]})'
                )
            except Exception:  # noqa: BLE001
                pass
        elif s == 'Windows':
            try:
                release, version, csd, ptype = platform().win32_ver()
                s += f' ({release} {version} {csd} {ptype})'
            except Exception:  # noqa: BLE001
                pass
        elif s == 'Darwin':
            try:
                release, _, _ = platform().mac_ver()
                s += f' (macOS {release})'
            except Exception:  # noqa: BLE001
                pass
        elif s == 'Java':
            # TODO: parse platform().java_ver()
            pass
        return s

    @property
    def platform(self) -> str:
        """Return the platform."""
        return platform().platform()

    @property
    def machine(self) -> str:
        """Return the machine type, e.g. 'i386'.

        An empty string is returned if the value cannot be determined.
        """
        return platform().machine()

    @property
    def architecture(self) -> str:
        """Return the bit architecture used for the executable."""
        return platform().architecture()[0]

    @property
    def cpu_count(self) -> int:
        """Return the number of CPUs in the system."""
        if not hasattr(self, '_cpu_count'):
            import multiprocessing  # lazy-load see PR#85

            self._cpu_count = multiprocessing.cpu_count()
        return self._cpu_count

    @property
    def total_ram(self) -> str:
        """Return total RAM info.

        If not available, returns 'unknown'.
        """
        if not hasattr(self, '_total_ram'):
            try:
                import psutil  # lazy-load see PR#85

                tmem = psutil.virtual_memory().total
                self._total_ram = f'{tmem / (1024.0**3):.1f} GiB'
            except ImportError:
                self._total_ram = 'unknown'

        return self._total_ram

    @property
    def mkl_info(self) -> str | None:
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
                self._mkl_info = cast('str', mkl.get_version_string())
            elif numexpr:
                self._mkl_info = cast('str', numexpr.get_vml_version())
            else:
                self._mkl_info = None

        return self._mkl_info

    @property
    def date(self) -> str:
        """Return the date formatted as a string."""
        now_utc = datetime.now(timezone.utc)
        return now_utc.strftime('%a %b %d %H:%M:%S %Y %Z')

    @property
    def filesystem(self) -> str | Literal[False]:
        """Get the type of the file system at the path of the scooby package."""
        if not hasattr(self, '_filesystem'):
            self._filesystem = get_filesystem_type()
        return self._filesystem


class PythonInfo:
    """Internal helper class to access Python info and package versions."""

    def __init__(
        self,
        additional: list[str | ModuleType] | None,
        core: list[str | ModuleType] | None,
        optional: list[str | ModuleType] | None,
        sort: bool,
    ) -> None:
        """Initialize python info."""
        self._packages: dict[str, Any] = {}  # Holds name of packages and their version
        self._sort = sort

        # Add packages in the following order:
        self._add_packages(additional)  # Provided by the user
        self._add_packages(core)  # Provided by a module dev
        self._add_packages(optional, optional=True)  # Optional packages

    def _add_packages(
        self,
        packages: list[str | ModuleType] | None,
        optional: bool = False,
    ) -> None:
        """Add all packages to list; optional ones only if available."""
        # Ensure arguments are a list
        if isinstance(packages, (str, ModuleType)):
            pckgs: list[str | ModuleType] = [
                packages,
            ]
        elif packages is None or len(packages) < 1:
            pckgs = []
        else:
            pckgs = list(packages)

        # Loop over packages
        for pckg in pckgs:
            name, version = get_version(pckg)
            if not (version == MODULE_NOT_FOUND and optional):
                self._packages[name] = version

    @property
    def sys_version(self) -> str:
        """Return the system version."""
        return sys.version

    @property
    def python_environment(self) -> Literal['Jupyter', 'IPython', 'Python']:
        """Return the python environment."""
        if in_ipykernel():
            return 'Jupyter'
        if in_ipython():
            return 'IPython'
        return 'Python'

    @property
    def packages(self) -> dict[str, Any]:
        """Return versions of all additional, core, and optional packages.

        Includes available and unavailable/unknown.

        """
        pckg_dict = dict(self._packages)
        if self._sort:
            packages: dict[str, Any] = {}
            for name in sorted(pckg_dict.keys(), key=lambda x: x.lower()):
                packages[name] = pckg_dict[name]
            pckg_dict = packages
        return pckg_dict

    @property
    def installed_packages(self) -> dict[str, str]:
        """Return versions of all installed packages.

        .. versionadded:: 0.11
        """
        # sort case-insensitively by name
        installed = sorted(
            (dist.metadata['Name'] for dist in distributions()),
            key=str.lower,
        )
        packages: dict[str, str] = {}
        for pkg in installed:
            name, version = get_version(pkg)
            packages[name] = version
        return packages

    @property
    def other_packages(self) -> dict[str, str]:
        """Packages which are installed but not labeled as additional, core, or optional.

        This is effectively ``installed_packages`` - ``packages``.

        .. versionadded:: 0.11
        """
        packages = self.packages
        installed: dict[str, str] = self.installed_packages
        other: dict[str, str] = installed.copy()
        for key in installed:
            if key in packages:
                other.pop(key)
        return other


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

    extra_meta : tuple(tuple(str, str), ...), optional
        Additional two component pairs of meta information to display.

    max_width : int, optional
        Max-width of html-table. By default None.

    show_other : bool, default: False
        Show all other installed packages not already included in ``additional``,
        ``core``, or ``other``. These packages are always sorted alphabetically.

        .. versionadded:: 0.11

    """

    def __init__(
        self,
        additional: list[str | ModuleType] | None = None,
        core: list[str | ModuleType] | None = None,
        optional: list[str | ModuleType] | None = None,
        ncol: int = 4,
        text_width: int = 80,
        sort: bool = False,
        extra_meta: tuple[tuple[str, str], ...] | list[tuple[str, str]] | None = None,
        max_width: int | None = None,
        show_other: bool = False,
    ) -> None:
        """Initialize report."""
        # Set default optional packages to investigate
        if optional is None:
            optional = ['numpy', 'scipy', 'IPython', 'matplotlib', 'scooby']

        PythonInfo.__init__(self, additional=additional, core=core, optional=optional, sort=sort)
        self.ncol = int(ncol)
        self.text_width = int(text_width)
        self.max_width = max_width
        self.show_other = show_other

        if extra_meta is not None:
            if not isinstance(extra_meta, (list, tuple)):
                msg = '`extra_meta` must be a list/tuple of key-value pairs.'
                raise TypeError(msg)
            if len(extra_meta) == 2 and isinstance(extra_meta[0], str):
                extra_meta = [extra_meta]
            for meta in extra_meta:
                if not isinstance(meta, (list, tuple)) or len(meta) != 2:
                    msg = 'Each chunk of meta info must have two values.'
                    raise TypeError(msg)
        else:
            extra_meta = []
        self._extra_meta = extra_meta

    def __repr__(self) -> str:
        """Return Plain-text version information."""

        def line_sep(sep: str = '-', *, newlines: bool = False) -> str:
            line = self.text_width * sep
            return '\n' + line + '\n' if newlines else line

        import textwrap  # lazy-load see PR#85

        # Width for text-version
        text = line_sep(newlines=True)

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
        for key in [
            'OS',
            'CPU(s)',
            'Machine',
            'Architecture',
            'RAM',
            'Environment',
            'File system',
        ]:
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
        package_template = '{name:>{row_width}} : {version}\n'
        for name, version in self.packages.items():
            text += package_template.format(name=name, version=version, row_width=row_width)

        # MKL details
        if self.mkl_info:
            text += '\n'
            for txt in textwrap.wrap(self.mkl_info, self.text_width - 4):
                text += '  ' + txt + '\n'

        if self.show_other:
            text = text.rstrip()
            text += line_sep('·', newlines=True)

            for name, version in self.other_packages.items():
                text += package_template.format(name=name, version=version, row_width=row_width)

        # Finish
        text += line_sep()

        return text

    def _repr_html_(self) -> str:
        """Return HTML-rendered version information."""
        # Define html-styles
        border = "border: 1px solid;'"

        def colspan(html: str, txt: str, ncol: int, nrow: int) -> str:
            r"""Print txt in a row spanning whole table."""
            html += '  <tr>\n'
            html += "     <td style='"
            if ncol == 1:
                html += 'text-align: left; '
            else:
                html += 'text-align: center; '
            if nrow == 0:
                html += 'font-weight: bold; font-size: 1.2em; '
            html += border + " colspan='"
            html += f"{2 * ncol}'>{txt}</td>\n"
            html += '  </tr>\n'
            return html

        def cols(html: str, version: str, name: str, ncol: int, i: int) -> tuple[str, int]:
            r"""Print package information in two cells."""
            # Check if we have to start a new row
            if i > 0 and i % ncol == 0:
                html += '  </tr>\n'
                html += '  <tr>\n'

            align = 'left' if ncol == 1 else 'right'
            html += f"    <td style='text-align: {align};"
            html += ' ' + border + f'>{name}</td>\n'

            html += "    <td style='text-align: left; "
            html += border + f'>{version}</td>\n'

            return html, i + 1

        # Start html-table
        html = "<table style='border: 1.5px solid;"
        if self.max_width:
            html += f' max-width: {self.max_width}px;'
        html += "'>\n"

        # Date and time info as title
        html = colspan(html, self.date, self.ncol, 0)

        # Platform/OS details
        html += '  <tr>\n'
        repr_dict = self.to_dict()
        i = 0
        for key in [
            'OS',
            'CPU(s)',
            'Machine',
            'Architecture',
            'RAM',
            'Environment',
            'File system',
        ]:
            if key in repr_dict:
                html, i = cols(html, repr_dict[key], key, self.ncol, i)
        for meta in self._extra_meta:
            html, i = cols(html, meta[1], meta[0], self.ncol, i)
        # Finish row
        html += '  </tr>\n'

        # Python details
        html = colspan(html, 'Python ' + self.sys_version, self.ncol, 1)
        html += '  <tr>\n'

        # Loop over packages
        i = 0  # Reset count for rows.
        for name, version in self.packages.items():
            html, i = cols(html, version, name, self.ncol, i)
        # Fill up the row
        while i % self.ncol != 0:
            html += '    <td style= ' + border + '></td>\n'
            html += '    <td style= ' + border + '></td>\n'
            i += 1
        # Finish row
        html += '  </tr>\n'

        # MKL details
        if self.mkl_info:
            html = colspan(html, self.mkl_info, self.ncol, 2)

        # Finish
        html += '</table>'

        return html

    def to_dict(self) -> dict[str, str]:
        """Return report as dict for storage."""
        out: dict[str, str] = {}

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
        out.update(self._packages)

        out['other'] = json.dumps(self.other_packages)

        # MKL details
        if self.mkl_info:
            out['MKL'] = self.mkl_info

        return out


class AutoReport(Report):
    """Auto-generate a scooby.Report for a package.

    This will generate a report based on the distribution requirements of the package.
    """

    def __init__(
        self,
        module: str | ModuleType,
        additional: str | None = None,
        ncol: int = 3,
        text_width: int = 80,
        sort: bool = False,
        show_other: bool = False,
    ) -> None:
        """Initialize."""
        if not isinstance(module, (str, ModuleType)):
            msg = f'Cannot generate report for type ({type(module)})'
            raise TypeError(msg)

        if isinstance(module, ModuleType):
            module = module.__name__

        # Autogenerate from distribution requirements
        deps = get_distribution_dependencies(module, separate_extras=True)
        core = [module, *deps.pop('core')]
        optional = [  # flatten all extras from the nested "optional" dict
            pkg for dep_list in deps['optional'].values() for pkg in dep_list
        ]

        Report.__init__(
            self,
            additional=additional,
            core=core,
            optional=optional,
            ncol=ncol,
            text_width=text_width,
            sort=sort,
            show_other=show_other,
        )


# This functionaliy might also be of interest on its own.
def get_version(module: str | ModuleType) -> tuple[str, str | None]:
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
    # module is (1) a module or (2) a string.
    if not isinstance(module, (str, ModuleType)):
        msg = f'Cannot fetch version from type ({type(module)})'
        raise TypeError(msg)

    # module is module; get name
    if isinstance(module, ModuleType):
        name = module.__name__
    else:
        name = module
        module = None

    # Check aliased names
    if name in PACKAGE_ALIASES:
        name = PACKAGE_ALIASES[name]

    # try importlib.metadata before loading the module
    try:
        return name, importlib_version(name)
    except PackageNotFoundError:
        module = None

    # importlib could not find the package, try to load it
    if module is None:
        try:
            module = importlib.import_module(name)
        except ImportError:
            return name, MODULE_NOT_FOUND
        except Exception:  # noqa: BLE001
            return name, MODULE_TROUBLE

    # Try common version names on loaded module
    for v_string in ('__version__', 'version'):
        try:
            return name, getattr(module, v_string)
        except AttributeError:  # noqa: PERF203
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

    # If still not found, return VERSION_NOT_FOUND
    return name, VERSION_NOT_FOUND


def platform() -> ModuleType:
    """Return platform as lazy load; see PR#85."""
    import platform

    return platform


def get_distribution_dependencies(
    dist_name: str,
    *,
    separate_extras: bool = False,
) -> list[str] | dict[str, list[str]]:
    """Get required and extra dependencies of a package distribution.

    Parameters
    ----------
    dist_name : str
        Name of the package distribution.

    separate_extras : bool, default: False
        Separate extra (optional) dependencies by name. If ``True`` a ``dict``
        is returned with a ``'core'`` key with all required dependencies,
        and a ``'optional'`` key which includes any extras as separate keys.

        .. versionadded:: 0.11

    Returns
    -------
    dependencies : list | dict[str, list[str]]
        List of dependency names, or dict of dependencies separated by extras
        name if ``separate_extras`` is ``True``.

    """
    try:
        dist = distribution(dist_name)
    except PackageNotFoundError:
        msg = f'Package `{dist_name}` has no distribution.'
        raise PackageNotFoundError(msg) from None

    def _package_name(requirement: str) -> str:
        for sep in (' ', ';', '<', '=', '>', '!'):
            requirement = requirement.split(sep, 1)[0]
        return requirement.strip()

    requires = dist.requires or []
    if not separate_extras:
        # Use dict for ordered and unique keys
        return list({_package_name(pkg): None for pkg in requires}.keys())

    deps_dict: dict[str, dict[str, None | dict[str, None]]] = {'core': {}, 'optional': {}}

    for req in requires:
        name = _package_name(req)
        # Extract the extra name from a requirement string like "extra == 'dev'"
        extras_match = re.search(r"extra\s*==\s*['\"]?([\w-]+)['\"]?", req)
        if extras_match:
            extra_name = extras_match.group(1)
            if extra_name not in deps_dict['optional']:
                deps_dict['optional'][extra_name] = {}
            deps_dict['optional'][extra_name][name] = None
        else:
            deps_dict['core'][name] = None

    # Convert dicts of names → lists while preserving order
    return {
        'core': list(deps_dict['core'].keys()),
        'optional': {k: list(v.keys()) for k, v in deps_dict['optional'].items() if v},
    }
