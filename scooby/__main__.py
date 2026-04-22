"""Create entry point for the command-line interface (CLI)."""

from __future__ import annotations

import argparse
import fnmatch
import importlib
from importlib.metadata import PackageNotFoundError
import runpy
import sys
from typing import Any

import scooby
from scooby.report import AutoReport, Report


def main(args: list[str] | None = None) -> None:
    """Parse command line inputs of CLI interface."""
    # If not explicitly called, catch arguments
    if args is None:
        args = sys.argv[1:]

    # Start CLI-arg-parser and define arguments
    parser = argparse.ArgumentParser(description='Great Dane turned Python environment detective.')

    # arg: Packages
    parser.add_argument(
        'packages',
        nargs='*',
        default=None,
        type=str,
        help=('names of the packages to report'),
    )

    # arg: Report of a package
    parser.add_argument(
        '--report',
        '-r',
        default=None,
        type=str,
        help=('print `Report()` of this package'),
    )

    # arg: Sort
    parser.add_argument(
        '--no-opt',
        action='store_true',
        default=None,
        help='do not show the default optional packages. Defaults to True if '
        'using --report and defaults to False otherwise.',
    )

    # arg: Sort
    parser.add_argument(
        '--sort',
        action='store_true',
        default=False,
        help='sort the packages when the report is shown',
    )

    # arg: Version
    parser.add_argument(
        '--version',
        '-v',
        action='store_true',
        default=False,
        help='only display scooby version',
    )

    # arg: Grep installed packages (issue #100)
    parser.add_argument(
        '--grep',
        '-g',
        default=None,
        metavar='PATTERN',
        action='append',
        help='list installed packages whose names match PATTERN '
        '(case-insensitive substring match, or fnmatch glob if PATTERN '
        "contains '*', '?', or '['). Repeatable.",
    )

    # arg: Track imports of a script (issue #100)
    parser.add_argument(
        '--track',
        default=None,
        metavar='SCRIPT',
        help='run a Python SCRIPT with import tracking enabled, then print a '
        'TrackedReport. Any additional positional arguments are forwarded to '
        "the script as sys.argv[1:] (flags prefixed with '-' are consumed by "
        'scooby itself; separate them with `--` if they should reach the '
        'script).',
    )

    # Call act with command line arguments as dict.
    act(vars(parser.parse_args(args)))


def act(args_dict: dict[str, Any]) -> None:
    """Act upon CLI inputs."""
    # Quick exit if only scooby version.
    if args_dict.pop('version'):
        print(f'scooby v{scooby.__version__}')
        return

    report = args_dict.pop('report')
    no_opt = args_dict.pop('no_opt')
    packages = args_dict.pop('packages')
    grep_patterns = args_dict.pop('grep')
    track_script = args_dict.pop('track')

    if no_opt is None:
        if report is None:
            no_opt = False
        else:
            no_opt = True

    # Grep installed packages.
    if grep_patterns:
        _grep(grep_patterns)
        return

    # Run a script with import tracking.
    if track_script:
        _track(track_script, packages or [], sort=args_dict['sort'])
        return

    # Report of another package.
    if report:
        try:
            module = importlib.import_module(report)
        except ImportError:
            pass
        else:
            try:
                report_cls = module.Report
            except AttributeError:
                pass
            else:
                if issubclass(report_cls, Report):
                    print(report_cls())
                    return

        try:
            print(AutoReport(report))
        except PackageNotFoundError:
            print(
                f'Package `{report}` has no Report class and `importlib` could not '
                'be used to autogenerate one.',
                file=sys.stderr,
            )
            sys.exit(1)
        else:
            return

    # Collect input.
    inp = {'additional': packages, 'sort': args_dict['sort']}

    # Define optional as empty list if no-opt.
    if no_opt:
        inp['optional'] = []

    # Print the report.
    print(Report(**inp))


def _grep(patterns: list[str]) -> None:
    """Print installed packages whose names match any of ``patterns``."""
    # Use Report's installed_packages — same source of truth as `other`.
    installed = Report(optional=[]).installed_packages
    lowered = {name.lower(): (name, version) for name, version in installed.items()}

    matches: dict[str, str] = {}
    for raw in patterns:
        pattern = raw.lower()
        is_glob = any(ch in pattern for ch in '*?[')
        for lname, (name, version) in lowered.items():
            hit = fnmatch.fnmatchcase(lname, pattern) if is_glob else pattern in lname
            if hit:
                matches[name] = version

    if not matches:
        # Non-zero exit mirrors `grep`'s convention for "no match".
        sys.exit(1)

    for name in sorted(matches, key=str.lower):
        print(f'{name}=={matches[name]}')


def _track(script: str, script_args: list[str], sort: bool) -> None:
    """Run ``script`` with import tracking, then print a TrackedReport."""
    scooby.track_imports()
    # Preserve and restore sys.argv so the tracked script sees its own argv.
    original_argv = sys.argv
    sys.argv = [script, *script_args]
    try:
        runpy.run_path(script, run_name='__main__')
        report = scooby.TrackedReport(sort=sort)
    finally:
        sys.argv = original_argv
        scooby.untrack_imports()
    print(report)


if __name__ == '__main__':
    main()
