"""
Flyttdata
"""
import sys
import logging
import pkgutil
import importlib
from argparse import ArgumentParser

import flyttdata.cli as cli_package

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(module)s - %(levelname)s: %(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S')
    parser = ArgumentParser(description=__doc__, prog="flyttdata")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    subparsers = parser.add_subparsers()

    # Import each module that implements a subcommand and add a subparser for it.
    # Each subcommand is implemented as a module in the cli subpackage.
    # It needs to implement an add_arguments() and a main() function.
    modules = pkgutil.iter_modules(cli_package.__path__)
    for _, module_name, _ in modules:
        module = importlib.import_module("." + module_name, cli_package.__name__)
        help_message = module.__doc__
        subparser = subparsers.add_parser(
            module_name, help=help_message, description=module.__doc__
        )
        subparser.set_defaults(module=module)
        module.add_arguments(subparser)

    args = parser.parse_args()
    if not hasattr(args, "module"):
        parser.error("Please provide the name of a subcommand to run")
    else:
        module = args.module
        del args.module
        module.main(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
