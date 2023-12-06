import click
import numpy as np
import json
from APIclient import APIclient

token = 'lVOh2bLTRWTOs8rwnF49KzJbhSnEmBsuNqXY7C0RMj9p2dzfiaHFPaYIoJgX'

@click.group()
def cli():
    pass

@cli.command(name='total_deposits')
@click.argument('over_time', default='all')
@click.option('--json-output/--no-json', default=False, required=False)
def request_total_deposits(over_time, json_output):
    client = APIclient(token)
    no_deposits = client.total_deposits(over_time)
    if json_output:
        if over_time.lower() == 'all':
            click.echo(json.dumps({"Total number of deposits": no_deposits}))
        else:
            json_str = json.dumps({"Total deposits " + over_time: no_deposits})
            click.echo(json_str)
    else:
        if over_time.lower() == 'all':
            click.echo(f"Total number of deposits: {no_deposits}!")
        else:
            click.echo(f"Total number of deposits {over_time}:")
            for key in no_deposits:
                click.echo(f"{key}: {no_deposits[key]}")


@cli.command(name='num_views')
@click.argument('id', default='all')
@click.argument('version', default='current', required=False)
@click.argument('start_date', default=None, required=False)
@click.argument('end_date', default=None, required=False)
@click.option('--unique/--not-unique', default=False, required=False)
@click.option('--json-output/--no-json', default=False, required=False)
def request_num_views(id, version, start_date, end_date, unique, json_output):
    client = APIclient(token)
    no_views = client.total_views(id, version, start_date, end_date, unique)
    if id.lower() == 'all':
        if json_output:
            click.echo(json.dumps({"Total number of " + ("unique" if unique else "") + " views by deposit " 
                                + ("(current versions)" if version.lower() == "current" else "(all versions)"): no_views}))
        else:
            click.echo("Total number of " + ("unique " if unique else "") + "views of " 
                       + ("current version" if version.lower() == "current" else "all versions") + " of each deposit:")
            for key in no_views:
                click.echo(f"Deposit {key}: {no_views[key]}")
    else:
        if json_output:
            if start_date is None and end_date is None:
                click.echo(json.dumps({"Total number of " + ("unique " if unique else "") + "views of deposit " 
                                + id + ("(current version)" if version.lower() == "current" else "(all versions)"): no_views}))
            else:
                click.echo(json.dumps({"Total number of " + ("unique " if unique else "") + "views of deposit " 
                                + id + ("(current version)" if version.lower() == "current" else "(all versions)") 
                                + " from " + start_date + " to " + end_date: no_views}))
        else:
            if start_date is None and end_date is None:
                click.echo("Total number of " + ("unique " if unique else "") + f"views of deposit {id} " + 
                       ("(current version): " if version.lower() == "current" else "(all versions): ") + f"{no_views}!")
            else:
                click.echo("Total number of " + ("unique " if unique else "") + f"views of deposit {id} " + 
                       ("(current version)" if version.lower() == "current" else "(all versions)") + " from " 
                       + start_date + " to " + end_date + f": {no_views}!")


"""
@cli.command(name='num_views_date_range')
@click.argument('id', default='all')
@click.argument('start_date', default=None)
@click.argument('end_date', default=None)
@click.option('--unique/--not-unique', default=False)
@click.option('--json-output/--no-json', default=False)
def request_num_views_date_range(id, start_date, end_date, unique, json_output):
    client = APIclient(token)
    no_views = client.total_views_date_range(id, version, unique)
"""

@cli.command(name='num_downloads')
@click.argument('id', default='all')
@click.argument('version', default='current')
@click.option('--unique/--not-unique', default=False)
@click.option('--json-output/--no-json', default=False)
def request_num_downloads(id):
    client = APIclient(token)
    no_downloads = client.total_downloads(id)
    if id.lower() == 'all':
        for key in no_downloads:
            click.echo(f"Total number of views of deposit {key}: {no_downloads[key]}")
    else:
        click.echo(f"Total number of views of deposit {id}: {no_downloads}!")


@cli.command(name='avg_views')
# argument for over time options
@click.argument('version', default='current')
@click.option('--unique/--not-unique', default=False)
def request_avg_views(version, unique):
    client = APIclient(token)
    avg = client.avg_views(version, unique)
    click.echo(f"Average number of views per deposit: {avg}!")


@cli.command(name='avg_downloads')
# argument for over time options
def request_avg_downloads(id):
    client = APIclient(token)
    avg = client.avg_downloads()
    click.echo(f"Average number of downloads per deposit: {avg}!")


@cli.command(name='top_downloads')
@click.argument('num', default=3)
def request_top_downloads(num):
    client = APIclient(token)
    sorted_downloads = client.top_downloads()
    click.echo(f"Top {num} deposits by number of downloads:")
    index = -1
    for i in range(0, num):
        key = list(sorted_downloads)[index]
        click.echo(f"Deposit {key}: {sorted_downloads[key]} downloads")
        index += 1


if __name__ == '__main__':
    cli()