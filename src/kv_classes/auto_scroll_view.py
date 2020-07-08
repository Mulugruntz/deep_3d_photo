from kivy.clock import mainthread
from kivy.uix.scrollview import ScrollView


class AutoScrollView(ScrollView):
    @mainthread
    def append_message(self, text):
        is_at_bottom = self.scroll_y == 0
        self.children[0].text += text
        if is_at_bottom:
            self.scroll_y = 0