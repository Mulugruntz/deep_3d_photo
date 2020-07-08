import os.path
from pathlib import Path

from kivy.app import App
from kivy.properties import ListProperty
from kivy.uix.button import Button
from plyer import filechooser


class FileChoose(Button):
    '''
    Button that triggers 'filechooser.open_file()' and processes
    the data response from filechooser Activity.
    '''

    selection = ListProperty([])

    def choose(self):
        '''
        Call plyer filechooser API to run a filechooser Activity.
        '''
        path = Path(App.get_running_app().root.ids.input_load.text)
        is_valid_path = Path(path := os.path.dirname(path)).exists() and bool(path)
        filechooser.open_file(
            on_selection=self.handle_selection,
            title="Pick a JPG file..",
            multiple=False,
            path=path if is_valid_path else os.path.expanduser("~"),
            filters=[("Image file (jpg)", "*.jpg")]
        )

    def handle_selection(self, selection):
        '''
        Callback function for handling the selection response from Activity.
        '''
        self.selection = selection

    def on_selection(self, *a, **k):
        '''
        Update TextInput.text after FileChoose.selection is changed
        via FileChoose.handle_selection.
        '''
        App.get_running_app().root.ids.input_load.text = str(self.selection[0])
        App.get_running_app().root.ids.image_client.source = str(self.selection[0])
        App.get_running_app().root.ids.image_depth.source = str('blank-transparent.png')
