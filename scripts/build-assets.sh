#! /bin/bash

# Color variables
red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
blue='\033[0;34m'
magenta='\033[0;35m'
cyan='\033[0;36m'
# Clear the color after that
clear='\033[0m'

echo -e "${yellow}Building assets for Knowledge Commons Works instance...${clear}"

# Fix axios version conflict in invenio_search_ui
echo -e "${yellow}Fixing axios version conflict in invenio_search_ui...${clear}"
if [ -f "/opt/invenio/src/.venv/lib/python3.12/site-packages/invenio_search_ui/webpack.py" ]; then
    sed -i '/"axios": "^0.21.0"/d' /opt/invenio/src/.venv/lib/python3.12/site-packages/invenio_search_ui/webpack.py
    echo -e "${green}Fixed axios version conflict in invenio_search_ui${clear}"
elif [ -f "/opt/invenio/src/.venv/lib/python3.9/site-packages/invenio_search_ui/webpack.py" ]; then
    sed -i '/"axios": "^0.21.0"/d' /opt/invenio/src/.venv/lib/python3.9/site-packages/invenio_search_ui/webpack.py
    echo -e "${green}Fixed axios version conflict in invenio_search_ui${clear}"
else
    echo -e "${red}Warning: Could not find invenio_search_ui/webpack.py to fix axios conflict${clear}"
fi

echo -e "${yellow}Collecting static files...${clear}"
invenio collect -v
echo -e "${yellow}Building assets...${clear}"
invenio webpack clean create
invenio webpack install
cd /opt/invenio/src
invenio shell ./scripts/symlink_assets.py
invenio webpack build
echo -e "${green}All done building assets...${clear}"