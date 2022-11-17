#!/usr/bin/env python3

HELP="""
Example:

$ ./kazneb.py "https://kazneb.kz/ru/bookView/view?brId=1561103&simple=true"

All downloaded files will be saved into current directory.
If you want to save files into different directory, you can 
use '-o/--output' option:

$ ./kazneb.py -o /tmp "https://kazneb.kz/ru/bookView/view?brId=1561103&simple=true"

"""

import signal
import logging
import requests
import re
import os
import sys

from argparse import ArgumentParser, RawDescriptionHelpFormatter

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class KaznebBook:

    def __init__(self, url):
        assert url is not None, "url argument must not be None"
        self.url = url
        self.pages = None
    
    def loadinfo(self):
        resp = requests.get(self.url)
        
        resp.raise_for_status()

        self.pages = re.findall('src: \"(\/FileStore\/dataFiles\/\w+\/\d+\/\d+\/content\/[^"]+)', resp.text)

        logger.debug("%d pages was found", len(self.pages))

    def download(self, path):
        '''
        Download full book page-by-page
        '''
        if self.pages is None:
            self.loadinfo()

        [self.downloadpage(p, path) for p in self.pages]

    def downloadpage(self, url, path):
        """
        Download single page by url
        """
        filename = re.search('\/(\d+\.\w+)\?', url).group(1)
        abspath = os.path.join(path, filename)

        with open(abspath, 'wb') as f:
            with requests.get('http://kazneb.kz/%s' % url, stream=True) as r:
                r.raise_for_status()
                
                [f.write(chunk) for chunk in r.iter_content(1024)]

        logging.info("%s was download successfully to %s with size = %d", 
            filename, path, os.path.getsize(abspath))
            

def do_main():

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    argparser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=HELP)
    
    argparser.add_argument(
        'book_url',
        help="book URL you want to be downloaded")
    argparser.add_argument(
        '-o', '--output-directory',
        help="Current directory by default",
        default='.')

    args = argparser.parse_args()
    
    book = KaznebBook(args.book_url)
    book.loadinfo()

    book.download(args.output_directory)
        
if __name__ == '__main__':
    do_main()
