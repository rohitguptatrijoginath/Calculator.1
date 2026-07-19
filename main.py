from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp

class CalculatorApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#000000')
        
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(10), dp(20), dp(30)], spacing=dp(10))
        
        display_box = BoxLayout(orientation='vertical', size_hint_y=0.45, spacing=dp(5))
        
        self.history = Label(
            text="",
            font_size='18sp',
            color=get_color_from_hex('#555555'),
            halign='right',
            valign='bottom'
        )
        self.history.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        self.display = Label(
            text="0",
            font_size='50sp',
            color=get_color_from_hex('#FFFFFF'),
            halign='right',
            valign='bottom'
        )
        self.display.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        display_box.add_widget(self.history)
        display_box.add_widget(self.display)
        main_layout.add_widget(display_box)
        
        buttons_grid = GridLayout(cols=4, spacing=dp(20), size_hint_y=0.55)
        
        # '⌫' की जगह '[x]' का इस्तेमाल किया है जो हर फोन में सही दिखेगा
        # फोटो की तरह गुणा के लिए '×' और भाग के लिए '÷' कर दिया है
        buttons = [
            'C', '[x]', '%', '÷',
            '7', '8', '9', '×',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '.', '00', '='
        ]
        
        for text in buttons:
            if text in ['C', '[x]', '%']:
                text_color = '#A5A5A5'
            elif text in ['÷', '×', '-', '+', '=']:
                text_color = '#9C27B0' # पर्पल थीम
            else:
                text_color = '#FFFFFF'
            
            btn = Button(
                text=text,
                font_size='26sp',
                bold=True,
                background_normal='',
                background_color=get_color_from_hex('#000000'),
                color=get_color_from_hex(text_color)
            )
            btn.bind(on_press=self.on_button_press)
            buttons_grid.add_widget(btn)
            
        main_layout.add_widget(buttons_grid)
        return main_layout

    def on_button_press(self, instance):
        current_text = self.display.text
        button_text = instance.text
        
        if button_text == 'C':
            self.display.text = '0'
            self.history.text = ""
        elif button_text == '[x]': # यहाँ '[x]' बैकस्पेस का काम करेगा
            if len(current_text) > 1:
                self.display.text = current_text[:-1]
            else:
                self.display.text = '0'
        elif button_text == '=':
            try:
                if current_text:
                    if self.history.text:
                        self.history.text += f"\n= {current_text}"
                    else:
                        self.history.text = current_text
                    
                    # eval के लिए '÷' को '/' और '×' को '*' में बदलना जरूरी है
                    calc_text = current_text.replace('÷', '/').replace('×', '*')
                    result = eval(calc_text)
                    self.display.text = str(result)
            except Exception:
                self.display.text = 'Error'
        else:
            if current_text == '0' or current_text == 'Error':
                self.display.text = button_text
            else:
                self.display.text = current_text + button_text

if __name__ == '__main__':
    CalculatorApp().run()
