#!/usr/bin/env python3.6
import requests
from bs4 import BeautifulSoup
import os
import sys
import argparse
import datetime
from pathlib import PurePath, Path
import glob

# Command line parser
def create_parser():
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True, help="Site url e.g http://www.spiegel.de")
    p.add_argument('--base_dir', required=True, help="Directory where will be saved images")
    return p


# Creating directory to save images
def create_dir(dir_path):
    """
    Create directory where will be stored image
    :param dir_path: desired directory name
    :return: path to directory that was created
    """
    actual_dir_path = dir_path
    # Create sub directory in case if directory already exist
    if Path(dir_path).exists():
        timestamp = datetime.datetime.now().strftime("%y%m%d-%H%m%S")
        actual_dir_path = PurePath(dir_path).joinpath(timestamp)
    try:
        os.mkdir(actual_dir_path)
    # Catch situation when the directory can't be created
    # e.g. C:\some\path in Linux
    except FileNotFoundError as exc:
        print(f'Error:\n{exc}')
        sys.exit(1)
    print(f'Images will be saved in: {Path(actual_dir_path).resolve()}')
    return actual_dir_path


def get_url(site_url):
    """
    Get link of image
    :param site_url: site address e.g. http://www.spiegel.de
    :return: response object
    """
    try:
        r = requests.get(site_url)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException) as e:
        print(f'Error:{e}')
        sys.exit(1)
    return r


def download_img(i_link):
    """
    Download the image that is stored by the link
    :param i_link: url of the image e.g. https://some_image.jpg
    """
    response_img = get_url(i_link)
    image_name = PurePath(i_link).name
    image_path = PurePath(dir_name).joinpath(image_name)
    print(f' > Current image is {i_link}')
    # Download only unique images
    if not Path(image_path).exists():
        with open(image_path, "wb") as f:
            f.write(response_img.content)
        if not Path(image_path).exists():
            print(f'Error: The following image wasn\'t downloaded {image_path}')
    else:
        print(f' > > > Image {i_link} has been already downloaded. Skipped.')


# Images link may be stored as values of src or some custom attribute.
# In case with custom attribute we don't know a name of this attribute.
# That why we must explore all attributes that img tag may contains
def get_all_links_from_img_tag(attrs, base_addr):
    """
    :param attrs: dictionary that contains all attributes of the img tag
    :param base_addr: site address e.g. http://www.spiegel.de
    :return: list of urls that were extracted from tag attributes
    """
    links_list = []
    for attr_name, attr_value in attrs.items():
        if isinstance(attr_value, str):
            attr_value = attr_value.strip()
            # Relative links
            if str(attr_value).startswith('//'):
                links_list.append(f'http:{attr_value}')
            elif str(attr_value).startswith('/'):
                links_list.append(f'{base_addr}/{attr_value}')
            # http/https links
            elif str(attr_value).startswith('http'):
                links_list.append(attr_value)
            # Cases like this
            # <img src="image-src.png" srcset="image-1x.png 1x, image-2x.png 2x">
            elif attr_name == "srcset":
                tlist = str(attr_value).split(",")
                for i in tlist:
                    links_list.append(str(i).split(" ")[0])
    for l in links_list:
        # Case like www.site.com?resize=....
        if '?' in l:
            q_index = l.find("?")
            new_link = l[:q_index]
            links_list[links_list.index(l)] = new_link
    return links_list


def files_count(somedir):
    extensions = ['jpg', 'png', 'gif', 'tif', 'svg']
    print(f'Were downloaded: ')
    total = 0
    for e in extensions:
        f_count = len(glob.glob1(somedir, f'*.{e}'))
        if f_count > 0:
            print(f'... *.{e}: {f_count}')
            total += f_count
    print(f'Total: {total}')


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
        curr_link_attrs = link.attrs
        img_urls = get_all_links_from_img_tag(curr_link_attrs, target_url)
        for url in img_urls:
            download_img(url)
    files_count(dir_name)

