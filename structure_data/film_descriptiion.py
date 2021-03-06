import codecs


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

    def to_dict(self) -> dict:
        result = {}
        for k, v in self.__dict__.items():
            if k in ['poster']:
                result[k] = v[0], codecs.encode(v[1], "base64").decode(), v[2]
            elif k in ['screenshots', 'ratings']:
                image_list = []
                for ref, image, ext in v:
                    image_encode = codecs.encode(image,
                                                 "base64").decode()  # unpickled = codecs.decode(image_encode.encode() ,"base64")
                    image_list.append((ref, image_encode, ext))
                result[k] = image_list
            else:
                result[k] = v
        return result

    def from_dict(self, dict_load):
        for k, v in dict_load:
            if k in ['poster']:
                self.__dict__[k] = v[0], codecs.decode(v.encode(), "base64"). v[2]
            elif k in ['screenshots', 'ratings']:
                image_list = []
                for ref, image_encode, ext in v:
                    image = codecs.decode(image_encode.encode(), "base64")
                    image_list.append((ref, image, ext))
                self.__dict__[k] = image_list
            else:
                self.__dict__.update(dict_load)

    def __str__(self):
        return 'FilmDescription: \n{}'.format(self.__dict__)

