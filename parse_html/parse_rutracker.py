import re
from shutil import rmtree
import os
import urllib.request as request
from structure_data.film_descriptiion import FilmDescription


class ParseFilmRutracker(object):
    def __init__(self, func_loader, func_loader_file):
        self.__html_loader = func_loader
        self.__web_file_loader = func_loader_file
        self.__path_div = r'<div class="post_body" id="p-[0-9]+">'
        self.__path_div_end = r'<div class="clear">.*?</div>.*?(</div>\s*<!--/post_body-->)'
        # self.__div_the_end = '</div><!--/post_wrap-->'
        self.__compile_regex()

    def __compile_regex(self):
        self.__p_frame = re.compile(
            r'(<head.*?>.*?</head>).*?(' + self.__path_div + '.*?)(?:' + self.__path_div_end + ')', re.DOTALL)
        self.__p_title = re.compile(r'(?<=>)\s*(.*?)(?=<br\s?/>)', re.DOTALL)
        self.__p_title_div = re.compile(r'([А-Яа-яёЁ 0-9]+)\s+[/\\]\s+([a-zA-Z 0-9]+)', re.MULTILINE)
        self.__p_screen_ref = re.compile(
            r'\s*<a .*?href="(http://.*?\.((?:(?:png)|(?:jpe?g)|(?:gif)))[.\w]*)".*?>', re.S)
        self.__p_screen_ref_image = re.compile(r"<script>\s+loading_img\s+=\s+'(.*?)';", re.S)
        self.__p_div_screen = re.compile(
            r'<div class="sp-head folded">.*?Скриншоты.*?(<div class="sp-body">).*?(</\s?div>)', re.S)
        self.__p_rating_img = re.compile(r'<var class="postImg" title="(http://[^\s>]+[.](gif)\s*)"\s*>', re.S)
        self.__p_poster = re.compile(r'(?<=>)\s*<var\s+class="postImg[" ].*?title="(http://.*?)".*?>', re.DOTALL)

    def parse(self, html_text):
        if html_text:
            film_descr = FilmDescription()
            m = self.__p_frame.search(html_text, re.DOTALL)
            if m and len(m.groups()) == 3:
                film_descr.web = '<html>{}<body>{}</body></html>'.format(m.group(1), m.group(2) + m.group(3))
                frame = film_descr.web[m.end(1):]
                film_descr.title, film_descr.title_rus, pos = self.__get_title(frame)
                film_descr.poster, pos = self.__get_poster(frame[pos:])
                if film_descr.poster:
                    with open('poster.png', 'wb') as fd:
                        fd.write(film_descr.poster[1])
                frame = frame[pos:]
                film_descr.country = self.__get_mini_descr(frame, 'Страна')
                film_descr.genre = self.__get_mini_descr(frame, 'Жанр')
                film_descr.description = self.__get_mini_descr(frame, 'Описание')
                film_descr.length = self.__get_mini_descr(frame, 'Продолжительность')
                film_descr.subtitles = self.__get_mini_descr(frame, 'Cубтитры')
                film_descr.year = self.__get_mini_descr(frame, r'Год(?:\sвыпуска)?')
                film_descr.video = self.__get_mini_descr(frame, r'(?:Качество\s)?видео')
                film_descr.cast = self.__get_mini_descr(frame, r'В\s+ролях')
                film_descr.screenshots = self.__get_screenshots(frame)
                if film_descr.screenshots:
                    for i, (ref, img, ext) in enumerate(film_descr.screenshots):
                        with open('screen_' + str(i) + '.' + ext, 'wb') as fd:
                            fd.write(img)
                film_descr.ratings = self.__get_ratings(frame)
                if film_descr.ratings:
                    for i, (ref, img, ext) in enumerate(film_descr.ratings):
                        with open('rates_' + str(i) + '.' + ext, 'wb') as fd:
                            fd.write(img)
                return film_descr
        return None

    def save_to_file(self, film_descr: FilmDescription, path_to_save, filename):
        html_text = film_descr.web
        name_dir_file = filename + '_files'
        dir_path = path_to_save + os.path.sep + name_dir_file
        if os.path.exists(dir_path):
            rmtree(dir_path, True)
        os.mkdir(dir_path)
        os.chdir(dir_path)
        html_text = self._create_image(html_text, film_descr.screenshots, name_dir_file, 'screen')
        html_text = self._create_image(html_text, film_descr.poster, name_dir_file, 'poster')
        os.chdir('..')
        with open(filename + '.html', 'wt') as f:
            f.writelines(html_text)

    def _create_image(self, html_text:str, list_images, dir_images, prefix: str):
        if list_images:
            for i, (ref, image, ext) in enumerate(list_images):
                filename = '{}_{}.{}'.format(prefix, i, ext)
                with open(filename, 'wb') as f:
                    f.write(image)
                    sym = '&#10;'
                    pattern = r'(<a\s+href="{}"\s+(?:class="postLink")?.*?>\s*<var .*?>)({})(</var>\s*</a>)'.format(ref, sym)
                    repl = r'\1<img src="{}" class="postImg" alt="pic">\3'.format('./' + dir_images + '/' + filename)
                    html_text = re.sub(pattern, repl, html_text)
        return html_text

    def __get_ratings(self, html_text: str) -> list:
        images = []
        list_url = self.__p_rating_img.findall(html_text)
        for url, ext in list_url:
            if url.find('www.kinopoisk.ru') >= 0 or url.find('imdb') >= 0:
                try:
                    image_kp = self.__web_file_loader(url)
                    if image_kp:
                        images.append((url, image_kp, ext))
                except request.URLError as err:
                    print('ERROR (ratings): {}'.format(err))
        return images

    def __get_screenshots(self, html_text: str) -> list:
        div_screens = self.__p_div_screen.search(html_text)
        if div_screens and len(div_screens.groups()) == 2:
            start = div_screens.end(1)
            end = div_screens.end(2)
            refs = self.__p_screen_ref.findall(html_text[start:end])
            images = []
            for ref, ext in refs:
                try:
                    text_ref = self.__html_loader(ref)
                    ref_image = self.__p_screen_ref_image.search(text_ref)
                    if ref_image and len(ref_image.groups()) == 1:
                        image = self.__web_file_loader(ref_image.group(1))
                        if image:
                            images.append((ref, image, ext))
                except request.URLError as err:
                    print('ERROR (screenshots): {}'.format(err))
            return images
        return None

    def __get_mini_descr(self, html_text, tag) -> str:
        m_tag = re.search(r'(?<=>)(?:\s+)?' + tag + r'(?:\s+)?.*?:(?:\s+)?(.*?)<.*?(?=<br\s?/>)', html_text,
                          re.S | re.I)
        if m_tag and m_tag.group(1):
            return m_tag.group(1)
        return ''

    def __get_poster(self, html_text) -> tuple:
        poster = self.__p_poster.search(html_text)
        if poster and len(poster.groups()) == 2:
            ref = poster.group(1)
            ext = poster.group(2)
            try:
                image = self.__web_file_loader(ref)
            except request.URLError:
                image = None
            return (ref, image, ext), poster.end()
        return (), 0

    def __get_title(self, html_text) -> tuple:
        m_title = self.__p_title.search(html_text)
        if m_title and m_title.group(1):
            title = m_title.group(1)
            title_div = self.__p_title_div.search(title)
            if title_div and len(title_div.groups()) == 2:
                return title_div.group(2), title_div.group(1), m_title.end()
            return title, '', m_title.end()
        return '', '', 0
