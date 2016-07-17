from parse_html.open_url import HtmlParserWebProxy
from argparse import ArgumentParser
import sys

if __name__ == '__main__':
    parse_args = ArgumentParser(description='The loader info about films')
    parse_args.add_argument('-s', '--source', dest='source_list', action='store')
    parse_args.add_argument('-p', '--proxy', dest='proxy', action='store_true')
    args = parse_args.parse_args(sys.argv[1:])
    if args and hasattr(args, 'source_list') and args.source_list:
        parser = HtmlParserWebProxy()
        if args.proxy:
            print('using proxy ...')
            parser.connect_proxy('127.0.0.1', 9050)
        for url in open(args.source_list, 'rt'):
            parser.load_info_film_from_rutracker(url.strip(), '.')
        # json.dump(parser.parse_film_descr_from_rutracker().to_dict(), open('film.txt', 'wt'), sort_keys=True, indent=4)
