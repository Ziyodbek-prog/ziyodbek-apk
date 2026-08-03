import sys
import os
import random
import string
import hashlib
import base64
import json
import threading
from urllib.request import Request, urlopen

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.core.window import Window
from kivy.clock import Clock

Window.clearcolor = (0.07, 0.08, 0.11, 1)

class MainApp(App):
    def build(self):
        self.title = "Ziyodbek SMM Pro Suite"
        tp = TabbedPanel(do_default_tab=False, tab_width=110, tab_height=45)

        # Tab 1: SMM Calc
        tab_smm = TabbedPanelHeader(text='📊 SMM Calc')
        smm_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        smm_layout.add_widget(Label(text="SMM Foyda Kalkulyatori", font_size='18sp', bold=True))
        
        self.input_cost = TextInput(hint_text="1000 ta xizmat tannarxi", input_filter='int', multiline=False)
        self.input_sell = TextInput(hint_text="1000 ta xizmat sotish narxi", input_filter='int', multiline=False)
        self.input_qty = TextInput(hint_text="Buyurtma miqdori", input_filter='int', multiline=False)
        
        smm_layout.add_widget(self.input_cost)
        smm_layout.add_widget(self.input_sell)
        smm_layout.add_widget(self.input_qty)

        btn_calc = Button(text="Hisoblash 💰", background_color=(0.1, 0.8, 0.4, 1))
        btn_calc.bind(on_press=self.calculate_smm)
        smm_layout.add_widget(btn_calc)

        self.lbl_smm_result = Label(text="Natija shu yerda chiqadi...")
        smm_layout.add_widget(self.lbl_smm_result)
        tab_smm.content = smm_layout
        tp.add_widget(tab_smm)

        return tp

    def calculate_smm(self, instance):
        try:
            cost = float(self.input_cost.text or 0)
            sell = float(self.input_sell.text or 0)
            qty = float(self.input_qty.text or 0)
            profit = ((sell - cost) / 1000.0) * qty
            self.lbl_smm_result.text = f"Sof Foyda: {profit:,.2f} so'm"
        except Exception:
            self.lbl_smm_result.text = "Xatolik yuz berdi!"

if __name__ == '__main__':
    MainApp().run()
  
