#! /usr/bin/env python

import os
from pathlib import Path

GLOBAL_DEBUG = False
DATA_DIR = Path(Path(__file__).parents[4], 'kcr-untracked-files')
if os.environ['MIGRATION_SERVER_DATA_DIR']:
    DATA_DIR = os.environ['MIGRATION_SERVER_DATA_DIR']
FILES_LOCATION = DATA_DIR / 'humcore'
SERVER_DOMAIN = os.environ['MIGRATION_SERVER_DOMAIN']
