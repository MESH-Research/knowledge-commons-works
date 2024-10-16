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
echo -e "${yellow}Collecting static files...${clear}"
invenio collect -v
echo -e "${yellow}Building assets...${clear}"
invenio webpack clean create
invenio webpack install
cd /opt/invenio/src
invenio shell ./scripts/symlink_assets.py
invenio webpack build
echo -e "${green}All done building assets...${clear}"