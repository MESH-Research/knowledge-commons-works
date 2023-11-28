import click
import numpy as np
from APIResponse import APIResponse

# get stats for:
    # all deposits (total number, an average across all deposits, num views of every deposit)
    # a certain deposit
    # deposits over time

token = 'lVOh2bLTRWTOs8rwnF49KzJbhSnEmBsuNqXY7C0RMj9p2dzfiaHFPaYIoJgX'

@click.group()
def cli():
    pass

@cli.command(name='total_deposits')
@click.argument('over_time', default='all')
def request_total_deposits(over_time):
    client = APIResponse(token)
    no_deposits = client.total_deposits(over_time)
    if over_time.lower() == 'all':
        click.echo(f"Total number of deposits: {no_deposits}!")
    else:
        click.echo(f"Total number of deposits {over_time}:")
        for key in no_deposits:
            click.echo(f"{key}: {no_deposits[key]}")


@cli.command(name='num_views')
@click.argument('id', default='all')
def request_num_views(id):
    client = APIResponse(token)
    no_views = client.total_views(id)
    if id.lower() == 'all':
        for key in no_views:
            click.echo(f"Total number of views of deposit {key}: {no_views[key]}")
    else:
        click.echo(f"Total number of views of deposit {id}: {no_views}!")


@cli.command(name='num_downloads')
@click.argument('id', default='all')
def request_num_downloads(id):
    client = APIResponse(token)
    no_downloads = client.total_downloads(id)
    if id.lower() == 'all':
        for key in no_downloads:
            click.echo(f"Total number of views of deposit {key}: {no_downloads[key]}")
    else:
        click.echo(f"Total number of views of deposit {id}: {no_downloads}!")


@cli.command(name='avg_views')
# argument for over time options
def request_avg_views(id):
    client = APIResponse(token)
    avg = client.avg_views()
    click.echo(f"Average number of views per deposit: {avg}!")


@cli.command(name='avg_downloads')
# argument for over time options
def request_avg_downloads(id):
    client = APIResponse(token)
    avg = client.avg_downloads()
    click.echo(f"Average number of downloads per deposit: {avg}!")


@cli.command(name='top_downloads')
@click.argument('num', default=3)
def request_top_downloads(num):
    client = APIResponse(token)
    sorted_downloads = client.top_downloads()
    click.echo(f"Top {num} deposits by number of downloads:")
    index = -1
    for i in range(0, num):
        key = list(sorted_downloads)[index]
        click.echo(f"Deposit {key}: {sorted_downloads[key]} downloads")
        index += 1


"""
@click.option('--request', prompt='What statistic would you like to generate?', required=True,
              help='You can request the following statistics: total_deposits, num_views')
@click.option('--id', prompt='Enter the id of a certain deposit or enter "all":', default='all', 
              help='Provide the id of a certain deposit.')
def request_stat(request, id):

    client = APIResponse(token)

    # handle user requesting total no. of deposits
    if request.lower() == 'total_deposits':
        no_deposits = client.total_deposits()
        click.echo(f"Total number of deposits: {no_deposits}!")

    # handle user requesting number of views of a deposit
    elif request.lower() == 'num_views':
        # no_views is a dictionary if id='all', and a string containing one ID otherwise
        no_views = client.total_views(id)
        if id == 'all':
            for id in no_views:
                click.echo(f"Total number of views of deposit {id}: {no_views[id]}!")
        else:
            click.echo(f"Total number of views of deposit {id}: {no_views}!")

    # handle user providing invalid request
    else:
        click.echo("Invalid request.")
"""

if __name__ == '__main__':
    cli()