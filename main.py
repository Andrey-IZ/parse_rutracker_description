from parse_html.open_url import HtmlParserWebProxy
import json
from structure_data.film_descriptiion import FilmDescription


if __name__ == '__main__':
    parser = HtmlParserWebProxy()
    parser.connect_proxy('127.0.0.1', 9050)
    json.dump(parser.parse_film_descr_from_rutracker().to_dict(), open('film.txt', 'wt'), sort_keys=True, indent=4)
