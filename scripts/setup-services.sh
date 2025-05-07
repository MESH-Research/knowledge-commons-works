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

local fixtures=0
local destroy=0

while getopts 'fd' flag
do
    case "${flag}" in
        f) fixtures=1 ;;
        d) destroy=1 ;;
        *) echo 'Error in command line parsing' >&2
           exit 1
    esac
done

if [ $destroy==1 ]
then
    echo -e "${yellow}Destroying the database...${clear}"
    invenio db destroy --yes-i-know
    echo -e "${yellow}Destroying the OpenSearch index...${clear}"
    invenio index destroy --force --yes-i-know
    echo -e "${yellow}Clearing the search indexing task queues...${clear}"
    invenio index queue init purge
fi

echo -e "${yellow}Setting up services for Knowledge Commons Works instance...${clear}"
echo -e "${yellow}Creating the database...${clear}"
invenio db init create
echo -e "${yellow}Do you want to use s3 or local file storage?${clear}"
select yn in "s3" "local"; do
    case $yn in
        s3 ) echo -e "${yellow}Setting up s3 for storage...${clear}"; invenio files location s3-default s3://hcommons-dev-invenio --default; break;;
        local ) echo -e "${yellow}Setting up local storage...${clear}"; invenio files location create --default default-location /opt/invenio/var/instance/data; break;;
    esac
done

echo -e "${yellow}Setting up admin roles and permissions...${clear}"
invenio roles create admin
invenio roles create administration
invenio roles create administration-moderation
invenio roles create admin-moderator
invenio access allow superuser-access role admin
invenio access allow superuser-access role administration
invenio access allow superuser-access role administration-moderation
invenio access allow administration-access role administration
invenio access allow administration-moderation role administration-moderation
echo -e "${yellow}Setting up OpenSearch index...${clear}"
invenio index init
echo -e "${yellow}Setting up custom metadata fields...${clear}"
invenio rdm-records custom-fields init
invenio communities custom-fields init
echo -e "${yellow}Compiling translations...${clear}"
pybabel compile -d /opt/invenio/src/translations
echo -e "${yellow}Setting up task queues...${clear}"
invenio queues declare

if [ $fixtures==1 ]
then
    echo -e "${yellow}Setting up fixtures in two stages (this may take a long time!!)...${clear}"
    invenio rdm fixtures
    invenio rdm-records fixtures & pid=$!
    # spinner during fixture setup
    i=1
    sp="\|/-"
    while ps -p $pid > /dev/null
    do
        printf "\b%c" "${sp:i++%4:1}"
        sleep 0.1
    done
else
    echo -e "${yellow}Skipping setting up fixtures (-f flag was not passed)...${clear}"
fi
echo -e "${green}All done setting up services."
echo -e "${green}Building and symlinking assets..."
bash ./scripts/build-assets.sh
echo -e "${green}Your instance is now ready to use.${clear}"