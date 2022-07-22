"""Create entry point for the command-line interface (CLI)."""
import argparse
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

    # Get command line arguments.
    args_dict = vars(parser.parse_args(args))

    # Only scooby version.
    if args_dict.pop('version'):

        print(f"scooby v{scooby.__version__}")
        return

    # Collect input.
    inp = {'additional': args_dict['packages'], 'sort': args_dict['sort']}

    # Define optional as empty list if no-opt.
    if args_dict['no_opt']:
        inp['optional'] = []

    # Print the report.
    print(Report(**inp))


if __name__ == "__main__":
    sys.exit(main())
