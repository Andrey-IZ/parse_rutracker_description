import re
from shutil import rmtree, move
import os
import urllib.request as request
from structure_data.film_descriptiion import FilmDescription


class ParseFilmRutracker(object):
    def __init__(self, func_loader, func_loader_file, download_file_on_disk):
        self.__html_loader = func_loader
        self.__web_file_loader = func_loader_file
        self.__download_file_on_disk = download_file_on_disk
        self.__path_div = r'<div class="post_body" id="p-[0-9]+">'
        self.__path_div_end = r'<div class="clear">.*?</div>.*?(</div>\s*<!--/post_body-->)'
        self.__compile_regex()

    def __compile_regex(self):
        self.__p_frame = re.compile(
            r'(<head.*?>.*?</head>).*?(' + self.__path_div + '.*?)(?:' + self.__path_div_end + ')', re.DOTALL)
        self.__p_title = re.compile(r'<span.*?>\s*([а-яА-яёЁ0-9\s(),.:;"\']+)\s*'
                                    r'(?:/?\s*([a-zA-z\s0-9(),.:;"\']+))?.*?'
                                    r'<span\s*class="post-b".*?>(?:(?:\s*Страна.*?)|'
                                    r'(?:\s*Год.*?))</span>', re.DOTALL | re.I)
        self.__p_title_div = re.compile(r'([А-Яа-яёЁ 0-9]+)\s+[/\\]\s+([a-zA-Z 0-9]+)', re.MULTILINE)
        self.__p_screen_ref = re.compile(
            r'\s*<a .*?href="(http://.*?\.((?:(?:png)|(?:jpe?g)|(?:gif)))[.\w]*)".*?>', re.M)
        self.__p_screen_ref_image = re.compile(r"<script>\s+loading_img\s+=\s+'(.*?)';", re.S)
        self.__p_screen_ref_radikal_image = re.compile(
            r'<div itemscope itemtype="http://schema.org/ImageObject">\s+'
            r'<img\s+src="(.*?)".*? itemprop="contentUrl".*?/>', re.S)
        ''''''
        self.__p_rating_img = re.compile(r'<var class="postImg" title="(http://[^\s>]+[.](gif)\s*)"\s*>', re.S)
        self.__p_poster = re.compile(r'(?<=>)\s*<var\s+class="postImg[" ].*?title="'
                                     r'(http://.*?\.((?:(?:png)|(?:jpe?g)|(?:gif))))".*?>', re.DOTALL)

    def parse(self, html_text) -> FilmDescription:
        if html_text:
            film_descr = FilmDescription()
            m = self.__p_frame.search(html_text, re.DOTALL)
            if m and len(m.groups()) == 3:
                film_descr.web = '<html>{}<body>{}</body></html>'.format(m.group(1), m.group(2) + m.group(3))
                frame = film_descr.web[m.end(1):]
                film_descr.title, film_descr.title_rus, pos = self.__get_title(frame)
                film_descr.poster, pos = self.__get_poster(film_descr.title, frame)
                frame = frame[pos:]
                film_descr.country = self.__get_mini_descr(frame, 'Страна')
                film_descr.genre = self.__get_mini_descr(frame, 'Жанр')
                film_descr.description = self.__get_mini_descr(frame, 'Описание')
                film_descr.length = self.__get_mini_descr(frame, 'Продолжительность')
                film_descr.subtitles = self.__get_mini_descr(frame, 'Cубтитры')
                film_descr.year = self.__get_mini_descr(frame, r'Год(?:\sвыпуска)?')
                film_descr.video = self.__get_quality(frame)
                film_descr.cast = self.__get_mini_descr(frame, r'В\s+ролях')
                film_descr.screenshots = self.__get_screenshots(film_descr.title, frame)
                film_descr.ratings = self.__get_ratings(film_descr.title, frame)
                return film_descr
        return None

    def save_to_file(self, film_descr: FilmDescription, path_to_save, filename):
        if film_descr:
            html_text = film_descr.web
            name_dir_files = filename + '_files'
            print(film_descr.title + ': save to file: {0} ...'.format(filename))
            os.chdir(path_to_save)
            # print(film_descr.title + ': get curcwd = ' + os.getcwd())
            dir_path = filename
            if os.path.exists(dir_path):
                rmtree(dir_path, False)

            os.makedirs(name_dir_files)

            os.chdir(name_dir_files)
            # print(film_descr.title + ': get curcwd = ' + os.getcwd())
            html_text = self._load_css(film_descr.title, html_text, name_dir_files)
            html_text = self._load_js(film_descr.title, html_text, name_dir_files)
            print(film_descr.title + ': saving screenshots ...')
            html_text = self._create_image(html_text, film_descr.screenshots, name_dir_files, 'screen')
            print(film_descr.title + ': saving poster ...')
            html_text = self._create_image(html_text, [film_descr.poster], name_dir_files, 'poster')
            print(os.path.abspath(dir_path + os.path.sep + '..'))
            os.chdir('..')
            print(film_descr.title + ': get curcwd = ' + os.getcwd())
            print(film_descr.title + ': saving web page: "{0}/{1}" ...'.format(os.getcwd(), filename))
            with open(filename + '.html', 'wt') as f:
                f.writelines(html_text)

            new_dir = filename
            s = re.search(r'([\s])',filename)
            if s:
                new_dir = filename[:s.start()]

            try:
                os.makedirs(new_dir)
            except FileExistsError as err:
                print(err)
                rmtree(new_dir, False)
                os.makedirs(new_dir)

            move(filename + '.html', os.path.join(new_dir, filename + '.html'))
            move(name_dir_files, os.path.join(new_dir, name_dir_files))
            os.chdir('..' )
            return True
        return False

    def _load_css(self, title, html_text: str, dir_files):
        print('{}: load css ...'.format(title))
        pattern = r'(<link\s+href=")(.*?)([^/]+[.]\w+)\s*("\s+rel="stylesheet">)'
        html_text = self._move_web_to_local_file(title, dir_files, html_text, pattern)
        return html_text

    def _load_js(self, title, html_text: str, dir_files):
        print('{}:load js ...'.format(title))
        pattern = r'(<script\s+src=")(.*?)([^/]+[.]\w+)\s*("\s*>.*?</script>)'
        html_text = self._move_web_to_local_file(title, dir_files, html_text, pattern)
        return html_text

    def _move_web_to_local_file(self, title, dir_files, html_text, pattern):
        list_re = re.findall(pattern, html_text, re.DOTALL)
        if list_re:
            for i, item_re in enumerate(list_re):
                web_file_name = item_re[2]
                file_web_path = item_re[1]
                file_web_path = file_web_path if file_web_path[:5] == 'http:' else 'http:' + file_web_path
                print('\t{} - {}) name= {}'.format(title, i, web_file_name))
                self.__download_file_on_disk(file_web_path + web_file_name, web_file_name)

                file_path = './' + dir_files + '/'
                repl = r'\1{}\3\4'.format(file_path)
                html_text = re.sub(pattern, repl, html_text, 1, re.DOTALL)
        print('')
        return html_text

    def _create_image(self, html_text: str, list_images, dir_files, prefix: str):
        if list_images:
            print('create image ... ')
            sym = '&#10;'
            for i, (ref, image, ext) in enumerate(list_images):
                filename = '{}_{}.{}'.format(prefix, i, ext)
                print('\t{}'.format(filename))
                with open(filename, 'wb') as f:
                    f.write(image)
                    # scr = '<var class="postImg" title="http://i69.fastpic.ru/thumb/2016/0622/bc/8c3a6dfb955623db9d9aa38fdc9489bc.jpeg">&#10;</var>'
                    # psr = '<var class="postImg postImgAligned img-right" title="http://i74.fastpic.ru/big/2016/0622/fc/26d51fc5c409f73f9ef75317798c66fc.jpg">&#10;</var>'
                    ref_web_name = re.sub(r'\w+://.*?[^/]+/([^/]+)\.(?:(?:(\w+)\.html?$)|(?:(\w+)[^(?:\.html)]))',
                                          r'\1', ref)
                    if prefix == 'screen':
                        pattern = '(<a\\s+href="http://.*?/{1}?\\.[a-z]+\\.html"\\s+(?:class="postLink")?.*?>)' \
                                  '\\s*<var\\s+class="postImg"\\s+.*?title="http://.*?/{1}?\\.[a-z]+".*?>' \
                                  '({0})(</var>\\s*</a>)'.format(sym, ref_web_name)
                    elif prefix == 'poster':
                        pattern = '<var\\s+class="postImg"? .*?title="http://.*?/{1}\\.[a-z]+".*?>' \
                                  '({0})</var>'.format(sym, ref_web_name)
                    else:
                        print("Error: Invalid option")
                        return ''
                    # pattern = r'(?P<tag_a>(<a\s+href="{}"\s+(?:class="postLink")?.*?>)?\s*<var\s+.*?>)({})(</var>\s*(?(tag_a)(?:</a>)|(?:)))'.format(ref, sym)
                    repl = r'<a href="{0}" class="postLink"><img src="{0}" class="postImg" alt="pic"></a>'.format(
                        './' + dir_files + '/' + filename)
                    # repl = '_____________'
                    html_text = re.sub(pattern, repl, html_text)
        return html_text

    def __get_ratings(self, title, html_text: str) -> list:
        images = []
        list_url = self.__p_rating_img.findall(html_text)
        if list_url:
            print('{}: get ratings ...'.format(title))
            for url, ext in list_url:
                if url.find('www.kinopoisk.ru') >= 0 or url.find('imdb') >= 0:
                    try:
                        image_kp = self.__web_file_loader(url)
                        if image_kp:
                            images.append((url, image_kp, ext))
                    except request.URLError as err:
                        print('ERROR (ratings): {}'.format(err))
        return images

    def __get_screenshots(self, title, html_text: str) -> list:
        print('{}: get screenshots ...'.format(title), end=' ')
        refs = self.__p_screen_ref.findall(html_text)
        print('({})'.format(len(refs)))
        images = []
        for i, (ref, ext) in enumerate(refs):
            try:
                text_ref = self.__html_loader(ref)
                if re.search(r'http://radikal.ru', ref):
                    ref_image = self.__p_screen_ref_radikal_image.search(text_ref)
                else:
                    ref_image = self.__p_screen_ref_image.search(text_ref)
                if ref_image and len(ref_image.groups()) == 1:
                    link = ref_image.group(1)
                    image = self.__web_file_loader(link)
                    if image:
                        images.append((ref, image, ext))
                        print('{0}:\t{1}'.format(i,ref))
            except request.URLError as err:
                print('ERROR (screenshots): {}'.format(err))
        return images

    def __get_quality(self, html_text):
        tag = r'Качество(?:\\s+видео)?'
        m_quality = re.search(r'(?<=>)\s*' + tag + r'.*?:(?:\s+)?(.*?)(?=<br\s*?/>)', html_text, re.I)
        if m_quality and m_quality.group(1):
            res_str = re.sub(r'<.*?>', '', m_quality.group(1))
            print('\tКачество: {}'.format(res_str.strip()))
            return res_str.strip()
        return ''

    def __get_mini_descr(self, html_text, tag) -> str:
        m_tag = re.search(r'' + tag + r'.*?:\s*(.*?)(?=<br\s?/>)', html_text,  re.S | re.I)
        if m_tag and m_tag.group(1):
            res_str = re.sub(r'<.*?>', '', m_tag.group(1)).strip()
            print('\t{0}: {1}'.format(tag, res_str))
            return res_str
        return ''

    def __get_poster(self, title, html_text) -> tuple:
        poster = self.__p_poster.search(html_text)
        if poster and len(poster.groups()) == 2:
            print('{}: get poster ...'.format(title), end=': ')
            ref = poster.group(1)
            print(ref)
            ext = poster.group(2)
            try:
                image = self.__web_file_loader(ref)
            except request.URLError:
                image = None
            return (ref, image, ext), poster.end()
        return (), 0

    def __get_title(self, html_text) -> tuple:
        m_title = self.__p_title.search(html_text)
        if m_title and len(m_title.groups()) >= 1:
            print('get title ...', end='')
            title_rus, title = m_title.groups()
            title_rus = '' if title_rus is None else title_rus
            title = '' if title is None else title
            print('title = ', title_rus, title)
            return title_rus.strip(), title.strip(), m_title.end()
        return '', '', 0
