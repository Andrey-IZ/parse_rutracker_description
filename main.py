from parse_html.open_url import HtmlParserWebProxy

if __name__ == '__main__':
    parser = HtmlParserWebProxy()
    parser.connect_proxy('127.0.0.1', 9050)
    # parser.load_http(r'http://rutracker.org/forum/viewtopic.php?t=5244345', 80)
    # parser.load_http('http://rutracker.org/forum/viewtopic.php?t=5244345', 80)
    print(parser.parse_film_descr_from_rutracker())