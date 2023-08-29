from halo import Halo
import json
import jsonlines
from pathlib import Path
import requests
import subprocess
from traceback import print_exc
from typing import Optional, Union
import urllib
import os
from pprint import pprint
import re
from urllib.parse import unquote

from core_migrate.config import (
    GLOBAL_DEBUG,
    FILES_LOCATION,
    SERVER_DOMAIN
)
from core_migrate.utils import logger, valid_date, compare_metadata


def api_request(method:str='GET', endpoint:str='records', server:str='',
                args:str='', token:str='', params:dict[str, str]={},
                json_dict:Optional[Union[dict[str, str], list[dict]]]={},
                file_data:Optional[bytes]=None) -> dict:
    """
    Make an api request and return the response
    """
    debug = GLOBAL_DEBUG or True
    if not server:
        server = SERVER_DOMAIN
    if not token:
        token = os.environ['API_TOKEN']

    payload_args = {}

    api_url = f'https://{server}/api/{endpoint}'
    if args:
        api_url = f'{api_url}/{args}'
    if debug: print('url:', api_url)

    callfuncs = {'GET': requests.get,
                 'POST': requests.post,
                 'DELETE': requests.delete,
                 'PUT': requests.put,
                 'PATCH': requests.patch}
    callfunc = callfuncs[method]

    headers={'Authorization': f'Bearer {token}'}
    if json_dict and method in ['POST', 'PUT', 'PATCH']:
        headers['Content-Type'] = 'application/json'
        payload_args['data'] = json.dumps(json_dict)
    elif file_data and method in ['POST', 'PUT']:
        headers['content-type'] = 'application/octet-stream'
        # headers['content-length'] = str(len(file_data.read()))
        payload_args['data'] = file_data

    # files = {'file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}
    if debug:
        print(f'request to {api_url}')
        # print(f'headers: {headers}')
        print(f'params: {params}')
        print(f'payload_args: {payload_args}')
    response = callfunc(api_url, headers=headers, params=params,
                        **payload_args, verify=False)
    if debug: pprint(response)

    return {'status_code': response.status_code,
            'headers': response.headers,
            'json': response.json() if method != 'DELETE' else None,
            'text': response.text}

def create_invenio_record(metadata:dict, server:str='',
                          token:str='', secure:bool=False) -> dict:
    """
    Create a new Invenio record from the provided dictionary of metadata
    """
    debug = GLOBAL_DEBUG or True
    if debug: print('~~~~~~~~')
    if debug: pprint(metadata)

    # Check for existing record with same DOI
    if 'pids' in metadata.keys() and 'doi' in metadata['pids'].keys():
        my_doi = metadata['pids']["doi"]['identifier']
        doi_for_query = my_doi.split('/')
        same_doi = api_request(method='GET', endpoint=f'records?q=pids.doi.identifier%3D%22{doi_for_query[0]}%2F{doi_for_query[1]}%22', params={})
        if same_doi['status_code'] not in [200, 404]:
            raise requests.HTTPError(same_doi)

        if same_doi['status_code'] == 200 and \
                same_doi['json']['hits']['total'] > 0:
            print('Found existing record with same DOI...')
            logger.info('    found existing record with same DOI...')
            existing_metadata = same_doi['json']['hits']['hits'][0]
            # Check for differences in metadata
            differences = compare_metadata(existing_metadata, metadata)
            if differences:
                # TODO: Create new version as draft
                raise RuntimeError(f'Existing record with same DOI has different metadata: {differences}')
            if not differences:
                logger.info('    continuing with existing (same metadata)...')
                result =  {'status_code': 201,
                        'headers': 'existing record with same DOI and same data',
                        'json': existing_metadata,
                        'text': existing_metadata}
                return(result)

    # Make draft and publish
    logger.info('    creating new draft record...')
    result = api_request(method='POST', endpoint='records',
                        json_dict=metadata)
    if result['status_code'] != 201:
        raise requests.HTTPError(result)
    publish_link = result['json']["links"]["publish"]
    if debug: print('publish link:', publish_link)
    if debug: pprint(result['json'])

    return(result)


def fetch_draft_files(files_dict:dict[str, str]) -> dict:
    """
    Fetch listed files from a remote address.
    """
    url = 'https://www.facebook.com/favicon.ico'
    r = requests.get(url, allow_redirects=True)


def upload_draft_files(draft_id:str, files_dict:dict[str, str]) -> dict:
    """
    Upload the files for one draft record using the REST api.

    This process involves three api calls: one to initialize the
    upload, another to actually send the file content, and a third
    to commit the uploaded data.

    :param str draft_id:    The id number for the Invenio draft record
                            for which the files are to be uploaded.
    :param dict files_dict:     A dictionary whose keys are the filenames to
                                be used for the uploaded files. The
                                values are the corresponding full filenames
                                used in the humcore folder. (The latter is
                                prefixed with a hashed (?) string.)
    """
    debug = GLOBAL_DEBUG or True
    filenames_list = [{'key': f} for f in files_dict.keys()]
    output = {}

    # initialize upload
    initialization = api_request(method='POST', endpoint='records',
                         args=f'{draft_id}/draft/files',
                         json_dict=filenames_list)
    if initialization['status_code'] != 201:
        raise requests.HTTPError(initialization.text)
    output['initialization'] = initialization
    output['file_transactions'] = {}

    # upload files
    if debug: pprint(initialization['json']['entries'])
    for f in initialization['json']['entries']:
        # {'updated': '2023-06-15T21:00:14.644204+00:00', 'status': 'pending', 'links': {'self': 'https://localhost/api/records/5bge2-p9906/draft/files/p', 'content': 'https://localhost/api/records/5bge2-p9906/draft/files/p/content', 'commit': 'https://localhost/api/records/5bge2-p9906/draft/files/p/commit'}, 'created': '2023-06-15T21:00:14.642209+00:00', 'key': 'p', 'metadata': None}
        output['file_transactions'][f['key']] = {}
        server_string = SERVER_DOMAIN
        if SERVER_DOMAIN == "10.98.11.40":
            server_string = "invenio-dev.hcommons-staging.org"
        content_args = f['links']['content'
            ].replace(f'https://{server_string}/api/records/', '')
        assert re.findall(draft_id, content_args)
        commit_args = f['links']['commit'
            ].replace(f'https://{server_string}/api/records/', '')
        assert re.findall(draft_id, commit_args)

        filename = content_args.split('/')[3]
        # handle @ characters in filenames
        assert unquote(filename) in files_dict.keys()
        long_filename = files_dict[unquote(filename)].replace('/srv/www/commons/current/web/app/uploads/humcore/', '')
        with open(Path(FILES_LOCATION) / long_filename, "rb") as binary_file_data:
            if debug: print('^^^^^^^^')
            if debug: print(f'filesize is {len(binary_file_data.read())} bytes')
            binary_file_data.seek(0)
            content_upload = api_request(method='PUT', endpoint='records',
                                         args=content_args,
                                         file_data=binary_file_data)
            if debug: print('@@@@@@@')
            if debug: pprint(content_upload)
            if content_upload['status_code'] != 200:
                pprint(content_upload)
                raise requests.HTTPError(content_upload)
            output['file_transactions'][f['key']]['content_upload'] = content_upload

            assert content_upload['json']['key'] == unquote(filename)
            assert content_upload['json']['status'] == 'pending'
            assert content_upload['json']['links']['commit'] == f['links']['commit']

        # commit uploaded data
        upload_commit = api_request(method='POST', endpoint='records',
                                     args=commit_args)
        if upload_commit['status_code'] != 200:
            print('&&&&&&&')
            pprint(upload_commit)
            raise requests.HTTPError(upload_commit.text)

        if debug: print('&&&&&&&')
        if debug: pprint(upload_commit)
        output['file_transactions'][f['key']]['upload_commit'] = upload_commit
        assert upload_commit['json']['key'] == unquote(filename)
        assert valid_date(upload_commit['json']['created'])
        assert valid_date(upload_commit['json']['updated'])
        assert upload_commit['json']['status'] == "completed"
        assert upload_commit['json']['metadata'] == None
        assert upload_commit['json']['links']['content'] == f['links']['content']
        assert upload_commit['json']['links']['self'] == f['links']['self']
        assert upload_commit['json']['links']['commit'] == f['links']['commit']

    # confirm uploads for deposit
    confirmation = api_request('GET', 'records', args=f'{draft_id}/draft/files/{filename}')
    if debug: print('######')
    if debug: pprint(confirmation)
    if confirmation['status_code'] != 200:
        raise requests.HTTPError(confirmation.text)
    output['confirmation'] = confirmation
    if debug: pprint('confirmation')
    if debug: pprint(confirmation)
    return(output)


def delete_invenio_record(record_id:str) -> dict:
    """
    Delete an Invenio record with the provided Id
    """
    result = api_request(method='DELETE', endpoint='records',
                         args=f'{record_id}/draft')
    assert result['status_code'] == 204
    return(result)


def create_invenio_user(user_email:str) -> dict:
    """
    Create a new user account in the Invenio instance
    """
    debug = GLOBAL_DEBUG or True
    user_id:str
    new_user_flag = True
    existing_user = subprocess.Popen(['pipenv', 'run', 'invenio', 'shell',
        'scripts/core-migrate/core_migrate/core_migrate_users.py',
        'get-user-id', user_email],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
        )
    stdout_eu, stderr_eu = existing_user.communicate()
    if debug: pprint('****')
    if debug: pprint(stdout_eu)
    if debug: pprint(stderr_eu)
    if debug: pprint(existing_user.returncode)
    if existing_user.returncode == 0 and 'success' in stdout_eu:
        user_id = re.search(r'success: user id is (\d+)\'\n', stdout_eu)[1]
        print('YAAAAAY', user_id)
        new_user_flag = False
    else:
        make_user = subprocess.Popen(['pipenv', 'run', 'invenio', 'users',
                                    'create', user_email,
                                    '--password=password'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
        stdout, stderr = make_user.communicate()
        if debug: pprint('#####')
        if debug: pprint(stdout)
        if debug: pprint(stderr)
        assert make_user.returncode in [0, 2]  # will be 2 if user exists
        assert f'\'email\': \'{user_email}\'' in stdout
        print('created new user...')
        # ('User created successfully.\n'
        # "{'email': 'myaddress2@somedomain.edu', 'password': '****', 'active': "
        # 'False}\n')
        activate_user = subprocess.Popen(['pipenv', 'run', 'invenio', 'users',
                                        'activate', user_email],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        universal_newlines=True)
        stdout2, stderr2 = activate_user.communicate()
        if debug: pprint('&&&&')
        if debug: pprint(stdout2)
        if debug: pprint(stderr2)
        assert activate_user.returncode == 0
        print('activated new user...')

        user_confirmed = subprocess.Popen(['pipenv', 'run', 'invenio', 'shell',
                                        'scripts/core-migrate/core_migrate/core_migrate_users.py',
                                        'get-user-id', user_email],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        universal_newlines=True)
        stdout3, stderr3 = user_confirmed.communicate()
        if debug: pprint('****')
        if debug: pprint(stdout3)
        if debug: pprint(stderr3)
        if debug: pprint(user_confirmed.returncode)
        if user_confirmed.returncode == 0 and 'success' in stdout3:
            user_id = re.search(r'success: user id is (\d+)\'\n', stdout3)[1]
            new_user_flag = True
        elif user_confirmed.returncode == 2 and \
                'already associated with an account' in stdout3:
            print('User already exists.')
        else:
            print('Error: Failed to create new user')
            print_exc()

    return({'user_id': user_id,
            'new_user': new_user_flag})


def get_invenio_user(user_email:str) -> str:
    """
    Retrieve the user id of the user with the provided email address.
    """
    return create_invenio_user(user_email)['user_id']


def change_record_ownership(record_id:str, old_owner_id:str, new_owner_id:str
                            ) -> dict:
    """
    Change the owner of the specified record to a new user.
    """
    debug = GLOBAL_DEBUG or True
    changed_ownership = subprocess.Popen(['pipenv', 'run', 'invenio', 'shell',
                                          'scripts/core-migrate/core_migrate/core_migrate_users.py', 'change-owner',
                                          f'{record_id}',
                                          f'{old_owner_id}',
                                          f'{new_owner_id}'
                                          ],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True,
                                         universal_newlines=True)
    stdout, stderr = changed_ownership.communicate()
    if debug: print('&&&& change_record_ownership')
    # if debug: pprint(''.join(chr(s) for s in stdout))
    # if debug: pprint(''.join(chr(s) for s in stderr))
    # if debug: pprint(stdout.encode('latin1').decode('unicode_escape').encode('latin1').decode('utf8'))
    # if debug: pprint(chr(stderr))
    if debug: print(stdout)
    if debug: print(stderr)
    if debug: print(type(stderr))
    return(changed_ownership.returncode)


def create_invenio_community(community_label:str) -> dict:
    """
    """
    community_data = {
        "hcommons": {
            "slug": "hcommons",
            "metadata": {
                    "title": "Humanities Commons",
                    "description": "A community representing the main humanities commons domain.",
                    "website": "https://hcommons.org",
                    "organizations": [{"name": "Humanities Commons"}]
            }
        },
        "msu": {
            "slug": "msu",
            "metadata": {
                    "title": "MSU Commons",
                    "description": "A community representing the MSU Commons domain",
                    "website": "https://commons.msu.edu",
                    "organizations": [{"name": "MSU Commons"}]
            }
        },
        "ajs": {
            "slug": "ajs",
            "metadata": {
                    "title": "AJS Commons",
                    "description": "AJS is no longer a member of Humanities Commons",
                    "website": "https://ajs.hcommons.org",
                    "organizations": [{"name": "AJS Commons"}]
            }
        },
        "arlisna": {
            "slug": "arlisna",
            "metadata": {
                    "title": "ARLIS/NA Commons",
                    "description": "A community representing the ARLIS/NA Commons domain",
                    "website": "https://arlisna.hcommons.org",
                    "organizations": [{"name": "ARLISNA Commons"}]
            }
        },
        "aseees": {
            "slug": "aseees",
            "metadata": {
                    "title": "ASEEES Commons",
                    "description": "A community representing the ASEEES Commons domain",
                    "website": "https://aseees.hcommons.org",
                    "organizations": [{"name": "ASEEES Commons"}]
            }
        },
        "hastac": {
            "slug": "hastac",
            "metadata": {
                    "title": "HASTAC Commons",
                    "description": "",
                    "website": "https://hastac.hcommons.org",
                    "organizations": [{"name": "HASTAC Commons"}]
            }
        },
        "caa": {
            "slug": "caa",
            "metadata": {
                    "title": "CAA Commons",
                    "description": "CAA is no longer a member of Humanities Commons",
                    "website": "https://caa.hcommons.org",
                    "organizations": [{"name": "CAA Commons"}]
            }
        },
        "mla": {
            "slug": "mla",
            "metadata": {
                    "title": "MLA Commons",
                    "description": "A community representing the MLA Commons domain",
                    "website": "https://mla.hcommons.org",
                    "organizations": [{"name": "MLA Commons"}]
            }
        },
        "sah": {
            "slug": "sah",
            "metadata": {
                    "title": "SAH Commons",
                    "description": "A community representing the SAH Commons domain",
                    "website": "https://sah.hcommons.org",
                    "organizations": [{"name": "SAH Commons"}]
            }
        },
        "up": {
            "access": {
                    "visibility": "restricted",
                    "member_policy": "closed",
                    "record_policy": "closed",
                    # "owned_by": [{"user": ""}]
                    },
            "slug": "up",
            "metadata": {
                    "title": "UP Commons",
                    "description": "A community representing the UP Commons domain",
                    "website": "https://up.hcommons.org",
                    "organizations": [{"name": "UP Commons"}]
            }
        },
    }
    my_community_data = community_data[community_label]
    my_community_data["access"] = {
        "visibility": "public",
        "member_policy": "closed",
        "record_policy": "open",
        "review_policy": "open",
        # "owned_by": [{"user": ""}]
    }
    # admin_user_id = os.environ['ADMIN_USER_ID']
    # my_community_data['access']['owned_by'] = [{"user": admin_user_id}]
    # FIXME: a better way to get the current user?
    result = api_request("POST", endpoint="communities",
                         json_dict=my_community_data)
    print(result)
    if result['status_code'] != 201:
        raise requests.HTTPError(result)
    return(result)

def create_full_invenio_record(core_data:dict) -> dict:
    """
    Create an invenio record with file uploads, ownership, communities.
    """
    debug = GLOBAL_DEBUG or True
    existing_record = None
    result = {}
    file_data = core_data['files']
    submitted_data = {'custom_fields': core_data['custom_fields'],
                      'metadata': core_data['metadata'],
                      'pids': core_data['pids']
                      }
    # FIXME: only for testing!!!
    # random_doi = submitted_data['pids']['doi']['identifier'].split('-')[0]
    # random_doi = f'{random_doi}-{generate_random_string(5)}'
    # submitted_data['pids']['doi']['identifier'] = random_doi

    submitted_data['access'] = {'records': 'public', 'files': 'public'}
    submitted_data['files'] = {'enabled': True}

    # domains = [
    #     'ajs.hcommons.org', 'arlisna.hcommons.org', 'aseees.hcommons.org',
    #     'caa.hcommons.org', 'commons.msu.edu', 'hastac.hcommons.org',
    #     'hcommons.org', 'mla.hcommons.org', 'sah.hcommons.org',
    #     'up.hcommons.org'
    # ]

    # Create/find the necessary domain communities
    logger.info('    finding or creating community...')
    if 'kcr:commons_domain' in core_data['custom_fields'].keys() \
            and core_data['custom_fields']['kcr:commons_domain']:
        community_label = core_data['custom_fields']['kcr:commons_domain'].split('.')
        if community_label[1] == 'msu':
            community_label = community_label[1]
        else:
            community_label = community_label[0]

        if debug:
            print(f'checking for community {community_label}')
        # try to look up a matching community
        community_check = api_request('GET', endpoint='communities',
                                      args=community_label)
        # otherwise create it
        if community_check['status_code'] == 404:
            print('Community', community_label, 'does not exist. Creating...')
            community_check = create_invenio_community(community_label)
        community_id = community_check['json']['id']
        result['community'] = community_check

    # Create the basic metadata record
    logger.info('    finding or creating draft metadata record...')
    metadata_record = create_invenio_record(core_data)
    result['metadata_record_created'] = metadata_record
    if metadata_record['headers'] == 'existing record with same DOI and same data':
        existing_record = metadata_record['json']
    # if debug: print('#### metadata_record')
    # if debug: pprint(metadata_record)
    draft_id = metadata_record['json']['id']

    # Upload the files
    logger.info('    uploading files for draft...')
    if existing_record:
        same_files = True
        if len(metadata_record['json']['files']['entries']) == 0:
            same_files = False
            logger.info('    no files attached to existing record')
        for k, v in core_data['files']['entries'].items():
            existing_files = metadata_record['json']['files']['entries'][k]
            if v['key'] != existing_files['key'] or \
                    str(v['size']) != str(existing_files['size']):
                same_files = False
        if same_files:
            logger.info('    skipping uploading files (same already uploaded)...')
        else:
            raise RuntimeError(f'Existing record with same DOI has different files.\n{metadata_record["json"]["files"]["entries"]}\n !=\n {core_data["files"]["entries"]}')
    else:
        my_files = {}
        for k, v in file_data['entries'].items():
            my_files[v['key']] = metadata_record['json']['custom_fields'
                                                        ]['hclegacy:file_location']
        uploaded_files = upload_draft_files(draft_id=draft_id, files_dict=my_files)
        # if debug: print('@@@@ uploaded_files')
        # if debug: pprint(uploaded_files)
        result['uploaded_files'] = uploaded_files


    # Attach the record to the communities
    if existing_record and existing_record['is_draft'] != True:
        if community_id in existing_record['parent']['communities']['ids']:
            logger.info('    skipping attaching the record to the community (already published)...')
        else:
            raise RuntimeError('Existing published record with same DOI has different communities.')
    else:
        logger.info('    attaching the record to the community...')
        review_body = {"receiver":
                    {"community": f'{community_id}'},"type":"community-submission"}
        request_to_community = api_request('PUT', endpoint='records',
            args=f'{draft_id}/draft/review', json_dict=review_body)
        # if debug: print('&&&& request_to_community')
        # if debug: pprint(request_to_community)
        assert request_to_community['status_code'] == 200
        # submit_url = request_to_community['json']['links']['actions']['submit']
        # if debug: print(submit_url)
        request_id = request_to_community['json']['id']
        request_community = request_to_community['json']['receiver']['community']
        assert request_community == community_id
        result['request_to_community'] = request_to_community

        submitted_body = {"payload": {
                            "content": "Thank you in advance for the review.",
                            "format": "html"
                        }
        }
        review_submitted = api_request('POST', endpoint='requests',
            args=f'{request_id}/actions/submit',
            json_dict=submitted_body)
        result['review_submitted'] = review_submitted
        if debug: print('!!!!!!')
        if debug: pprint(review_submitted)
        if debug: pprint('%%%%%')
        if debug: print(submitted_data['metadata'])
        assert review_submitted['status_code'] == 200

        review_accepted = api_request('POST', endpoint='requests',
            args=f'{request_id}/actions/accept',
            json_dict={})
        if debug: print('!!!!!!')
        if debug: pprint(review_accepted)
        if review_accepted['status_code'] != 200:
            invite = {
                "members":[
                    {
                        "id":"3",
                        "type":"user"
                    }
                ],
                "role":"owner",
                "message":"<p>Hi</p>"
            }
            send_invite = api_request('POST', endpoint='communities',
                                    args=f'{community_id}/invitations',
                                    json_dict=invite,
                                    token="ehdWRDeM9ZSkwxwTZEPDnbZCdWYIaDa4YXxRcFJ61oQLvWy5OK1czlIoVoxd")
            print(send_invite)

        assert review_accepted['status_code'] == 200
        result['review_accepted'] = review_accepted

    # Publish the record (BELOW NOT NECESSARY BECAUSE PUBLISHED
    # AT COMMUNITY REVIEW ACCEPTANCE)
    # published = api_request('POST', endpoint='records',
    #     args=f'{draft_id}/draft/actions/publish')
    # result['published'] = published
    # if debug: print('^^^^^^')
    # if debug: pprint(published)
    # assert published['status_code'] == 202

    # Create/find the necessary user account
    logger.info('    creating or finding the user (submitter)...')
    # TODO: Make sure this will be the same email used for SAML login
    new_owner_email = core_data['custom_fields']['kcr:submitter_email']
    created_user = create_invenio_user(new_owner_email)
    new_owner_id = created_user['user_id']

    if existing_record and \
            existing_record['custom_fields']['kcr:submitter_email'
                                            ] == new_owner_email \
            and existing_record['parent']['access']['owned_by'][0]['user'] == new_owner_id:
        logger.info(f'    skipping re-assigning ownership of the record ')
        logger.info(f'    (already belongs to {new_owner_email}, '
                    f'user {new_owner_id})...')
    else:
        result['created_user'] = created_user

        # Change the ownership of the record
        logger.info(f'    re-assigning ownership of the record to the '
                    f'submitter ({new_owner_email}, '
                    f'{new_owner_id})...')
        current_owner_id = get_invenio_user('scottia4@msu.edu')
        changed_ownership = change_record_ownership(draft_id, new_owner_id,
                                                    current_owner_id)
        result.setdefault('changed_ownership', {})['return_code'] = changed_ownership
        assert changed_ownership == 0
        if debug: print('++++++++')
        if debug: pprint(changed_ownership)

    result['existing_record'] = existing_record
    return(result)


def load_records_into_invenio(start:int=1, stop:int=-1) -> None:
    """
    Create new InvenioRDM records (including deposit files) for serialized CORE deposits.
    """
    record_counter = 0
    failed_records = []
    successful_records = 0
    new_records = 0
    args = [start]
    if stop > -1:
        args.append(stop + 1)

    logger.info('Starting to load records into Invenio...')
    stop_string = '' if stop == -1 else f' to {stop}'
    logger.info(f'Loading records from {str(start) + stop_string}...')

    with jsonlines.open(Path(__file__).parent / 'data' /
                        'serialized_core_data.jsonl', "r") as json_source:
        import itertools
        top = itertools.islice(json_source, *args)
        for rec in top:
            current_record = start + record_counter
            rec_doi = rec["pids"]["doi"]["identifier"]
            rec_hcid = [r for r in rec['metadata']['identifiers'] if r['scheme'] == 'hclegacy-pid'][0]['identifier']
            rec_recid = [r for r in rec['metadata']['identifiers'] if r['scheme'] == 'hclegacy-record-id'][0]['identifier']
            logger.info(f'....starting to load record {current_record}')
            logger.info(f'    {rec_doi} {rec_hcid} {rec_recid}')
            spinner = Halo(
                text=f'    Loading record {current_record}', spinner='dots')
            spinner.start()
            try:
                result = create_full_invenio_record(rec)
                print(f'    loaded record {current_record}')
                successful_records += 1
                if not result['existing_record']:
                    new_records += 1
            except Exception as e:
                print('ERROR:', e)
                print_exc()
                logger.error(f'ERROR: {e}')
                logger.error(f'ERROR: {print_exc()}')
                failed_records.append((f'index {current_record}',
                                       rec_doi, rec_hcid, rec_recid))
            spinner.stop()
            logger.info(f'....done with record {current_record}')
            record_counter += 1

    print('Finished!')
    logger.info('All done loading records into InvenioRDM')
    message = (f'Processed {str(record_counter)} records in InvenioRDM '
               f'({start} to {start + record_counter - 1}) \n'
               f'    {str(successful_records)} successful \n'
               f'    {str(new_records)} successful \n'
               f'    {str(successful_records - new_records)} already existed \n'
               f'    {str(len(failed_records))} failed \n'
               )
    print(message)
    logger.info(message)
    if failed_records:
        logger.info('Failed records:')
        for r in failed_records:
            logger.info(r)


def delete_records_from_invenio(record_ids):
    """
    Delete the selected records from the invenioRDM instance.
    """
    print('Starting to delete records')
    for r in record_ids:
        print(f'deleting {r}')
        deleted = api_request('DELETE', f'records/{r}')
        pprint(deleted)
    print('finished deleting records')