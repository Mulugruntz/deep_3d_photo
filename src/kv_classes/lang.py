from kivy.lang import Observable
import gettext

from constants import LOCALE_DIR


class Lang(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang, transalte=None):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang
        self._translate = transalte if transalte is not None else gettext.gettext
        self.switch_lang(self.lang)

    def __call__(self, text):
        return self._translate(text)

    def fbind(self, name, func, *largs, **kwargs):
        if name == "_":
            self.observers.append((func, largs, kwargs))
        else:
            return super(Lang, self).fbind(name, func, *largs, **kwargs)

    def funbind(self, name, func, *largs, **kwargs):
        if name == "_":
            key = (func, largs, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Lang, self).funbind(name, func, *largs, **kwargs)

    def switch_lang(self, lang):
        # get the right locales directory, and instanciate a gettext
        locales = gettext.translation('Deep3DPhoto', LOCALE_DIR, languages=[lang])
        self.ugettext = locales.gettext

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)
