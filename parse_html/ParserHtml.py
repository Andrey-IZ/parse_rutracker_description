import urllib.request as request
import requests

from parse_html.parse_rutracker import ParseFilmRutracker
from parse_html.tests import HTML_TEXT_RUTRACKER


class HtmlParser(object):
    def __init__(self, **kwargs):
        self._html_text = ''

    @property
    def html_text(self):
        return self._html_text

    def load(self):
        pass

    def get_html_text(self, address):
        return requests.get(address).text

    def get_web_file(self, address):
        return request.urlopen(address).read()

    def parse_film_descr_from_rutracker(self) -> dict:
        self._html_text = HTML_TEXT_RUTRACKER
        if self._html_text:
            parser = ParseFilmRutracker(self.get_html_text, self.get_web_file)
            result = parser.parse(self._html_text)
            return result
        return 'no'

