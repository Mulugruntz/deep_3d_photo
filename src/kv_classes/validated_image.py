from pathlib import Path

from kivy.app import App
from kivy.properties import ListProperty, StringProperty
from kivy.uix.image import Image


class ValidatedImage(Image):
    allowed_ext = ListProperty([])
    default_image = StringProperty()

    def reset(self):
        self.source = self.default_image

    def set_source(self, source: Path):
        if self.is_valid_nondefault_file(source):
            self.source = str(source)
        else:
            self.reset()
        App.get_running_app().root.ids.btn_start.revalidate()

    def is_default(self):
        return Path(self.source).resolve() == Path(self.default_image).resolve()

    def is_valid_nondefault_file(self, filepath: Path):
        res_filepath = filepath.resolve()
        return (
            res_filepath != Path(self.default_image).resolve()
            and res_filepath.is_file()
            and res_filepath.parts[-1].rsplit(".", maxsplit=1)[-1].lower()
            in self.allowed_ext
        )
