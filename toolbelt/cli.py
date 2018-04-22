import click

from toolbelt import generate_loopbacks
from toolbelt import load_host_data
from toolbelt import update_hosts
from toolbelt import generate_vagrant_file


@click.command()
@click.argument('DATAFILE')
def cli(data_file):
    """
    Create a Vagrantfile from a YAML data input file.

    DATAFILE: Location of DATAFILE
    """
    data = load_host_data(data_file)
    loopbacks = generate_loopbacks(data['hosts'])
    update_hosts(data['hosts'])
    return generate_vagrant_file(data, loopbacks)
