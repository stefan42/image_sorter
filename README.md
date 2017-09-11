# image_sorter

A small script which collects images from different imput folders and sorts them by the date.

When I'm on vacation, I use different cameras (smartphone, digital camera, SLR,...) with different image naming conventions. But I want the images to be sorted by the time they were taken. This scripts scans the input folders, reads the exif data and sorts the images. You can even create a subfolder for each day of the trip.

## Usage
```
usage: image_sorter.py [-h] [-n] -m COPY_MODE [-s] -o folder I [I ...]

Sort images in correct order

positional arguments:
  I                     input folders

optional arguments:
  -h, --help            show this help message and exit
  -n, --dry_run         perform dry run
  -m COPY_MODE, --copy_mode COPY_MODE
                        specify the copy mode, allowed values [copy,move,link]
  -s, --subfolders      create subfolders for each day of the trip
  -o folder, --out folder
                        output folder
```
