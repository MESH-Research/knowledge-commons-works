import hashlib


def file_md5(bytes_object):
    return hashlib.md5(bytes_object).hexdigest()


def build_file_links(record_id, base_api_url, filename):
    return {
        "content": f"{base_api_url}/records/{record_id}/files/{filename}/content",
        "iiif_api": (
            f"{base_api_url}/iiif/record:{record_id}:{filename}/full/full/0/"
            "default.png"
        ),
        "iiif_base": f"{base_api_url}/iiif/record:{record_id}:{filename}",
        "iiif_canvas": f"{base_api_url}/iiif/record:{record_id}/canvas/{filename}",
        "iiif_info": f"{base_api_url}/iiif/record:{record_id}:{filename}/info.json",
        "self": f"{base_api_url}/records/{record_id}/files/{filename}",
    }
