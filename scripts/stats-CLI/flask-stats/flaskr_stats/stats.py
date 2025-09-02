import functools
import subprocess
from pprint import pprint

import stats_CLI
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

bp = Blueprint('stats', __name__, url_prefix='/')

@bp.route('/')
def stats():
    # send command line request to get total no. of deposits

    get_no_deposits = subprocess.Popen(["pipenv", "run", "python3", "stats_CLI.py", "total_deposits", "--json-output"], 
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True,)
    stdout_gnd, stderr_gnd = get_no_deposits.communicate()

    print(get_no_deposits.returncode)

    pprint(stdout_gnd)
    pprint(stderr_gnd)

    number = "34"

    return render_template('base.html', number=number)