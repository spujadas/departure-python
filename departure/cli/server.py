import importlib
import pkgutil

import click

import departure.commons as commons
import departure.renderer

# initialise logging
commons.init_logging()


# code from https://packaging.python.org/guides/creating-and-discovering-plugins/
def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


# find available renderers (departure.renderer.*) and add their command to main CLI
for finder, name, ispkg in iter_namespace(departure.renderer):
    # get .cli submodule
    submodule = importlib.import_module('.cli', name)

    # get run() function - bound to @click.command
    command_function = getattr(submodule, 'run')

    # get command name for CLI
    command_name = getattr(submodule, 'COMMAND')

    # add command to CLI
    entry_point.add_command(command_function, name=command_name)


@click.group()
def entry_point():
    """
    Starts a departure board display server using the back end specified by COMMAND.

    Back ends are available as additional packages, see documentation for full list.
    """


if __name__ == "__main__":
    entry_point()
