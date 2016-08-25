#!/usr/bin/env python3

# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import exifread
import argparse
import shutil
import sys
import os


def is_image_data_valid(image_data):
    return 'datetime' in image_data

def adjust_image_data(image_data):
    if image_data['camera'] == 'Canon PowerShot SX270 HS':
        image_data['datetime'] = image_data['datetime'] + timedelta(hours=1)
    return image_data

def adjust_image_datas(image_datas):
    result = []
    for image_data in image_datas:
        result.append(adjust_image_data(image_data))
    return result

def split_valid_from_invalid_data(image_datas):
    valid_datas = []
    invalid_datas = []
    for image_data in image_datas:
        if is_image_data_valid(image_data):
            valid_datas.append(image_data)
        else:
            invalid_datas.append(image_data)
    return (valid_datas, invalid_datas)

def copy_valid_image(config, index, image_data):
    old_image_name = image_data['image_name']
    new_image_name = os.path.join(config['output_folder'], 'IMGWe are the {} who say "{}!"'.format('knights', 'Ni')    
    if not config['dry_run']:
        if config['move_files']:
            pass
# TODO
        else:
            pass
#            shutil.copy2(old_image_name, new_image_name)
#            shutil.copy2(old_raw_name, new_ras_name)
    pass

def copy_invalid_image(config, image_data):
# TODO
    pass

def copy_images(config, image_datas):
    (valid_datas, invalid_datas) = split_valid_from_invalid_data(image_datas)
    print('Got ' + str(len(valid_datas)) + ' with correct EXIF datetimes, but ' + str(len(invalid_datas)) + ' without')
    sorted_valid_images_datas = sorted(valid_datas, key=lambda k: k['datetime'])
    image_index = 1
    for image_data in sorted_valid_images_datas:
        copy_valid_image(config, image_index, image_data)
        image_index += 1
    for image_data in invalid_datas:
        copy_invalid_image(config, image_data)


def scan_image(image_name):
    f = open(image_name, 'rb')
    tags = exifread.process_file(f, details=False)
    result = {}
    result['image_name'] = image_name
    if 'EXIF DateTimeOriginal' in tags:
        try:
            date_str = tags['EXIF DateTimeOriginal'].values
            date_obj = datetime.strptime(date_str,'%Y:%m:%d %H:%M:%S')
            if date_obj:
                result['datetime'] = date_obj
        except ValueError:
            print('wrong image format in image \'' + image_name + '\' - \'' + date_str + '\'', file=sys.stderr)
    if 'Image Model' in tags:
        result['camera'] = tags['Image Model'].values
    return result

def scan_input_folders(input_folders):
    image_datas = []
    for input_folder in input_folders:
        if (not os.path.isdir(input_folder)):
            print('Error: input directory ' + input_dir + ' does not exist.')
            sys.exit(1)
        for file_name in os.listdir(input_folder):
            norm_file_name = file_name.lower()
            print('processing: ' + file_name)
            if norm_file_name.endswith(".jpg") or norm_file_name.endswith('.jpeg'):
                image_datas.append(scan_image(os.path.join(input_folder, file_name)))
    return image_datas

def parse_args():
    parser = argparse.ArgumentParser(description='Sort images in correct order')
    parser.add_argument('input_folders', metavar='I', nargs='+',
                    help='an integer for the accumulator')
    parser.add_argument('-o', '--out', help='output folder', dest='output_folder', metavar='folder', required=True)
    args = parser.parse_args()
    result = {}
    print(str(args))
    if args.input_folders:
        result['input_folders'] = args.input_folders
    if args.output_folder:
        result['output_folder'] = args.output_folder
# TODO configure dry run
    result['dry_run'] = True
# TODO configure move/copy
    result['move_files'] = True
    return result

def main():
    config = parse_args()
    print(config)
    image_datas = scan_input_folders(config['input_folders'])
    print('scanned ' + str(len(image_datas)) + ' images')

    copy_images(config, image_datas)

if __name__ == "__main__":
  main()
