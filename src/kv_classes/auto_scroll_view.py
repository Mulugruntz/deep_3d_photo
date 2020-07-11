from kivy.clock import mainthread
from kivy.uix.scrollview import ScrollView


class AutoScrollView(ScrollView):
    @mainthread
    def append_message(self, text):
        self.children[0].text += text
        self.scroll_y = 0
