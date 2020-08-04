import sys
from pathlib import Path

GUESSED_MAIN_DIR = Path(__file__).parent.resolve()

sys.path.insert(0, str(GUESSED_MAIN_DIR / '3d-photo-inpainting'))
sys.path.insert(0, str(GUESSED_MAIN_DIR / 'src'))

import logging
from contextlib import redirect_stdout, redirect_stderr

from constants import RESOURCE_DIR, MAIN_DIR

if GUESSED_MAIN_DIR != MAIN_DIR:
    raise EnvironmentError(
        f'Something went wrong when initializing the environment! {GUESSED_MAIN_DIR} != {MAIN_DIR}'
    )

FAVICON = str(RESOURCE_DIR / 'deep3dphoto-256.png')

from kivy.config import Config

Config.set('kivy', 'window_icon', FAVICON)

from kivy.clock import Clock
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window




print(sys.path)
print(sys._base_executable)
print(sys.base_exec_prefix)
print(sys.base_prefix)


from kv_classes import ComplexProgressBar, StartButton, AutoScrollView, FileChoose
from kv_classes.localization import _, change_language_to, current_language, list_languages
from kv_classes.start_button import START_DOWNLOAD
from utilities import check_models_existence

Window.clearcolor = (.95, .95, .95, 1)


class KivyTextOut:
    def __init__(self, *_, delayed_callback, sep='', std=sys.stdout):
        self.delayed_callback = delayed_callback
        self.callback = None
        self.sep = sep
        self.terminal = std

    def dynamic_init(self):
        if self.callback is not None:
            return True
        try:
            self.callback = self.delayed_callback()
        except:
            return False
        self.write = self._new_write
        return True

    def _new_write(self, txt):
        self.callback(self.sep + txt)
        self.terminal.write(txt)

    def write(self, txt):
        if self.dynamic_init():
            self.write(txt)
        self.terminal.write(txt)

    def flush(self):
        pass


class MyLabelHandler(logging.Handler):
    def __init__(self, delayed_callback, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.delayed_callback = delayed_callback
        self.callback = None

    def emit(self, record):
        """using the Clock module for thread safety with kivy's main loop"""
        try:
            if self.callback is None:
                self.callback = self.delayed_callback()
        except:
            pass
        else:
            self.new_emit(record=record)
            self.emit = self.new_emit

    def new_emit(self, record):
        def func(dt=None):
            self.callback(self.format(record) + '\n')

        Clock.schedule_once(func)


class Deep3DPhotoWidget(Widget):
    def __init__(self, **kwargs):
        super(Deep3DPhotoWidget, self).__init__(**kwargs)


print(list_languages())
print(current_language())
change_language_to("fr")
print(current_language())


class Deep3DPhotoApp(App):
    lang = StringProperty('fr')

    def on_lang(self, instance, lang):
        change_language_to(lang)

    def build(self):
        self.icon = FAVICON
        return Deep3DPhotoWidget()

    def on_start(self, **kwargs):
        log = logging.getLogger()
        log.level = logging.DEBUG
        log.addHandler(MyLabelHandler(lambda: App.get_running_app().root.ids.scrlv.append_message, logging.DEBUG))
        missing_models = check_models_existence()
        btn_start = self.root.ids.btn_start
        if missing_models:
            btn_start.missing_models = missing_models
            btn_start.tr_text = START_DOWNLOAD

        btn_start.image_handler = self.root.ids.btn_image_load
        btn_start.depth_handler = self.root.ids.btn_depth_load
        btn_start.bar_total = self.root.ids.pb_total
        btn_start.bar_current = self.root.ids.pb_current

        btn_start.revalidate()


def main():
    #with redirect_stdout(KivyTextOut(delayed_callback=lambda: App.get_running_app().root.ids.scrlv.append_message)), \
    #     redirect_stderr(
    #         KivyTextOut(delayed_callback=lambda: App.get_running_app().root.ids.scrlv.append_message, std=sys.stderr)):
    with redirect_stdout(KivyTextOut(delayed_callback=lambda: App.get_running_app().root.ids.scrlv.append_message)):
        Deep3DPhotoApp().run()


if __name__ == '__main__':
    main()
