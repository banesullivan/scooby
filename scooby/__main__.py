"""Create entry point for the command-line interface (CLI)."""
import argparse
import importlib
import sys

import scooby
from scooby.report import Report


def main(args=None):
    """Parse command line inputs of CLI interface."""
    # If not explicitly called, catch arguments
    if args is None:
        args = sys.argv[1:]

    # Start CLI-arg-parser and define arguments
    parser = argparse.ArgumentParser(description="Great Dane turned Python environment detective.")

    # arg: Packages
    parser.add_argument(
        "packages", nargs="*", default=None, type=str, help=("names of the packages to report")
    )

    # arg: Report of a package
    parser.add_argument(
        "--report", default=None, type=str, help=("print `Report()` of this package")
    )

    # arg: Sort
    parser.add_argument(
        "--no-opt",
        action="store_true",
        default=False,
        help="do not show the default optional packages",
    )

    # arg: Sort
    parser.add_argument(
        "--sort",
        action="store_true",
        default=False,
        help="sort the packages when the report is shown",
    )

    # arg: Version
    parser.add_argument(
        "--version", action="store_true", default=False, help="only display scooby version"
    )

    # Call act with command line arguments as dict.
    act(vars(parser.parse_args(args)))


def act(args_dict):
    """Act upon CLI inputs."""
    # Quick exit if only scooby version.
    if args_dict.pop('version'):

        print(f"scooby v{scooby.__version__}")
        return

    # Report of another package.
    report = args_dict.pop('report')
    if report:
        try:
            module = importlib.import_module(report)
        except ImportError:
            print(f"Package `{report}` could not be imported.", file=sys.stderr)
            return

        try:
            print(module.Report())
        except AttributeError:
            print(f"Package `{report}` has no attribute `Report()`.", file=sys.stderr)

    # Scooby report with additional options.
    else:

        # Collect input.
        inp = {'additional': args_dict['packages'], 'sort': args_dict['sort']}

        # Define optional as empty list if no-opt.
        if args_dict['no_opt']:
            inp['optional'] = []

        # Print the report.
        print(Report(**inp))


if __name__ == "__main__":
    sys.exit(main())
