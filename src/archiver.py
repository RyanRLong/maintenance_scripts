#   MIT License
#
#  Copyright (c) 2019.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import argparse
import errno
import os
import os.path
import shutil
import time
from zipfile import ZipFile, ZIP_LZMA

DEFAULT_EXPIRATION_IN_DAYS = 60
ZIP_FILE_NAME = 'expired_archive.zip'

SECONDS_PER_DAY = 86400

now = time.time()


def get_file_list(search_path):
    """
    Gets the file list
    :param search_path: absolute path of the files to test
    :return:
    """
    for item in os.listdir(get_download_path(search_path)):
        yield os.path.abspath(
            (os.path.join(get_download_path(search_path), item)))


def get_download_path(raw_path):
    """
    Converts the absolute path to be compatible with OS

    :param raw_path:
    :return:
    """
    return os.path.join(raw_path)


def should_be_archived(file, days):
    """
    Returns true if file should be archived based on days since accessed

    :param file:
    :param days:
    :return:
    """
    if is_archive_file(file):
        return False
    return os.stat(file).st_mtime < get_expiration_date(days) or os.stat(
        file).st_ctime < get_expiration_date(days)


def is_archive_file(file):
    if os.path.isdir(file):
        return False
    if os.path.basename(file) == ZIP_FILE_NAME:
        return True


def get_expiration_date(days_old):
    """
    Returns the expiation timestamp

    :param days_old:
    :return:
    """
    return now - (days_old * SECONDS_PER_DAY)


def delete_archived_file(file):
    """
    Deletes the file

    :param file:
    :return:
    """

    if os.path.isfile(file):
        os.remove(file)
    else:
        shutil.rmtree(file)
    if os.path.exists(file):
        raise OSError(errno.EEXIST, "Unable to delete file", file)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Move files past an expiration date to an archive')
    parser.add_argument('expiration_in_days', type=int,
                        help='number of days since last access to consider expired')
    parser.add_argument('path', help='absolute path to be archived')

    args = parser.parse_args()
    # writing files to a zipfile
    try:
        expiration_in_days = args.expiration_in_days
    except IndexError:
        expiration_in_days = DEFAULT_EXPIRATION_IN_DAYS

    path = args.path
    files = [file for file in get_file_list(path)]

    with ZipFile(os.path.join(path,
                              ZIP_FILE_NAME), 'a',
                 compression=ZIP_LZMA) as zipp:
        for f in files:
            if should_be_archived(f, int(expiration_in_days)):
                print(f)
                zipp.write(f)
                delete_archived_file(f)
    exit(0)
