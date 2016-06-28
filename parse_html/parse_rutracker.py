import re
import urllib.request as request

# FD_GENRE_CHOICE = ('action', 'thriller', 'comedy', 'doc', 'other')
import requests

FD_GENRE_CHOICE = ('боевик', 'триллер', 'комедия', 'документальный', 'фантастика', 'приключения', 'детектив')


class FilmDescription(object):
    def __init__(self):
        self.title = ''
        self.title_rus = ''
        self.country = ''
        self.description = ''
        self.genre = ''
        self.year = ''
        self.length = ''
        self.subtitles = ''
        self.translation = ''
        self.video = ''
        self.cast = ''
        self.ratings = None
        self.screenshots = None
        self.poster = None
        self.web = None

    def __str__(self):
        return 'FilmDescription:' + self.web


class ParseFilmRutracker(object):
    def __init__(self, func_loader, func_loader_file):
        self.__hrml_loader = func_loader
        self.__web_file_loader = func_loader_file
        self.__path_div = r'<div class="post_body" id="p-70916052">'
        self.__path_div_end = r'<div class="clear">.*?</div><!--/post_wrap-->'
        self.__div_the_end = '</div><!--/post_wrap-->'
        self.__dict_pattern = {''}

    def parse(self, html_text):
        if html_text:
            film_descr = FilmDescription()
            pattern = '(?<=' + self.__path_div + ')' + r'(.*?)(?=' + self.__path_div_end + ')'
            m = re.search(pattern, html_text, re.DOTALL)
            if m:
                frame = m.group(0) + self.__div_the_end
                film_descr.web = frame
                film_descr.title, film_descr.title_rus, pos = self.__get_title(frame[0:])
                # film_descr.poster, pos = self.__get_poster(frame[pos:])
                # with open('poster.png', 'wb') as fd:
                #     fd.write(film_descr.poster)
                frame = frame[pos:]
                film_descr.country = self.__get_mini_descr(frame, 'Страна')
                film_descr.genre = self.__get_mini_descr(frame, 'Жанр')
                film_descr.description = self.__get_mini_descr(frame, 'Описание')
                film_descr.length = self.__get_mini_descr(frame, 'Продолжительность')
                film_descr.subtitles = self.__get_mini_descr(frame, 'Cубтитры')
                film_descr.year = self.__get_mini_descr(frame, r'Год(?:\sвыпуска)?')
                film_descr.video = self.__get_mini_descr(frame, r'(?:Качество\s)?видео')
                film_descr.cast = self.__get_mini_descr(frame, r'В\s+ролях')
                # film_descr.screenshots = self.__get_screenshots(frame)
                # for i, img in enumerate(film_descr.screenshots):
                #     with open(str(i) + '.png', 'wb') as fd:
                #         fd.write(img)
                film_descr.ratings = self.__get_ratings(frame)
                for i, img in enumerate(film_descr.ratings):
                    with open(str(i) + '.png', 'wb') as fd:
                        fd.write(img)
                return film_descr
        return None

    def __get_ratings(self, html_text):
        refs = re.findall(r'<var\s+class="postImg"\s+title="(http://.*?)">&#10;</var>', html_text, re.S)
        images = []
        for ref in refs:
            try:
                image = self.__web_file_loader(ref)
                if image:
                    images.append(image)
            except request.URLError:
                pass
        return images

    def __get_screenshots(self, html_text):
        div_screens = re.search(r'<div class="sp-head folded">.*?Скриншоты.*?(<div class="sp-body">).*?(</\s?div>)', html_text, re.S)
        if div_screens and len(div_screens.groups()) == 2:
            start = div_screens.end(1)
            end = div_screens.end(2)
            refs = re.findall(r'(?<=>)\s*<a .*?href="(http://.*?)".*?>', html_text[start:end], re.S)
            images = []
            for ref in refs:
                try:
                    text_ref = self.__hrml_loader(ref)
                    ref_image = re.search(r"<script>\s+loading_img\s+=\s+'(.*?)';", text_ref, re.S)
                    if ref_image and len(ref_image.groups()) == 1:
                        image = self.__web_file_loader(ref_image.group(1))
                        if image:
                            images.append(image)
                except request.URLError:
                    pass
            return images
        return None

    def __get_real_image(self, ref):
        pass

    def __get_mini_descr(self, html_text, tag):
        m_tag = re.search(r'(?<=>)(?:\s+)?' + tag + r'(?:\s+)?.*?:(?:\s+)?(.*?)<.*?(?=<br\s?/>)', html_text, re.S | re.I)
        if m_tag and m_tag.group(1):
            return m_tag.group(1)
        return ''

    def __get_poster(self, html_text):
            poster = re.search(r'(?<=>)\s*<var\s+class="postImg[" ].*?title="(http://.*?)".*?>', html_text, re.DOTALL)
            if poster and poster.group(1):
                ref = poster.group(1)
                try:
                    image = self.__web_file_loader(ref)
                except request.URLError:
                    image = None
                return image, poster.end()
            return ('', bytes()), 0

    def __get_title(self, html_text):
        m_title = re.search(r'(?<=>)(.*?)<.*?(?=<br\s?/>)', html_text, re.DOTALL)
        if m_title and m_title.group(1):
            title = m_title.group(1)
            title_div = re.search(r'([А-Яа-яёЁ 0-9]+)\s+[/\\]\s+([a-zA-Z 0-9]+)', title, re.MULTILINE)
            if title_div and len(title_div.groups()) == 2:
                return title_div.group(2), title_div.group(1), m_title.end()
            return title, '', m_title.end()
        return '', '', 0

