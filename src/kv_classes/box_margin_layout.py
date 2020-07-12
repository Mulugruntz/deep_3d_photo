from typing import List, Tuple

from kivy.uix.boxlayout import BoxLayout


class BoxMarginLayout(BoxLayout):
    def do_layout(self, *args):
        super().do_layout(*args)
        self.apply_margins()
        self._trigger_layout.cancel()

    def apply_margins(self):
        for child in self.children:
            if hasattr(child, "margin"):
                m = child.margin
                if not isinstance(m, (List, Tuple)) or len(m) == 1:
                    left, top, right, bottom = m, m, m, m
                elif len(m) == 2:
                    (left, right), (top, bottom) = m, m
                elif len(m) == 4:
                    left, top, right, bottom = m
                else:
                    continue
                child.x += left
                child.y += bottom
                child.width -= left + right
                child.height -= top + bottom
