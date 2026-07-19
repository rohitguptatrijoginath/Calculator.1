from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

import ast
import operator
import math


# ✅ SAFE OPERATORS
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}


def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](_eval(node.operand))
        else:
            raise Exception("Invalid")

    node = ast.parse(expr, mode='eval').body
    return _eval(node)


class RoundedButton(Button):
    def __init__(self, bg_color="#1C1C1C", **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = get_color_from_hex(bg_color)

        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(radius=[dp(30)])

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.animate_press)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def animate_press(self, *args):
        anim = Animation(scale=0.95, duration=0.05) + Animation(scale=1, duration=0.05)
        anim.start(self)


class CalculatorApp(App):

    memory = 0
    dark_mode = True

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        self.sound = SoundLoader.load(None)

        self.main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        self.history_label = Label(
            text="",
            size_hint_y=None,
            halign="right",
            valign="top",
            color=(0.7, 0.7, 0.7, 1)
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))

        scroll = ScrollView(size_hint=(1, 0.25))
        scroll.add_widget(self.history_label)

        self.display = Label(
            text="0",
            font_size='45sp',
            halign='right',
            valign='middle',
            size_hint=(1, 0.2),
            color=(1, 1, 1, 1)
        )
        self.display.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.display.bind(on_touch_down=self.check_double_tap)

        self.main.add_widget(scroll)
        self.main.add_widget(self.display)

        self.grid = GridLayout(cols=4, spacing=dp(10))
        self.main.add_widget(self.grid)

        self.load_buttons()

        return self.main

    def load_buttons(self):

        buttons = [
            'MC', 'MR', 'M+', 'M-',
            'C', '±', '%', '÷',
            '7', '8', '9', '×',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '.', '√', '=',
            'x²', '^', '[x]', '00'
        ]

        for text in buttons:

            if text in ['÷', '×', '-', '+', '=', '^']:
                color = '#9C27B0'
            elif text in ['C', '±', '√', 'x²', '[x]', '%']:
                color = '#424242'
            elif text in ['MC', 'MR', 'M+', 'M-']:
                color = '#00695C'
            else:
                color = '#1C1C1C'

            btn = RoundedButton(
                text=text,
                bg_color=color,
                font_size='22sp',
                color=(1, 1, 1, 1)
            )

            if text == "C":
                btn.bind(on_release=self.clear_short)
                btn.bind(on_press=self.start_long_clear)

            else:
                btn.bind(on_press=self.on_press)

            self.grid.add_widget(btn)

    # ✅ Double tap theme
    def check_double_tap(self, instance, touch):
        if touch.is_double_tap:
            self.dark_mode = not self.dark_mode
            Window.clearcolor = (1,1,1,1) if not self.dark_mode else (0,0,0,1)
            self.display.color = (0,0,0,1) if not self.dark_mode else (1,1,1,1)

    # ✅ Long press clear
    def start_long_clear(self, instance):
        self.long_press = Clock.schedule_once(self.clear_history, 1)

    def clear_short(self, instance):
        if hasattr(self, 'long_press'):
            self.long_press.cancel()
        self.display.text = "0"

    def clear_history(self, dt):
        self.history_label.text = ""

    def adjust_font(self):
        length = len(self.display.text)
        if length > 15:
            self.display.font_size = '25sp'
        elif length > 10:
            self.display.font_size = '35sp'
        else:
            self.display.font_size = '45sp'

    def on_press(self, instance):
        text = instance.text
        current = self.display.text

        if text == "[x]":
            self.display.text = current[:-1] if len(current) > 1 else "0"

        elif text == "±":
            self.display.text = current[1:] if current.startswith("-") else "-" + current

        elif text == "√":
            try:
                self.display.text = str(round(math.sqrt(float(current)), 10))
            except:
                self.display.text = "Error"

        elif text == "x²":
            try:
                self.display.text = str(round(float(current) ** 2, 10))
            except:
                self.display.text = "Error"

        elif text == "=":
            try:
                expr = current.replace('×', '*').replace('÷', '/').replace('^', '**')
                result = safe_eval(expr)
                self.history_label.text += current + " = " + str(result) + "\n"
                self.display.text = str(round(result, 10))
            except:
                self.display.text = "Error"

        elif text in ['MC', 'MR', 'M+', 'M-']:
            try:
                value = float(self.display.text)
            except:
                value = 0

            if text == "MC":
                self.memory = 0
            elif text == "MR":
                self.display.text = str(self.memory)
            elif text == "M+":
                self.memory += value
            elif text == "M-":
                self.memory -= value

        elif text in ['+', '-', '×', '÷', '^', '%']:
            if current[-1] in ['+', '-', '×', '÷', '^', '%']:
                self.display.text = current[:-1] + text
            else:
                self.display.text += text

        else:
            if current == "0":
                self.display.text = text
            else:
                self.display.text += text

        self.adjust_font()


if __name__ == "__main__":
    CalculatorApp().run()
