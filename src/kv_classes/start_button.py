import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import mainthread
from kivy.properties import ListProperty
from kivy.uix.button import Button

from wrapper import wrap_3d_pi_with_override
from utilities import download_models

START_DOWNLOAD = 'Download models (required first time)'
START_DOWNLOADING = 'Downloading models...'
START_DEEP = 'Start'
START_DEEPING = 'Working, please wait...'


class StartButton(Button):
    missing_models = ListProperty()
    # stop = threading.Event()
    # threads: List[threading.Thread] = []

    def run(self):
        self.set_disabled(True)
        if self.text == START_DOWNLOAD:
            self.text = START_DOWNLOADING
            t = threading.Thread(target=self.download_thread, args=())
            t.daemon = True
            # self.threads.append(t)
            t.start()
        elif self.text == START_DEEP:
            self.text = START_DEEPING
            t = threading.Thread(target=self.deep_thread, args=())
            t.daemon = True
            # self.threads.append(t)
            t.start()

    def deep_thread(self):
        print('Will start working...')
        try:
            wrap_3d_pi_with_override(
                Path(App.get_running_app().root.ids.input_load.text),
                depth_image=App.get_running_app().root.ids.image_depth,
                bar_total=App.get_running_app().root.ids.pb_total,
                bar_current=App.get_running_app().root.ids.pb_current,
            )
        except Exception as e:
            print(e)
            print('Done working: failure!')
        else:
            print('Done working: success!')
        self.text = START_DEEP
        self.set_disabled(False)

    def download_thread(self):
        print('Will start downloading the models...')
        try:
            download_models(
                self.missing_models,
                bar_total=App.get_running_app().root.ids.pb_total,
                bar_current=App.get_running_app().root.ids.pb_current,
            )
            self.text = START_DEEP
            self.missing_models = []
        except Exception as e:
            print(e)
            print('Model download: Done (failure).')
            self.text = START_DOWNLOAD
        else:
            print('Model download: Done (success).')
            self.text = START_DEEP
        self.set_disabled(False)

    @mainthread
    def append_logs(self, text):
        App.get_running_app().root.ids.logs.text += '\n' + text

    # def watchdog(self):
    #     while True:
    #         if self.stop.is_set():
    #             for t in self.threads:
    #                 if t.is_alive():
    #                     t.st