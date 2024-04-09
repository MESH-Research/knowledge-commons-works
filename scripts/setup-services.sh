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

echo -e "${yellow}Setting up services for Knowledge Commons Works instance...${clear}"
read -p "${yellow}Do you want to use s3 for storage? (y/n)${clear}" s3 -n 1 -r
echo -e "${yellow}Creating the database...${clear}"
invenio db init create
if (( s3 == 'y' )); then
    echo -e "${yellow}Setting up s3 for storage...${clear}"
    invenio files location s3-default s3://hcommons-dev-invenio --default
else
    echo -e "${yellow}Setting up local storage...${clear}"
    invenio files location create --default default-location /opt/invenio/var/instance/data
fi
echo -e "${yellow}Setting up admin user and role...${clear}"
invenio roles create admin
invenio access allow superuser-access role admin
echo -e "${yellow}Setting up OpenSearch index...${clear}"
invenio index init
echo -e "${yellow}Setting up custom metadata fields...${clear}"
invenio rdm-records custom-fields init
invenio communities custom-fields init
echo -e "${yellow}Setting up fixtures (this may take a long time!!)...${clear}"
invenio rdm fixtures
invenio rdm-records fixtures
echo -e "${yellow}Compiling translations...${clear}"
pybabel compile -d /opt/invenio/src/translations
echo -e "${yellow}Setting up task queues...${clear}"
invenio queues declare
echo -e "${yellow}Creating administrator role...${clear}"
invenio roles create administrator
echo -e "${green}All done setting up services."
echo -e "${yellow}Building assets for Knowledge Commons Works instance...${clear}"
bash ./build-assets.sh
echo -e "${green}Your instance is now read to use.${clear}"