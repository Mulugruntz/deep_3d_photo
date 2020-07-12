import inspect
import sys

from typing import Union, Callable, Type, TypeVar

from kivy.clock import mainthread
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.stacklayout import StackLayout
from kv_classes.localization import _
from utilities import f


T = TypeVar('T')


def call_function_get_frame(func, *args, **kwargs):
    """
  Calls the function *func* with the specified arguments and keyword
  arguments and snatches its local frame before it actually executes.
  """

    frame = None
    trace = sys.gettrace()

    def snatch_locals(_frame, name, arg):
        nonlocal frame
        if frame is None and name == 'call':
            frame = _frame
            sys.settrace(trace)
        return trace

    sys.settrace(snatch_locals)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(trace)
    return frame, result


class ComplexProgressBar(StackLayout):

    def __init__(self, **kwargs):
        super(ComplexProgressBar, self).__init__(**kwargs)
        self.__label = None
        self.__pb = None

    def _find_child(self, type_: Type[T]) -> T:
        for child in self.children:
            if isinstance(child, type_):
                return child
        else:
            raise AttributeError(f(_("The {self.__class__} has no {type_} child!")))

    @property
    def label(self) -> Label:
        if self.__label is None:
            self.__label = self._find_child(Label)
        return self.__label

    @property
    def pb(self) -> ProgressBar:
        if self.__pb is None:
            self.__pb = self._find_child(ProgressBar)
        return self.__pb

    @property
    def max(self):
        return self.pb.max

    @max.setter
    @mainthread
    def max(self, value):
        self.pb.max = value

    @property
    def value(self):
        return self.pb.value

    @value.setter
    @mainthread
    def value(self, value):
        self.pb.value = value

    @property
    def value_normalized(self):
        return self.pb.value_normalized

    @value_normalized.setter
    @mainthread
    def value_normalized(self, value_normalized):
        self.pb.value_normalized = value_normalized

    @property
    def text(self):
        return self.label.text

    @mainthread
    def reset(self):
        self.pb.value = 0
        self.max = 100
        self.text = "{internal_name}"

    @text.setter
    @mainthread
    def text(self, text: Union[str, Callable]):
        values = {
            'max_': self.pb.max,
            'value': self.pb.value,
            'internal_name': self.label.internal_name,
        }
        if not isinstance(text, Callable):
            text = text.format
        else:
            kw = inspect.getfullargspec(text).kwonlyargs
            values = {k: v for k, v in values.items() if k in kw}
        self.label.text = text(**values)

    @mainthread
    def add(self, value: int, text: Union[str, Callable] = None):
        self.pb.value += value
        if text is not None:
            self.text = text
