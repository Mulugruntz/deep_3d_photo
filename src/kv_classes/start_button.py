from __future__ import annotations
import sys
import threading
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.button import Button

from wrapper import wrap_3d_pi_with_override
from utilities import download_models

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from kv_classes import ComplexProgressBar, FileChoose

from kv_classes.localization import _


START_DOWNLOAD = _('Download models (required first time)')
START_DOWNLOADING = _('Downloading models...')
START_DEEP = _('Start')
START_DEEPING = _('Working, please wait...')
START_DEPTH = _('Generate Depth file')
START_DEPTHING = _('Generating Depth file...')


class TranslatedStr(str):
    def __eq__(self, other):
        return super(TranslatedStr, self).__eq__(_(other))


class StartButton(Button):
    missing_models = ListProperty()
    depth_handler: FileChoose = ObjectProperty(None)
    image_handler: FileChoose = ObjectProperty(None)
    bar_total: ComplexProgressBar = ObjectProperty(None)
    bar_current: ComplexProgressBar = ObjectProperty(None)

    @property
    def tr_text(self):
        return TranslatedStr(self.text)

    @tr_text.setter
    def tr_text(self, value):
        self.text = _(value)

    def run(self):
        self.revalidate()
        if self.disabled:
            return
        self.set_disabled(True)
        if self.tr_text == START_DOWNLOAD:
            self.tr_text = START_DOWNLOADING
            t = threading.Thread(target=self.download_thread, args=())
            t.daemon = True
            t.start()
        elif self.tr_text == START_DEEP:
            self.tr_text = START_DEEPING
            t = threading.Thread(target=self.deep_thread, args=())
            t.daemon = True
            t.start()
        elif self.tr_text == START_DEPTH:
            self.tr_text = START_DEPTHING
            t = threading.Thread(target=self.depth_thread, args=())
            t.daemon = True
            t.start()

    def depth_thread(self):
        print(_('Will generate the depth...'))
        try:
            wrap_3d_pi_with_override(
                Path(self.image_handler.bnd_image.source),
                depth_handler=self.depth_handler,
                bar_total=self.bar_total,
                bar_current=self.bar_current,
                just_depth=True,
            )
        except Exception as e:
            print(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      file=sys.stdout)
            print(_('Done working: failure!'))
        else:
            print(_('Done working: success!'))
        self.tr_text = START_DEPTH
        self.revalidate()
        # self.set_disabled(False)

    def deep_thread(self):
        print(_('Will start working...'))
        try:
            wrap_3d_pi_with_override(
                Path(self.image_handler.bnd_image.source),
                depth_handler=self.depth_handler,
                bar_total=self.bar_total,
                bar_current=self.bar_current,
                just_depth=False,
            )
        except Exception as e:
            print(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      file=sys.stdout)
            print(_('Done working: failure!'))
        else:
            print(_('Done working: success!'))
        self.tr_text = START_DEEP
        self.revalidate()

    def download_thread(self):
        print(_('Will start downloading the models...'))
        try:
            download_models(
                self.missing_models,
                bar_total=self.bar_total,
                bar_current=self.bar_current,
            )
            self.missing_models = []
        except Exception as e:
            print(e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      file=sys.stdout)
            print(_('Model download: Done (failure).'))
        else:
            print(_('Model download: Done (success).'))

        self.revalidate()

    @mainthread
    def append_logs(self, text):
        App.get_running_app().root.ids.logs.text += '\n' + text

    @mainthread
    def revalidate(self):
        if self.tr_text in [START_DOWNLOADING, START_DEPTHING, START_DEEPING]:
            self.set_disabled(True)
        elif self.missing_models:
            self.tr_text = START_DOWNLOAD
            self.set_disabled(False)
        else:
            self.set_disabled(self.image_handler.bnd_image.is_default())
            self.tr_text = START_DEPTH if self.depth_handler.bnd_image.is_default() else START_DEEP
