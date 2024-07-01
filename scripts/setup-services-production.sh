#! /bin/bash

# This script sets up the services for the Knowledge Commons Works instance.
# It creates the database, sets up s3 storage, creates the admin user and role,
# sets up the OpenSearch index, custom metadata fields, compiles translations,
# sets up task queues, and creates the administrator role.
#
# If the -f flag is passed, it also sets up fixtures in two stages. This is not
# done by default since it can take a long time, particularly if large
# subject vocabularies are being used.
#
# This script is meant to be run in the production environment.

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

while getopts 'f' flag
do
    case "${flag}" in
        f) fixtures=1 ;;
        *) echo 'Error in command line parsing' >&2
           exit 1
    esac
done

echo -e "${yellow}Setting up services for Knowledge Commons Works instance...${clear}"
echo -e "${yellow}Creating the database...${clear}"
invenio db init create
echo -e "${yellow}Setting up s3 storage...${clear}"
invenio files location s3-default s3://{$INVENIO_S3_BUCKET_NAME} --default;
echo -e "${yellow}Setting up admin user and role...${clear}"
invenio roles create admin
invenio access allow superuser-access role admin
echo -e "${yellow}Setting up OpenSearch index...${clear}"
invenio index init
echo -e "${yellow}Setting up custom metadata fields...${clear}"
invenio rdm-records custom-fields init
invenio communities custom-fields init
echo -e "${yellow}Compiling translations...${clear}"
pybabel compile -d /opt/invenio/src/translations
echo -e "${yellow}Setting up task queues...${clear}"
invenio queues declare
echo -e "${yellow}Creating administrator role...${clear}"
invenio roles create administrator
if [ $fixtures==1 ]
then
    echo -e "${yellow}Setting up fixtures in two stages (this may take a long time!!)...${clear}"
    invenio rdm fixtures --verbose
    invenio rdm-records fixtures --verbose & pid=$!
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
echo -e "${green}Your instance is now ready to use.${clear}"