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
                result[k] = codecs.encode(v, "base64").decode()
            elif k in ['screenshots', 'ratings']:
                image_list = []
                for image in v:
                    image_encode = codecs.encode(image,
                                                 "base64").decode()  # unpickled = codecs.decode(image_encode.encode() ,"base64")
                    image_list.append(image_encode)
                result[k] = image_list
            else:
                result[k] = v
        return result

    def from_dict(self, dict_load):
        for k, v in dict_load:
            if k in ['poster']:
                self.__dict__[k] = codecs.decode(v.encode(), "base64")
            elif k in ['screenshots', 'ratings']:
                image_list = []
                for image_encode in v:
                    image = codecs.decode(image_encode.encode(), "base64")
                    image_list.append(image)
                self.__dict__[k] = image_list
            else:
                self.__dict__.update(dict_load)

    def __str__(self):
        return 'FilmDescription: \n{}'.format(self.__dict__)

