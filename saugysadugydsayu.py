from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

# Define your screens in KV language
kv = '''
ScreenManager:
    MainScreen:
    AnotherScreen:

<MainScreen>:
    name: 'main'
    MDLabel:
        text: 'This is the main screen'
        halign: 'center'
    MDRectangleFlatButton:
        text: 'Go to another screen'
        pos_hint: {'center_x':0.5,'center_y':0.4}
        on_release: app.root.current = 'another'

<AnotherScreen>:
    name: 'another'
    MDLabel:
        text: 'This is another screen'
        halign: 'center'
    MDRectangleFlatButton:
        text: 'Go back to main screen'
        pos_hint: {'center_x':0.5,'center_y':0.4}
        on_release: app.root.current = 'main'
'''

class MainScreen(Screen):
    pass

class AnotherScreen(Screen):
    pass

class MyApp(MDApp):
    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(MainScreen(name="main"))
        screen_manager.add_widget(AnotherScreen(name="another"))
        return Builder.load_string(kv)

if __name__ == '__main__':
    MyApp().run()
