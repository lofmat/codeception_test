#!/usr/bin/env python3.6
import requests
from bs4 import BeautifulSoup
import os
import sys
import argparse
import datetime


# Command line parser
def create_parser():
    p = argparse.ArgumentParser()
    parser.add_argument('--url', required=True)
    parser.add_argument('--base_dir', required=True)
    return p


# Creating directory to save images
def create_dir(dir_path):
    act_dir_path = dir_path
    if os.path.exists(dir_path):
        timestamp = datetime.datetime.now().strftime("%y%m%d-%H%m%S")
        act_dir_path = os.path.join(dir_path, timestamp)
    try:
        os.mkdir(act_dir_path)
    except FileNotFoundError as exc:
        print(f'Error:\n{exc}')
        sys.exit(1)
    return act_dir_path


def get_url(url):
    try:
        r = requests.get(url)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        print(f'Error:{e}')
        sys.exit(1)
    return r


if __name__ == '__main__':
    # Create parser
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    target_url = namespace.url
    response_page = get_url(target_url)
    # Pulling data out of HTML
    data = response_page.text
    soup = BeautifulSoup(data, "lxml")
    # Create directory where will be saved images
    dir_name = create_dir(namespace.base_dir)
    # Loop over all img tags on the web page
    for link in soup.find_all('img'):
        # Image link may be stored as src or data-original attribute
        for image_link in link.get("src"), link.get("data-original"):
            if image_link:
                # Link may contains question mark
                # e.g src="https://www.somesite/blabla.png?strip=all&amp;w=210"
                # in other case will be returned "-1"
                q_index = image_link.find("?")
                if q_index != -1:
                    image_link = image_link[:q_index]
                if (image_link.endswith('jpg') or
                        image_link.endswith('png') or
                        image_link.endswith('gif') or
                        image_link.endswith('tif')):
                    # Case when src contains relative path
                    if not image_link.startswith('http:/') and not image_link.startswith('https:/'):
                        image_link = f'{target_url}/{image_link}'
                    response_img = get_url(image_link)
                    image_name = os.path.basename(image_link)
                    image_path = os.path.join(dir_name, image_name)
                    print(f'Current image is {image_path}')
                    with open(image_path, "wb") as f:
                        f.write(response_img.content)
