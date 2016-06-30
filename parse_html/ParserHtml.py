import urllib.request as request
import requests
import os.path
import re
from parse_html.parse_rutracker import ParseFilmRutracker, FilmDescription
from parse_html.tests import HTML_TEXT_RUTRACKER
from parse_html.tests import HTML_TEXT_RUTRACKER2


class HtmlParser(object):
    def __init__(self, **kwargs):
        # self._html_text = ''
        pass

    # @property
    # def html_text(self):
    #     return self._html_text

    def load(self):
        pass

    def _get_html_text(self, address):
        return requests.get(address).text

    def get_web_file(self, address):
        return request.urlopen(address).read()

    def get_info_film_from_rutracker(self, address, path_to_save='.'):
        # html_text = HTML_TEXT_RUTRACKER
        html_text = self._get_html_text(address)
        parser = ParseFilmRutracker(self._get_html_text, self.get_web_file)
        fd = parser.parse(html_text)
        title = '{1} ({0})_({2})_{3}'.format(fd.title_rus, fd.title,  re.sub(r'[;:\s,\]\[.]', '_', fd.genre), fd.video)
        parser.save_to_file(fd, path_to_save, title)

