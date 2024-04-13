from enum import Enum


class DocumentLang(Enum):
    EN = ("en", {"vi": "Tiếng Anh",
                 "en": "English"})
    VI = ("vi", {"vi": "Tiếng Việt",
                 "en": "Vietnamese"})

    def __str__(self):
        return self.value[0]

    @staticmethod
    def get_lang_from_abbrev(abbrev):
        __mapper = {'vi': DocumentLang.VI,
                    'en': DocumentLang.EN}
        return __mapper[abbrev]

    def get_full_lang_name(self, target_lang):
        return self.value[1][str(target_lang)]
