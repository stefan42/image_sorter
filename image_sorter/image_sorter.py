# -*- coding: utf-8 -*-
from enum import Enum
from datetime import datetime
import exifread
import argparse
import shutil
import re
import sys
import os


class CopyMode(Enum):
    MOVE = 1
    COPY = 2
    LINK = 3
    UNKNOWN = 4


def is_image_data_valid(image_data):
    return 'datetime' in image_data


def adjust_image_data(image_data):
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
    return valid_datas, invalid_datas


def get_file_op_str(config):
    if config['copy_mode'] is CopyMode.MOVE:
        return 'move'
    elif config['copy_mode'] is CopyMode.COPY:
        return 'copy'
    elif config['copy_mode'] is CopyMode.LINK:
        return 'link'
    else:
        return 'UNKNOWN'


def copy_file(config, old_file_name, new_file_name):
    if not os.path.isfile(old_file_name):
        print('unable to {} file \'{}\' to \'{}\' - old file does not exist'.format(get_file_op_str(config),
                                                                                    old_file_name, new_file_name),
              file=sys.stderr)
        return
    if os.path.exists(new_file_name):
        print('unable to {} file \'{}\' to \'{}\' - new file already exists'.format(get_file_op_str(config),
                                                                                    old_file_name, new_file_name),
              file=sys.stderr)
        return

    new_dir_name = os.path.dirname(new_file_name)
    if not os.path.exists(new_dir_name):
        print('creating new directory: ' + new_dir_name)
        if not config['dry_run']:
            os.makedirs(new_dir_name)

    print('{} file \'{}\' to \'{}\''.format(get_file_op_str(config), old_file_name, new_file_name))

    if not config['dry_run']:
        if config['copy_mode'] is CopyMode.MOVE:
            shutil.move(old_file_name, new_file_name)
        elif config['copy_mode'] is CopyMode.COPY:
            shutil.copy2(old_file_name, new_file_name)
        elif config['copy_mode'] is CopyMode.LINK:
            os.symlink(old_file_name, new_file_name)
        else:
            sys.exit(1)
    return


def get_new_image_path(config, image_data):
    new_path = config['output_folder']
    if config['subfolders']:
        new_path = os.path.join(new_path, image_data['datetime'].strftime("%Y_%m_%d"))
    return new_path


def get_new_raw_image_path(config, image_data):
    return os.path.join(get_new_image_path(config, image_data), "raw")


def get_raw_image_name(image_name):
    p = re.compile('(.*)jpg$', re.IGNORECASE)
    m = p.match(image_name)
    if not m:
        print('unable to get raw image name for ' + image_name, file=sys.stderr)
        return None
    raw_image_name = m.group(1) + 'CR2'
    if os.path.isfile(raw_image_name):
        return raw_image_name
    else:
        return None


def copy_valid_image(config, index, image_data):
    old_image_name = image_data['image_name']
    new_image_name = os.path.join(get_new_image_path(config, image_data),
                                  'IMG_{:05d}_{}.jpg'.format(index, image_data['datetime'].strftime("%Y%m%d_%H%M%S")))
    copy_file(config, old_image_name, new_image_name)
    old_raw_image_name = get_raw_image_name(old_image_name)
    if old_raw_image_name:
        new_raw_image_name = os.path.join(get_new_raw_image_path(config, image_data),
                                          'IMG_{:05d}_{}.CR2'.format(index,
                                                                     image_data['datetime'].strftime("%Y%m%d_%H%M%S")))
        copy_file(config, old_raw_image_name, new_raw_image_name)


def copy_invalid_image(config, image_data):
    print('WARNING: {} has no exif data, skipping'.format(image_data['image_name']), file=sys.stderr)
    pass


def copy_images(config, image_datas):
    (valid_datas, invalid_datas) = split_valid_from_invalid_data(image_datas)
    print('Got {} with correct EXIF datetimes, but {} without'.format(len(valid_datas), len(invalid_datas)))
    sorted_valid_images_datas = sorted(adjust_image_datas(valid_datas), key=lambda k: k['datetime'])
    image_index = 1
    for image_data in sorted_valid_images_datas:
        copy_valid_image(config, image_index, image_data)
        image_index += 1
    for image_data in invalid_datas:
        copy_invalid_image(config, image_data)


def scan_image(image_name):
    f = open(image_name, 'rb')
    tags = exifread.process_file(f, details=False)
    result = {'image_name': image_name}
    if 'EXIF DateTimeOriginal' in tags:
        date_str = ''
        try:
            date_str = tags['EXIF DateTimeOriginal'].values
            date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
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
        if not os.path.isdir(input_folder):
            print('Error: input directory ' + input_folder + ' does not exist.', file=sys.stderr)
            sys.exit(1)
        for file_name in os.listdir(input_folder):
            norm_file_name = file_name.lower()
            # print('processing: ' + file_name)
            if norm_file_name.endswith(".jpg") or norm_file_name.endswith('.jpeg'):
                image_datas.append(scan_image(os.path.join(input_folder, file_name)))
    return image_datas


def parse_copy_mode(input_string):
    if input_string == "move":
        return CopyMode.MOVE
    if input_string == "copy":
        return CopyMode.COPY
    if input_string == "link":
        return CopyMode.LINK
    return CopyMode.UNKOWN


def parse_args():
    parser = argparse.ArgumentParser(description='Sort images in correct order')
    parser.add_argument('input_folders', metavar='I', nargs='+',
                        help='input folders')
    parser.add_argument('-n', '--dry_run',
                        help='perform dry run',
                        dest='dry_run', required=False, action='store_true')
    parser.add_argument('-m', '--copy_mode',
                        help='specify the copy mode, allowed values [copy,move,link]',
                        dest='copy_mode', required=True)
    parser.add_argument('-s', '--subfolders',
                        help='create subfolders for each day of the trip',
                        dest='subfolders', required=False, action='store_true')
    parser.add_argument('-o', '--out', metavar='folder',
                        help='output folder',
                        dest='output_folder', required=True)
    args = parser.parse_args()
    result = {}
    # print(str(args))
    if args.input_folders:
        folders = []
        for input_folder in args.input_folders:
            folders.append(os.path.abspath(input_folder))
        result['input_folders'] = folders
    if args.output_folder:
        result['output_folder'] = os.path.abspath(args.output_folder)
    result['dry_run'] = args.dry_run
    result['copy_mode'] = parse_copy_mode(args.copy_mode)
    result['subfolders'] = args.subfolders
    return result


def main():
    config = parse_args()
    # print(config)
    image_datas = scan_input_folders(config['input_folders'])
    print('scanned ' + str(len(image_datas)) + ' images')

    copy_images(config, image_datas)


if __name__ == "__main__":
    main()
