import translations.en as en
import translations.heb as heb


class Localization:
    def __init__(self, code):
        if code == "en":
            self._mod = en
            self._code = 0
        else:
            self._mod = heb
            self._code = 1

    def get(self, arg) -> str:
        return getattr(self._mod, arg)

    @property
    def code(self):
        return self._code
