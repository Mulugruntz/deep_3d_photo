import os.path
from pathlib import Path

from kivy.properties import ListProperty, ObjectProperty, DictProperty
from kivy.uix.button import Button
from plyer import filechooser
from kv_classes.localization import _


class FileChoose(Button):
    '''
    Button that triggers 'filechooser.open_file()' and processes
    the data response from filechooser Activity.
    '''

    selection = ListProperty([])
    filetype = DictProperty({"title": _("Pick a file..."), "filters": []})
    bnd_text_input = ObjectProperty(None)
    bnd_image = ObjectProperty(None)

    def choose(self):
        '''
        Call plyer filechooser API to run a filechooser Activity.
        '''
        path = Path(self.bnd_text_input.text)
        is_valid_path = Path(path := os.path.dirname(path)).exists() and bool(path)
        properties = dict(
            on_selection=self.handle_selection,
            title=_("Pick a JPG file.."),
            multiple=False,
            path=path if is_valid_path else os.path.expanduser("~"),
            filters=[(_("Image file (jpg)"), "*.jpg")]
        )
        properties.update(self.filetype)
        filechooser.open_file(**properties)

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
        self.bnd_text_input.text = str(self.selection[0])
        self.bnd_image.set_source(Path(str(self.selection[0])))
