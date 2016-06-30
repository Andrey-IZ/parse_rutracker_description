import socket

import requests

from parse_html.ParserHtml import HtmlParser


class HtmlParserWeb(HtmlParser):
    def __init__(self, **kwargs):
        super(HtmlParserWeb, self).__init__(**kwargs)
        self._dict_proxies = {}

    def connect_proxy(self, address, port, login=None):
            if login:
                user, password = login
                self._dict_proxies = dict(http='socks5://{}:{}@{}:{}'.format(user, password, address, port),
                                          https='socks5://{}:{}@{}:{}'.format(user, password, address, port))
            else:
                self._dict_proxies = dict(http='socks5://{}:{}'.format(address, port),
                                          https='socks5://{}:{}'.format(address, port))

    def _get_html_text(self, address):
        try:
            return requests.get(address, proxies=self._dict_proxies).text
        except requests.exceptions.ConnectionError as err:
            print('ERROR: {}'.format(err))
        return ''

    def load_http(self, address, port):
        try:
            self._html_text = self._get_html_text(address)
        except ConnectionError as err:
            raise ConnectionError('ERROR: don\'t possible connect to: {} - {}; \n'.format(self._dict_proxies , err))


class HtmlParserWebProxy(HtmlParserWeb):
    def __init__(self, **kwargs):
        super(HtmlParserWebProxy, self).__init__(**kwargs)
