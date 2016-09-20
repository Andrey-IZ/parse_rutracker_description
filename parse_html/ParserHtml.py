import urllib.request as request
import requests
import os.path
import re
from parse_html.parse_rutracker import ParseFilmRutracker
# from parse_html.tests import HTML_TEXT_RUTRACKER
# from parse_html.tests import HTML_TEXT_RUTRACKER2


class HtmlParser(object):
    def __init__(self, **kwargs):
        # self._html_text = ''
        pass

    # @property
    # def html_text(self):
    #     return self._html_text

    def load(self):
        pass

    def download_file_on_disk(self, url, filename_on_disk):
        request.urlretrieve(url, filename_on_disk)

    def _get_html_text(self, url) -> str:
        return requests.get(url).text

    def get_web_file(self, address):
        try:
            return request.urlopen(address).read()
        except ConnectionResetError as err:
            print(err)
            return None


    def load_info_film_from_rutracker(self, address, path_to_save='.') -> bool:
        # html_text = HTML_TEXT_RUTRACKER
        print('parsing web site: {}'.format(address))
        html_text = self._get_html_text(address)
        parser = ParseFilmRutracker(self._get_html_text, self.get_web_file,
                                    self.download_file_on_disk)
        fd = parser.parse(html_text)
        if fd:
            title = '{1} ({0})_({2})_{4}_{3}'.format(re.sub(r'[_;:"\'\\/\s.]', '_', fd.title_rus),
                                                 re.sub(r'[;:\\/\s.]', '_', fd.title),
                                                 re.sub(r'[;:\\/\s,\]\[.]', '_', fd.genre),
                                                 re.sub(r'[\[\]\\/]', '_', fd.video),
                                                 fd.year)
            print('==== SAVE ==== title: {0}; curdir = {1}'.format(title, os.getcwd()))
            if parser.save_to_file(fd, path_to_save, title):
                print('========= web page is saved =================')
                return True
        return False

