import click
from invenio_subjects_fast.download_marcxml_files import download_marcxml_files
from invenio_subjects_fast.convert_to_yaml import convert_to_yaml

"""
A Script and command line interface for producing an InvenioRDM vocabulary file from the FAST subject vocabulary marcxml files.

Setup

This script

"""

@click.group()
def cli():
    pass


@cli.command("download")
def download_marcxml():
    """
    Download the FAST vocabulary marcxml files.
    """
    download_marcxml_files()


@cli.command("convert")
def convert_marcxml():
    """
    Convert the downloaded FAST marcxml files to a yaml vocabulary file
    """
    convert_to_yaml()



if __name__ == "__main__":
    cli()