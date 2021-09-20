#!/usr/bin/env python
#
# Usage: python read_gzip_sample_records.py gzip_fp [csv_fp] [nlines]
#

import gzip
import sys
import os


def read_gzip(src, dest, nl):
    try:
        with gzip.open(src, 'rb') as gz:
            records = [next(gz) for x in range(nl)]
        with open(dest, 'w') as csv:
            csv.writelines(records)
    except StopIteration:
        pass


if __name__ == '__main__':
    try:
        src_gzip = os.path.abspath(sys.argv[1])
        if not os.path.isfile(src_gzip):
            raise IOError(src_gzip + ' is not a valid file')
    except IndexError:
        raise IndexError('Provide the source gzip file path')
    try:
        dest_csv = sys.argv[2]
        dest_path = os.path.abspath(os.path.dirname(dest_csv))
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)
    except IndexError:
        dest_csv = os.path.basename(src_gzip).rsplit('.', 1)[0] + '.csv'
    try:
        nlines = int(sys.argv[3])
    except IndexError or TypeError:
        nlines = 10
    
    read_gzip(src_gzip, dest_csv, nlines)
