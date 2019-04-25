import os
import sys
import zipfile

import requests

from src import config


def dl_relevant_archive(url, dir, callback):
    response = requests.get(url, stream=True)
    file_path = os.path.join(dir, config.RELEVANT_ZIP_NAME)
    with open(file_path, "wb") as f:
        dl = 0
        for data in response.iter_content(chunk_size=4096):
            dl += len(data)
            f.write(data)
            if callback is not None:
                callback(dl, config.RELEVANT_ZIP_NAME, 0)


def dl_archive_files(entries, dir, callback):
    file_c = 1
    for c_id, url in entries:
        response = requests.get(url, stream=True)
        file_name = "kstat_" + c_id + ".xls"
        file_path = os.path.join(dir, file_name)
        with open(file_path, "wb") as f:
            dl = 0
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                if callback is not None:
                    callback(dl, file_name, file_c, len(entries))
        file_c += 1


def get_relevant_page():
    r = requests.get(config.RELEVANT_DATA_URL)
    return r.text if r.ok else None


def get_page(url):
    r = requests.get(url)
    return r.text if r.ok else None
