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

    def get_info_film_from_rutracker(self, address, path_to_save):
        # html_text = HTML_TEXT_RUTRACKER
        html_text = self._get_html_text(address)
        fd = self._parse_film_descr_from_rutracker(html_text)
        title = '{1} ({0})_({2})_{3}'.format(fd.title_rus, fd.title,  re.sub(r'[;:\s,\]\[.]', '_', fd.genre), fd.video)
        filename = '{0}{1}{2}'.format(path_to_save, os.path.sep, title + '.html')
        with open(filename, 'wt') as f:
            f.writelines(fd.web)

    def _parse_film_descr_from_rutracker(self, html_text) -> FilmDescription:
        if html_text:
            parser = ParseFilmRutracker(self._get_html_text, self.get_web_file)
            result = parser.parse(html_text)
            return result
        return

