from parse_html.ParserHtml import HtmlParser


class HtmlParserFile(HtmlParser):
    def __init__(self, **kwargs):
        super(HtmlParserFile, self).__init__(**kwargs)

    def open_file(self, file):
        pass

    def parse_from_rutracker(self) -> dict:
        pass

