import multiprocessing
import platform
import time
from kivymd.tools.hotreload.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Line
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivymd.theming import ThemeManager
from threading import Thread
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color


class App(MDApp):
    def __init__(self, **kwargs):
        self.colors = {
            "green": "./GUI/CO/green.jpeg",
            "blue": "./GUI/CO/blue.jpeg",
            "red": "./GUI/CO/red.jpeg",
            "yellow": "./GUI/CO/yellow.jpeg",
            "grey": "./GUI/CO/grey.jpeg",
        }

        self.images = {
            "admiration": "./GUI/BA/Admiration.png",
            "amusement": "./GUI/BA/Happy.png",
            "anger": "./GUI/BA/Anger.png",
            "annoyance": "./GUI/BA/annoyance.png",
            "approval": "./GUI/BA/Approval.png",
            "caring": "./GUI/BA/caring.png",
            "confusion": "./GUI/BA/Confusion.png",
            "curiosity": "./GUI/BA/Confusion.png",
            "desire": "./GUI/BA/Admiration.png",
            "disappointment": "./GUI/BA/Dissapointment.png",
            "disapproval": "./GUI/BA/Dissapointment.png",
            "disgust": "./GUI/BA/Scared.png",
            "embarrassment": "./GUI/BA/Embaresed.png",
            "excitement": "./GUI/BA/Exitment.png",
            "fear": "./GUI/BA/Scared.png",
            "gratitude": "./GUI/BA/7o.png",
            "grief": "./GUI/BA/Sad.png",
            "joy": "./GUI/BA/Happy.png",
            "love": "./GUI/BA/caring.png",
            "nervousness": "./GUI/BA/Scared.png",
            "optimism": "./GUI/BA/Happy.png",
            "pride": "./GUI/BA/7o.png",
            "realization": "./GUI/BA/Exitment.png",
            "relief": "./GUI/BA/Normal.png",
            "remorse": "./GUI/BA/Dissapointment.png",
            "sadness": "./GUI/BA/Sad.png",
            "surprise": "./GUI/BA/Exitment.png/",
            "neutral": "./GUI/BA/Normal.png",
        }

        if platform.system() == "Linux":
            Window.borderless = True

        Clock.schedule_interval(self.change_face, 0.1)

        super().__init__(**kwargs)

    def change_face(self, *args):
        if self.queue.empty():
            return
        else:
            emotion = self.queue.get()
            print(emotion)
            if emotion[0] == "E":
                emotion = emotion[1:]
                page = self.images[emotion]
                self.eyes.source = page
            elif emotion[0] == "C":
                color = emotion[1:]
                page = self.colors[color]
                self.line.source = page

    def run(self, queue: multiprocessing.Queue):
        self.queue = queue
        super().run()

    def build_app(self, first=False):
        self.theme_cls = ThemeManager()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.index = 0

        layout = ScreenManager()
        screen = Screen()
        self.line = Image(
            source=self.colors["yellow"],
            size_hint=(0.9, 1),
            pos_hint={"center-x": 0, "center_y": 0.98},
            size_hint_y=0.7,
            size_hint_x=1.1,
        )

        self.eyes = Image(
            source=self.images["neutral"],
            size_hint=(0.9, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        screen.add_widget(self.eyes)
        screen.add_widget(self.line)

        layout.add_widget(screen)

        return layout
