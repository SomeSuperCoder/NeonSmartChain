import random
import threading
import time

import requests
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
import os
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
import pyperclip
from kivymd.uix.button import MDFlatButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard

import data_encrypt
import net_utils
import utils

Window.size = (480, 800)
node = "127.0.0.1"
app_exit = False
allowed_words = open("cli_wallet_stuff/words.txt", "r").read().strip().split("\n")
address = None
seed_phrase = None
private_key = None
public_key = None


def is_seed_phrase(text: str):
    words = text.strip().split(" ")

    if len(words) != 12:
        return False

    for word in words:
        if word not in allowed_words:
            return False

    return True


def generate_random_seed():
    result = ""
    random.choice(allowed_words)
    for i in range(12):
        result = result + f"{random.choice(allowed_words)} "

    return result.strip()


class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''
class Content(MDBoxLayout):
    pass

class Wallet(MDApp):
    # def open_file(self):
    #     self.screen('file_pem')
    #     selected_file = self.root.ids.file_chooser.selection and self.root.ids.file_chooser.selection[0]
    #     if selected_file:
    #         with open(selected_file, 'r') as file:
    #             file_contents = file.read()
    #             print(file_contents)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True
        )
        self.file_manager.ext = [".txt"]
        self.dialog_send = None
        self.dialog_staking = None
        # self.bind(on_request_close=self.on_stop()))

    def pad(self, s):
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

    def undo_pad(self, s):
        return s[:-ord(s[len(s) - 1:])]

    def screen(self, screen_name):
        self.root.current = screen_name

    def file_manager_open(self, file):
        self.manager_open = True
        self.file_manager.show(os.path.expanduser("D:/"))

    def login_using_password(self):
        self.screen('main_screen')
        # self.screen('main_screen')
        # text = self.root.ids.seed_text.text
        # password = self.root.ids.password_login.text
        # encrypted_text = self.encrypt_text(password, text)
        # with open("file.txt", "w") as myfile:
        #     myfile.write(f"{encrypted_text}")
        # with open("file.dat", "w") as myfile:
        #     a = self.root.ids.password_login.text
        #     hashed_string = hashlib.sha256(a.encode('utf-8')).hexdigest()
        #     myfile.write(f"{hashed_string}")
        #     myfile.close()

    def show_confirmation_dialog(self):
        self.dialog_send = MDDialog(
            title="Address:",
            type="custom",
            content_cls=Content(),
            buttons=[
                MDFlatButton(
                    text="Отмена",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog_close(self.dialog_send),
                ),
                MDFlatButton(
                    text="Отправить",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.send(self.dialog_send),
                ),
            ],
        )
        self.dialog_send.open()

    def staking_dialog(self):
        try:
            stake_amount_123 = net_utils.get_data_from_path(f"/utils/stake_info?address={address}", node)
            print(f"Stake amount: {stake_amount_123}")
        except requests.exceptions.ConnectionError as e:
            stake_amount_123 = 0
            print(f"{e.__class__.__name__}: {e}")
            print("[bold red]Network connection error")

        self.dialog_staking = MDDialog(
            title=f"{stake_amount_123} NEON",
            type="custom",
            buttons=[
                MDFlatButton(
                    text="Ок",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.dialog_close(self.dialog_staking),
                )
            ]
        )
        self.dialog_staking.open()

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        self.root.ids.download_pem.text = f"{path}"

        toast(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.material_style = "M3"
        # self.root.current = 'second_login'
        sm = Builder.load_file("kivy.kv")
        if os.path.isfile("cli_wallet_stuff/account.bin"):
            sm.current = "login_account_enter_password"
        return sm

    def copy_button_text(self):
        pyperclip.copy(self.root.ids.user_address.text)

    def dialog_close(self, target):
        target.dismiss()

    # def on_stop(self):
    #     global app_exit
    #     app_exit = True

    # login stuff
    def login(self):
        global seed_phrase
        password = self.root.ids.login_password_input.text
        try:
            seed_phrase = data_encrypt.decrypt_text(open("cli_wallet_stuff/account.bin", "r+b").read(), password)
            if not is_seed_phrase(seed_phrase):
                raise Exception
            do_login_by_seed_phrase()
            self.refresh_balance()
            self.screen("main_screen")
        except:
            print("[bold red]Wrong password!")
            MDDialog(title='Неверный пароль', size_hint=(None, None), size=(400, 400)).open()

    def create_account(self):
        global seed_phrase
        seed_phrase = generate_random_seed()
        self.screen('create_account_enter_password')

    def final_create_account(self):
        global seed_phrase

        password = self.root.ids.password_login.text
        # seed_phrase = generate_random_seed()
        enc_data = data_encrypt.encrypt_text(text=seed_phrase, password=password)
        open("cli_wallet_stuff/account.bin", "w+b").write(enc_data)
        do_login_by_seed_phrase()
        self.refresh_balance()
        self.screen("main_screen")

    def login_by_seed_phrase(self):
        global seed_phrase
        seed = self.root.ids.seed_text.text

        if is_seed_phrase(seed):
            seed_phrase = seed
            # do_login_by_seed_phrase()
            self.screen("create_account_enter_password")
        else:
            MDDialog(title='Неправильная сид фраза', size_hint=(None, None), size=(400, 400)).open()

    def logout(self):
        os.remove("cli_wallet_stuff/account.bin")
        self.screen("first_login")

    def refresh_balance(self):
        try:
            balance = net_utils.get_data_from_path(f"/utils/balance_of?address={address}", node)
            print(f"Balance: {balance}")
        except requests.exceptions.ConnectionError as e:
            balance = 0
            print(f"{e.__class__.__name__}: {e}")
            print("[bold red]Network connection error")
        try:
            self.root.ids.balance_user.text = f"{balance} NEON"
        except NameError:
            pass
        except AttributeError:
            pass

    def show_seed_phrase(self):
        global seed_phrase

        MDDialog(title="Сид фраза",
                 type="custom",
                 content_cls=MDTextField(text=f"{seed_phrase}", multiline=True)
                 ).open()

    def send(self, button):
        global private_key
        content = self.dialog_send
        amount = float(content.content_cls.ids.amount.text)
        to = content.content_cls.ids.to.text
        message = content.content_cls.ids.message.text
        print(f"{to} {amount} {message}")
        try:
            index = int(net_utils.get_data_from_path(f"/utils/get_latest_tx_id_for_address?address={address}", node))
        except requests.exceptions.ConnectionError as e:
            print(f"{e.__class__.__name__}: {e}")
            print("[bold red]Network connection error")
            return
        send_tx = utils.send(
            id=index + 1,
            private_key=private_key,
            to=to,
            amount=amount,
            message=message
        )
        try:
            net_utils.broadcast_json_to_url(send_tx.serialize(), url="/new_transaction", node_list=[node])
        except requests.exceptions.ConnectionError as e:
            print(f"{e.__class__.__name__}: {e}")
            print("[bold red]Network connection error")
            return

def do_login_by_seed_phrase():
    global private_key
    global public_key
    global address

    private_key = utils.private_key_from_seed_phrase(seed_phrase)
    public_key = private_key.get_verifying_key()
    address = utils.generate_address(public_key)
    wallet.root.ids.user_address.text = address


wallet = Wallet()
wallet.run()

