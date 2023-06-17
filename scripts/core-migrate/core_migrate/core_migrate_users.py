#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# adapted from scripts in invenio-utilities-tuw
# <https://gitlab.tuwien.ac.at/fairdata/invenio-utilities-tuw>
# copyright TU Wien <tudata@tuwien.ac.at>
#
# Run with `pipenv run invenio shell core_migrate_users.py`
# to ensure that the script has access to a current Flask app
# instance.

import click,csv

from invenio_utilities_tuw.utils import get_identity_for_user, get_record_service, get_user_by_identifier
from invenio_utilities_tuw.cli.utils import set_record_owners
from pprint import pprint

from core_migrate.config import GLOBAL_DEBUG

cli = click.Group()

@cli.command("get-user-id")
@click.argument('user_email', type=str)
def get_user_id(user_email):
    v = get_user_by_identifier(user_email)
    pprint(f'success: user id is {v.id}')
    return(v.id)


@cli.command("change-owner")
@click.argument("recid", required=True, type=str)
@click.argument("new_owner", required=True, type=str)
@click.argument("old_owner", required=True, type=str)
def change_owner(recid, new_owner, old_owner):
    debug = GLOBAL_DEBUG or True
    print('__________')
    print(f'Changing ownership of record {recid}')
    u = get_identity_for_user(old_owner)
    service = get_record_service()
    record = service.read(id_=recid, identity=u)._record
    all_owners = [get_user_by_identifier(new_owner)]
    set_record_owners(record, all_owners)
    if service.indexer:
        service.indexer.index(record)
    print('final record is:')
    pprint(service.read(id_=recid, identity=u)._record)
    return(service.read(id_=recid, identity=u)._record)


@cli.command()
@click.argument('owner_file', type=click.File('r'))
def change_owners(owner_file):
    reader = csv.reader(owner_file)
    for line in reader:
        print(line[0])
        change_owner(line[0],int(line[1]),2)
        exit()

if __name__=="__main__":
    exit(cli())