from pathlib import Path
import requests
from zipfile import ZipFile

"""
Copyright 2023, MESH Research

FAST (Faceted Application of Subject Terminology) data files are made
available by OCLC under the Open Data Commons Attribution License
(ODC-By): http://www.oclc.org/research/activities/fast/odcby.htm
"""


def download_marcxml_files() -> dict[str]:
    """
    Download the raw marcxml files from the FAST repository.

    :returns: a dictionary of strings representing the paths of the
              downloaded marcxml files
    :rtype: str
    """
    print('Downloading FAST marcxml files...')
    url_base = "https://researchworks.oclc.org/researchdata/fast/"  # noqa
    source_filenames = ['FASTPersonal.marcxml.zip',
                        'FASTCorporate.marcxml.zip',
                        'FASTEvent.marcxml.zip',
                        'FASTTitle.marcxml.zip',
                        'FASTChronological.marcxml.zip',
                        'FASTTopical.marcxml.zip',
                        'FASTGeographic.marcxml.zip',
                        'FASTFormGenre.marcxml.zip',
                        'FASTMeeting.marcxml.zip'
                        ]
    output_list = []
    for f in source_filenames:
        bare_filename = f.replace(".zip", "")
        print(f'getting {bare_filename}...')
        download_url = f'{url_base}{f}'
        target_folder = Path(__file__).parent / 'downloads'
        target_path = target_folder / f

        with requests.get(download_url, stream=True) as req:
            if req.ok:
                with open(target_path, 'wb') as f:
                    print("saving to", target_path)
                    for chunk in req.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            f.write(chunk)

            else:  # HTTP status code 4XX/5XX
                print("Download failed: status code {}\n{}".format(
                    req.status_code, req.text))

        print('unzipping download into downloads folder...')
        with ZipFile(target_path, 'r') as zObject:
            zObject.extractall(path=target_folder)
        print(f'successfully downloaded {bare_filename}')
        output_list.append(target_path)
    print('All Done!')
    return output_list
