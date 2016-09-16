from parse_html.open_url import HtmlParserWebProxy
from argparse import ArgumentParser
import sys
import re


if __name__ == '__main__':
    parse_args = ArgumentParser(description='The loader info about films')
    parse_args.add_argument('-s', '--source', dest='source_list', action='store')
    parse_args.add_argument('-p', '--proxy', dest='proxy', action='store_true')
    parse_args.add_argument('-d', '--dest-to-save', dest='save_path', action='store', default='.')
    args = parse_args.parse_args(sys.argv[1:])
    if args and hasattr(args, 'source_list') and args.source_list:
        parser = HtmlParserWebProxy()
        if args.proxy:
            print('using proxy ...')
            parser.connect_proxy('127.0.0.1', 9050)
        for url in open(args.source_list, 'rt'):
            m = re.match(r'(https?://\S+).*?#?.*',url)
            if m:
                parser.load_info_film_from_rutracker(m.group(1).strip(), args.save_path)
        # json.dump(parser.parse_film_descr_from_rutracker().to_dict(), open('film.txt', 'wt'), sort_keys=True, indent=4)
