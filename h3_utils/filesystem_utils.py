from email.mime import image
import re
import os, sys

import numpy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

import requests
from PIL import Image
from io import BytesIO


from consts import SERVER_URL
from h3_utils.path_configs import FolderPathsConfig
from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()


def get_presets():
    preset_folder = 'presets'
    presets = ['initial']
    if not os.path.exists(preset_folder):
        print('No presets found.')
        return presets

    return presets + [f[:f.index(".json")] for f in os.listdir(preset_folder) if f.endswith('.json')]

def download_image_from_url(url):
    log.info(f"Downloading image from URL: {url}")
    if SERVER_URL is not None and "https://" in SERVER_URL:
        if SERVER_URL.split("://")[1] in url:
            possible_uuid_uri = url.replace(SERVER_URL, "").replace("/photo", "").replace("/", "")
            path_local = FolderPathsConfig.path_outputs + f"/{possible_uuid_uri}"
            if os.path.exists(path_local):
                image = Image.open(path_local)
                numpy_image = numpy.asarray(image)
                log.info(f"Image found locally: {path_local}")
                return numpy_image
        else:
            log.info(f"Image not found locally or not on the same server. (URL: {url})")
            print(f"Image not found locally: {path_local}")
            save_uri = url.split("/")[-1]
            if "." not in save_uri:
                raise ValueError("URL does not contain a valid image extension.")
            if save_uri.split(".")[-1] not in ["jpg", "jpeg", "png", "webp"]:
                raise ValueError("URL does not contain a valid image extension.")
            path_local = os.path.join(FolderPathsConfig.path_outputs, save_uri)
            response = requests.get(url)
            np_image = numpy.asarray(Image.open(BytesIO(response.content)))
            assert np_image.dtype == numpy.uint8, "Input image must be of type uint8"
            return np_image
        

    else:
        save_uri = url.split("/")[-1]
        if "." not in save_uri:
            raise ValueError("URL does not contain a valid image extension.")
        if save_uri.split(".")[-1] not in ["jpg", "jpeg", "png", "webp"]:
            raise ValueError("URL does not contain a valid image extension.")
        path_local = os.path.join(FolderPathsConfig.path_outputs, save_uri)
        response = requests.get(url)
        np_image = numpy.asarray(Image.open(BytesIO(response.content)))
        assert np_image.dtype == numpy.uint8, "Input image must be of type uint8"
        return np_image


def get_model_filenames(folder_paths, extensions=None, name_filter=None):
    if extensions is None:
        extensions = ['.pth', '.ckpt', '.bin', '.safetensors', '.fooocus.patch']
    files = []

    if not isinstance(folder_paths, list):
        folder_paths = [folder_paths]
    for folder in folder_paths:
        files += get_files_from_folder(folder, extensions, name_filter)

    return files


def makedirs_with_log(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as error:
        print(f'Directory {path} could not be created, reason: {error}')


def get_files_from_folder(folder_path, extensions=None, name_filter=None):
    if not os.path.isdir(folder_path):
        raise ValueError("Folder path is not a valid directory.")

    filenames = []

    for root, _, files in os.walk(folder_path, topdown=False):
        relative_path = os.path.relpath(root, folder_path)
        if relative_path == ".":
            relative_path = ""
        for filename in sorted(files, key=lambda s: s.casefold()):
            _, file_extension = os.path.splitext(filename)
            if (extensions is None or file_extension.lower() in extensions) and (name_filter is None or name_filter in _):
                path = os.path.join(relative_path, filename)
                filenames.append(path)

    return filenames