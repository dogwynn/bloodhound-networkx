from pathlib import Path

import click

from ..common import setup_logging

@click.group()
@click.option('--loglevel', default='info', type=click.Choice([
    'debug', 'info', 'warning', 'error',
]))
def bnx_cli(loglevel: str):
    setup_logging(loglevel)

