# SPDX-FileCopyrightText: 2024-present Anthony Wu <https://github.com/anthonywu>
#
# SPDX-License-Identifier: MIT
import click

from mflux_fasthtml.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="mflux-fasthtml")
def mflux_fasthtml():
    click.echo("Hello world!")
