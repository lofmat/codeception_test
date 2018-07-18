# hw

# Setup [Ubuntu instruction] 
1. Install python3.6
```shell
$ sudo add-apt-repository ppa:deadsnakes/ppa

$ sudo apt-get update

$ sudo apt-get install python3.6
```
2. Install pip3
```shell
$ sudo apt-get -y install python3-pip
```
3. Install required modules:
```shell
$ pip3 install -r requirements.txt
```
# Run script
```shell
$ ./img_scraper.py --url "http://www.site.com" --base_dir "./site_images"
```
