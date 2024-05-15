import click
import numpy as np
import json
from APIclient import APIclient
import os

token = os.environ['CLI_TOKEN']

@click.group()
def cli():
    pass

@cli.command(name='total_deposits')
@click.argument('freq', default=None, required=False)
@click.option('--json-output/--no-json', default=False, required=False)
def request_total_deposits(freq, json_output):
    client = APIclient(token)
    no_deposits = client.total_deposits(freq)
    if json_output:
        if freq == None:
            click.echo(json.dumps({"Total number of deposits": no_deposits}))
        else:
            json_str = json.dumps({"Total deposits " + freq: no_deposits})
            click.echo(json_str)
    else:
        if freq == None:
            click.echo(f"Total number of deposits: {no_deposits}!")
        else:
            click.echo(f"Total number of deposits {freq}:")
            for key in no_deposits:
                click.echo(f"{key}: {no_deposits[key]}")


@cli.command(name='num_views')
@click.argument('id', default='all')
@click.argument('version', default='current', required=False)   # options: current or all
@click.argument('start_date', default=None, required=False)      # if a freq option is specified, can only have start 
                                                                    # and end dates within the same calendar year
@click.argument('end_date', default=None, required=False)
@click.argument('freq', default=None, required=False)          # options: monthly, weekly, daily
@click.option('--unique/--not-unique', default=False, required=False)
@click.option('--json-output/--no-json', default=False, required=False)
def request_num_views(id, version, start_date, end_date, freq, unique, json_output):
    client = APIclient(token)
    no_views = client.total_views(id, version, start_date, end_date, freq, unique)
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
                                + id + (" (current version)" if version.lower() == "current" else " (all versions)"): no_views}))
            elif freq != None:
                click.echo(json.dumps({"Numbers of " + ("unique " if unique else "") + freq + " views of deposit " 
                                + id + (" (current version)" if version.lower() == "current" else " (all versions)")
                                + " from " + start_date + " to " + end_date: no_views}))
            else:
                click.echo(json.dumps({"Total number of " + ("unique " if unique else "") + "views of deposit " 
                                + id + (" (current version)" if version.lower() == "current" else " (all versions)") 
                                + " from " + start_date + " to " + end_date: no_views}))
        else:
            if start_date is None and end_date is None:
                click.echo("Total number of " + ("unique " if unique else "") + f"views of deposit {id} " + 
                       ("(current version): " if version.lower() == "current" else "(all versions): ") + f"{no_views}!")
            elif freq != None:
                click.echo("Numbers of " + ("unique " if unique else "") + freq + f" views of deposit {id} " + 
                       ("(current version)" if version.lower() == "current" else "(all versions)") + " from " 
                       + start_date + " to " + end_date + ":")
                for key in no_views:
                    click.echo(str(key) + ": " + str(no_views[key]))
            else:
                click.echo("Total number of " + ("unique " if unique else "") + f"views of deposit {id} " + 
                       ("(current version)" if version.lower() == "current" else "(all versions)") + " from " 
                       + start_date + " to " + end_date + f": {no_views}!")


@cli.command(name='avg_views')
@click.argument('version', default='current')
@click.argument('start_date', default=None, required=False)
@click.argument('end_date', default=None, required=False)
@click.argument('freq', default=None, required=False)
@click.option('--unique/--not-unique', default=False)
@click.option('--json-output/--no-json', default=False, required=False)
def request_avg_views(version, start_date, end_date, freq, unique, json_output):
    client = APIclient(token)
    avg = client.avg_views(version, start_date, end_date, freq, unique)
    if freq is None:
        if json_output:
            click.echo(json.dumps({"Average number of " + ("unique " if unique else "") + "views per deposit, taken from " 
                                + ("current version" if version == "current" else "all versions")
                                + (" over " + start_date + " to " + end_date if start_date != None and end_date != None else ""): avg}))
        else:
            click.echo("Average number of " + ("unique " if unique else "") + "views per deposit, taken from "
                    + ("current versions" if version == "current" else "all versions") 
                    + (" over " + start_date + " to " + end_date if start_date != None and end_date != None else "") + f": {avg}")
    
    elif freq != None and start_date != None and end_date != None:
        if json_output:
            click.echo(json.dumps({"Average " + freq + ("unique " if unique else "") + "views per deposit, taken from " 
                                + ("current versions" if version.lower() == "current" else "all versions")
                                + " over " + start_date + " to " + end_date: avg}))
        else:
            click.echo("Average " + freq + " numbers of " + ("unique " if unique else "") + "views per deposit, taken from " 
                        + ("current versions" if version.lower() == "current" else "all versions") + " over " 
                        + start_date + " to " + end_date + ":")
            for key in avg:
                click.echo(str(key) + ": " + str(avg[key]))


@cli.command(name='num_downloads')
@click.argument('id', default='all')
@click.argument('version', default='current', required=False)
@click.argument('start_date', default=None, required=False)
@click.argument('end_date', default=None, required=False)
@click.argument('freq', default=None, required=False)          # options: monthly, weekly, daily
@click.option('--unique/--not-unique', default=False, required=False)
@click.option('--json-output/--no-json', default=False, required=False)
def request_num_downloads(id, version, start_date, end_date, freq, unique, json_output):
    client = APIclient(token)
    no_downloads = client.total_downloads(id, version, start_date, end_date, freq, unique)
    if id.lower() == 'all':
        if json_output:
            click.echo(json.dumps({"Total number of " + ("unique" if unique else "") + " downloads by deposit " 
                                + ("(current versions)" if version.lower() == "current" else "(all versions)"): no_downloads}))
        else:
            click.echo("Total number of " + ("unique " if unique else "") + "downloads of " 
                       + ("current version" if version.lower() == "current" else "all versions") + " of each deposit:")
            for key in no_downloads:
                click.echo(f"Deposit {key}: {no_downloads[key]}")
    else:
        if json_output:
            if start_date is None and end_date is None:
                click.echo(json.dumps({"Total number of " + ("unique " if unique else "") + "downloads of deposit " 
                                + id + (" (current version)" if version.lower() == "current" else " (all versions)"): no_downloads}))
            elif freq != None:
                click.echo(json.dumps({"Numbers of " + ("unique " if unique else "") + freq + " downloads of deposit " 
                                + id + (" (current version)" if version.lower() == "current" else " (all versions)")
                                + " from " + start_date + " to " + end_date: no_downloads}))
            else:
                click.echo(json.dumps({"Total number of " + ("unique " if unique else "") + "downloads of deposit " 
                                + id + (" (current version)" if version.lower() == "current" else " (all versions)") 
                                + " from " + start_date + " to " + end_date: no_downloads}))
        else:
            if start_date is None and end_date is None:
                click.echo("Total number of " + ("unique " if unique else "") + f"downloads of deposit {id} " + 
                       ("(current version): " if version.lower() == "current" else "(all versions): ") + f"{no_downloads}!")
            elif freq != None:
                click.echo("Numbers of " + ("unique " if unique else "") + freq + f" downloads of deposit {id} " + 
                       ("(current version)" if version.lower() == "current" else "(all versions)") + " from " 
                       + start_date + " to " + end_date + ":")
                for key in no_downloads:
                    click.echo(str(key) + ": " + str(no_downloads[key]))
            else:
                click.echo("Total number of " + ("unique " if unique else "") + f"downloads of deposit {id} " + 
                       ("(current version)" if version.lower() == "current" else "(all versions)") + " from " 
                       + start_date + " to " + end_date + f": {no_downloads}!")


@cli.command(name='avg_downloads')
@click.argument('version', default='current')
@click.argument('start_date', default=None, required=False)
@click.argument('end_date', default=None, required=False)
@click.argument('freq', default=None, required=False)
@click.option('--unique/--not-unique', default=False)
@click.option('--json-output/--no-json', default=False, required=False)
def request_avg_downloads(version, start_date, end_date, freq, unique, json_output):
    client = APIclient(token)
    avg = client.avg_downloads(version, start_date, end_date, freq, unique)
    if freq is None:
        if json_output:
            click.echo(json.dumps({"Average number of " + ("unique " if unique else "") + "downloads per deposit, taken from " 
                                + ("current version" if version == "current" else "all versions")
                                + (" over " + start_date + " to " + end_date if start_date != None and end_date != None else ""): avg}))
        else:
            click.echo("Average number of " + ("unique " if unique else "") + "downloads per deposit, taken from "
                    + ("current versions" if version == "current" else "all versions") 
                    + (" over " + start_date + " to " + end_date if start_date != None and end_date != None else "") + f": {avg}")
    
    elif freq != None and start_date != None and end_date != None:
        if json_output:
            click.echo(json.dumps({"Average " + freq + ("unique " if unique else "") + "downloads per deposit, taken from " 
                                + ("current versions" if version.lower() == "current" else "all versions")
                                + " over " + start_date + " to " + end_date: avg}))
        else:
            click.echo("Average " + freq + " numbers of " + ("unique " if unique else "") + "downloads per deposit, taken from " 
                        + ("current versions" if version.lower() == "current" else "all versions") + " over " 
                        + start_date + " to " + end_date + ":")
            for key in avg:
                click.echo(str(key) + ": " + str(avg[key]))


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