import logging
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

sys.path.insert(0, str(Path(sys.base_prefix, 'src')))
sys.path.insert(0, str(Path(sys.base_prefix, '3d-photo-inpainting')))


print(sys.path)
print(sys._base_executable)
print(sys.base_exec_prefix)
print(sys.base_prefix)


from kv_classes import ComplexProgressBar, StartButton, AutoScrollView, FileChoose
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
        def f(dt=None):
            self.callback(self.format(record) + '\n')

        Clock.schedule_once(f)


class Deep3DPhotoWidget(Widget):
    def __init__(self, **kwargs):
        super(Deep3DPhotoWidget, self).__init__(**kwargs)
        # self.ids.btn_load.bind(on_press=self.cb_btn_load_on_press)

    # def cb_btn_load_on_press(self, event: MotionEvent) -> None:
    #     path = filechooser.open_file(title="Pick a JPG file..",
    #                              filters=[("Image file (jpg)", "*.jpg")])
    #     print(path)


class Deep3DPhotoApp(App):
    # def on_stop(self):
    #     self.root.ids.btn_start.stop.set()

    def build(self):
        log = logging.getLogger()
        log.level = logging.DEBUG
        log.addHandler(MyLabelHandler(lambda: App.get_running_app().root.ids.scrlv.append_message, logging.DEBUG))
        return Deep3DPhotoWidget()

    def on_start(self, **kwargs):
        missing_models = check_models_existence()
        if missing_models:
            self.root.ids.btn_start.missing_models = missing_models
            self.root.ids.btn_start.text = START_DOWNLOAD


def main():
    with redirect_stdout(KivyTextOut(delayed_callback=lambda: App.get_running_app().root.ids.scrlv.append_message)), \
         redirect_stderr(
             KivyTextOut(delayed_callback=lambda: App.get_running_app().root.ids.scrlv.append_message, std=sys.stderr)):

        Deep3DPhotoApp().run()


if __name__ == '__main__':
    main()
