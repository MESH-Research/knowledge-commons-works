import click
from APIResponse import APIResponse

# get stats for:
    # all deposits (total number, an average across all deposits, num views of every deposit)
    # a certain deposit
    # deposits over time

token = 'lVOh2bLTRWTOs8rwnF49KzJbhSnEmBsuNqXY7C0RMj9p2dzfiaHFPaYIoJgX'

# create click command for requesting statistic
# use commands and command groups instead
@click.group()
@click.option('--request', prompt='What statistic would you like to generate?', required=True,
              help='You can request the following statistics: total_deposits, num_views')
#@click.argument('request')
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

#@request_stat.command()
def main():
    request_stat()

if __name__ == '__main__':
    main()