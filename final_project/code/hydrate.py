#!/usr/bin/env python3

#
# This script will walk through all the tweet id files and
# hydrate them with twarc. The line oriented JSON files will
# be placed right next to each tweet id file.
#
# Note: you will need to install twarc, tqdm, and run twarc configure
# from the command line to tell it your Twitter API keys.
#

import gzip
import json

from tqdm import tqdm
from twarc import Twarc2, expansions
from pathlib import Path

twarc = Twarc2(
    bearer_token="AAAAAAAAAAAAAAAAAAAAAEZYfgEAAAAA5GgorT90uemHY7goUzC8MAT8tnE%3DDNVp9U0WcZxqpQff2n0OfsUqUfJhdrRABrRINAkw44bKrIGnP5")
data_dirs = ['2022-02']


def main():
    for data_dir in data_dirs:
        for path in Path(data_dir).iterdir():
            if path.name.endswith('02-11-02.txt'):
                hydrate(path)


def _reader_generator(reader):
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)


def raw_newline_count(fname):
    """
    Counts number of lines in file
    """
    f = open(fname, 'rb')
    f_gen = _reader_generator(f.raw.read)
    return sum(buf.count(b'\n') for buf in f_gen)


def hydrate(id_file):
    print('hydrating {}'.format(id_file))

    gzip_path = id_file.with_suffix('.jsonl.gz')
    if gzip_path.is_file():
        print('skipping json file already exists: {}'.format(gzip_path))
        return

    num_ids = raw_newline_count(id_file)

    with gzip.open(gzip_path, 'w') as output:
        with tqdm(total=num_ids) as pbar:
            file = open(id_file, 'r')
            lines = file.readlines()
            tweet_ids= []
            # Strips the newline character
            for line in lines:
                tweet_ids.append(str(line.strip()))
            lookup = twarc.tweet_lookup(tweet_ids=tweet_ids)
            for page in lookup:
                # The Twitter API v2 returns the Tweet information and the user, media etc.  separately
                # so we use expansions.flatten to get all the information in a single JSON
                result = expansions.flatten(page)
                for tweet in result:
                    output.write(json.dumps(tweet).encode('utf8') + b"\n")
                    pbar.update(1)


if __name__ == "__main__":
    main()
