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

import ast
import operator
import math
import speech_recognition as sr
import matplotlib.pyplot as plt
import numpy as np

try:
    from jnius import autoclass
    ANDROID = True
except:
    ANDROID = False


# ✅ SAFE OPERATORS
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
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
            raise Exception("Invalid Expression")

    node = ast.parse(expr, mode='eval').body
    return _eval(node)


# ✅ Rounded Animated Button
class RoundedButton(Button):
    def __init__(self, bg_color="#1C1C1C", **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self.rect = RoundedRectangle(radius=[dp(30)])

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.animate_press)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def animate_press(self, *args):
        anim = Animation(size=(self.width*0.95, self.height*0.95), duration=0.05) + \
               Animation(size=(self.width, self.height), duration=0.05)
        anim.start(self)


class CalculatorApp(App):

    memory = 0
    dark_mode = True

    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        self.main = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # ✅ History Scroll
        self.history_label = Label(
            text="",
            size_hint_y=None,
            halign="right",
            valign="top",
            color=(0.7, 0.7, 0.7, 1)
        )
        self.history_label.bind(texture_size=self.history_label.setter('size'))

        scroll = ScrollView(size_hint=(1, 0.3))
        scroll.add_widget(self.history_label)

        self.display = Label(
            text="0",
            font_size='40sp',
            halign='right',
            valign='middle',
            size_hint=(1, 0.2),
            color=(1, 1, 1, 1)
        )
        self.display.bind(size=lambda i, v: setattr(i, 'text_size', v))

        self.main.add_widget(scroll)
        self.main.add_widget(self.display)

        self.grid = GridLayout(cols=5, spacing=dp(8))
        self.main.add_widget(self.grid)

        self.load_buttons()

        return self.main

    def load_buttons(self):

        buttons = [
            'MC','MR','M+','M-','🔐',
            'C','±','%','√','÷',
            '7','8','9','x²','×',
            '4','5','6','^','-',
            '1','2','3','📈','+',
            '0','.','🎤','[x]','='
        ]

        for text in buttons:

            color = '#1C1C1C'

            if text in ['÷','×','-','+','=','^']:
                color = '#9C27B0'
            elif text in ['C','±','√','x²']:
                color = '#424242'
            elif text in ['MC','MR','M+','M-']:
                color = '#00695C'
            elif text in ['🔐','📈','🎤']:
                color = '#455A64'

            btn = RoundedButton(
                text=text,
                bg_color=color,
                font_size='18sp',
                color=(1,1,1,1)
            )
            btn.bind(on_press=self.on_press)
            self.grid.add_widget(btn)

    # ✅ Voice Input
    def voice_input(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.display.text = "Listening..."
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            text = text.lower()
            text = text.replace("plus","+").replace("minus","-") \
                       .replace("into","*").replace("divide","/")
            self.display.text = text
        except:
            self.display.text = "Voice Error"

    # ✅ Graph Plot
    def plot_graph(self):
        expr = self.display.text.replace('^','**')
        x = np.linspace(-10,10,400)

        try:
            y = eval(expr)
            plt.plot(x,y)
            plt.grid()
            plt.show()
        except:
            self.display.text = "Graph Error"

    # ✅ Fingerprint
    def fingerprint_auth(self):
        if ANDROID:
            self.display.text = "Fingerprint Auth..."
        else:
            self.display.text = "Android Only"

    def on_press(self, instance):
        text = instance.text
        current = self.display.text

        if text == "C":
            self.display.text = "0"

        elif text == "[x]":
            self.display.text = current[:-1] if len(current)>1 else "0"

        elif text == "±":
            self.display.text = current[1:] if current.startswith("-") else "-" + current

        elif text == "√":
            try:
                self.display.text = str(round(math.sqrt(float(current)),10))
            except:
                self.display.text = "Error"

        elif text == "x²":
            try:
                self.display.text = str(round(float(current)**2,10))
            except:
                self.display.text = "Error"

        elif text == "=":
            try:
                expr = current.replace('×','*').replace('÷','/').replace('^','**')
                result = safe_eval(expr)
                self.history_label.text += current + " = " + str(result) + "\n"
                self.display.text = str(round(result,10))
            except:
                self.display.text = "Error"

        elif text == "🎤":
            self.voice_input()

        elif text == "📈":
            self.plot_graph()

        elif text == "🔐":
            self.fingerprint_auth()

        elif text in ['MC','MR','M+','M-']:
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

        elif text in ['+','-','×','÷','^','%']:
            if current[-1] in ['+','-','×','÷','^','%']:
                self.display.text = current[:-1] + text
            else:
                self.display.text += text

        else:
            if current == "0":
                self.display.text = text
            else:
                self.display.text += text


if __name__ == "__main__":
    CalculatorApp().run()