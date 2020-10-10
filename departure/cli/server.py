import importlib
import pkgutil

import click

from departure.commons.log import init_logging

# initialise logging
init_logging()


# CLI entry point
@click.group()
def entry_point():
    """
    Starts a departure board display server using the back end specified by COMMAND.
    Back ends are available as additional packages, see online documentation for full
    list.
    """


# find modules in namespace
def iter_namespace(ns_pkg):
    # code from https://packaging.python.org/guides/creating-and-discovering-plugins/
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


# import renderers if any
try:
    # ignore pylint errors if no renderers available => will be caught at runtime
    # pylint: disable=no-name-in-module,import-error
    import departure.renderer

    # find available renderers (departure.renderer.*) and add their command to main CLI
    # pylint: disable=no-member
    for finder, name, ispkg in iter_namespace(departure.renderer):
        # get .cli submodule
        submodule = importlib.import_module(".cli", name)

        # get run() function - bound to @click.command
        command_function = getattr(submodule, "run")

        # get command name for CLI
        command_name = getattr(submodule, "COMMAND")

        # add command to CLI
        entry_point.add_command(command_function, name=command_name)
except ModuleNotFoundError:
    # run anyway if no renderers found
    pass


if __name__ == "__main__":
    entry_point()
