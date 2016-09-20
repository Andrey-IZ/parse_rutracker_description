import os.path
from concurrent.futures import ProcessPoolExecutor, as_completed

from parse_html.open_url import HtmlParserWebProxy
from argparse import ArgumentParser
import sys
import re


if __name__ == '__main__':
    parse_args = ArgumentParser(description='The loader info about films')
    parse_args.add_argument('-s', '--source', dest='source_list', action='store')
    parse_args.add_argument('-p', '--proxy', dest='proxy', action='store_true')
    parse_args.add_argument('-d', '--dest-to-save', dest='save_path', action='store', default='.')
    parse_args.add_argument('-t', '--parallel-threading', dest='parallel_threading', type=int, default=0)

    args = parse_args.parse_args(sys.argv[1:])
    if args and hasattr(args, 'source_list') and args.source_list:
        parser = HtmlParserWebProxy()
        if args.proxy:
            print('using proxy ...')
            parser.connect_proxy('127.0.0.1', 9050)
        count = args.parallel_threading
        with open(args.source_list, 'rt') as fd:
            lists_num = fd.readlines()
        if args.parallel_threading != 0:
            pool = ProcessPoolExecutor(max_workers=args.parallel_threading)
        futures = []
        for url in lists_num:
            m = re.match(r'(https?://\S+).*?#?.*', url)
            if m:
                if args.parallel_threading == 0:
                    parser.load_info_film_from_rutracker(m.group(1).strip(), args.save_path)
                else:
                    futures.append(pool.submit(parser.load_info_film_from_rutracker, m.group(1).strip(),
                                               os.path.abspath(args.save_path)))

        for x in as_completed(futures):
            print(x.result() if 'OK' else '--> Error')
