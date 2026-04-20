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
echo -e "${yellow}Setting up s3 storage...${clear}"
invenio files location s3-default s3://$INVENIO_S3_BUCKET_NAME --default;
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
    # Seed ROR-backed vocabularies (funders, affiliations) from live ROR via
    # Zenodo. These are not in vocabularies.yaml and so are not loaded by
    # `invenio rdm-records fixtures`; without this step the deposit form's
    # funder and affiliation fields are empty until the first scheduled
    # process_ror_{funders,affiliations} job run.
    echo -e "${yellow}Seeding ROR-backed vocabularies (funders, affiliations) from Zenodo (this requires network egress to doi.org and zenodo.org)...${clear}"
    invenio vocabularies import -v funders
    invenio vocabularies import -v affiliations
    # Seed the awards vocabulary from OpenAIRE Graph (via Zenodo). Unlike
    # funders/affiliations, the upstream `awards` DATASTREAM_CONFIG has no
    # HTTP reader, so `invenio vocabularies import -v awards` would not pull
    # data; the HTTP-driven config lives only in the import_awards_openaire
    # JobType. The schedule is also registered (idempotently) below regardless
    # of -f, but for fresh installs we also fire one immediate run with
    # --run-now so the awards field in the deposit form is populated without
    # waiting up to a week for the next scheduled run.
    echo -e "${yellow}Seeding awards vocabulary from OpenAIRE (this requires network egress to zenodo.org and may transfer multi-GB data)...${clear}"
    invenio kcworks-jobs upsert import_awards_openaire \
        --title "Import Awards OpenAIRE" \
        --schedule "crontab:minute=0,hour=5,day_of_week=0" \
        --queue celery \
        --run-now
else
    echo -e "${yellow}Skipping setting up fixtures (-f flag was not passed)...${clear}"
fi

# Register recurring vocabulary refresh jobs as invenio-jobs Job rows.
# Idempotent: re-running upserts in place. Safe to run regardless of the -f
# flag because (without --run-now) it does not load data; it only records the
# schedule that the `scheduler` compose service (celery beat with
# RunScheduler) will dispatch. Schedules are offset by an hour so the four
# heavy network/index pulls don't overlap. The CORDIS pass is scheduled an
# hour after OpenAIRE because it only augments existing award records (its
# writer runs with insert=False, update=True), so it depends on the OpenAIRE
# pass having loaded the master award list first.
echo -e "${yellow}Registering scheduled vocabulary refresh jobs...${clear}"
invenio kcworks-jobs upsert process_ror_funders \
    --title "Load ROR funders" \
    --schedule "crontab:minute=0,hour=3,day_of_week=0" \
    --queue celery
invenio kcworks-jobs upsert process_ror_affiliations \
    --title "Load ROR affiliations" \
    --schedule "crontab:minute=0,hour=4,day_of_week=0" \
    --queue celery
invenio kcworks-jobs upsert import_awards_openaire \
    --title "Import Awards OpenAIRE" \
    --schedule "crontab:minute=0,hour=5,day_of_week=0" \
    --queue celery
invenio kcworks-jobs upsert update_awards_cordis \
    --title "Update Awards CORDIS" \
    --schedule "crontab:minute=0,hour=6,day_of_week=0" \
    --queue celery

echo -e "${green}All done setting up services."
echo -e "${green}Your instance is now ready to use.${clear}"