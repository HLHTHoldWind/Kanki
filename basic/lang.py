import json
import os
import locale
import ctypes
from basic.constants import *
import configparser

config = configparser.ConfigParser()

if os.name == 'nt':
    kernel32 = ctypes.windll.kernel32
    kernel32.GetUserDefaultUILanguage()
    default_lang = locale.windows_locale[kernel32.GetUserDefaultUILanguage()]

else:
    default_lang = locale.getdefaultlocale()[0]


if not os.path.exists(f"{LOCAL_PATH}\\config.ini"):
    with open(f"{LOCAL_PATH}\\config.ini", "w") as configfile:
        config["CONFIG"] = {"lang": default_lang}
        config.write(configfile)

with open("languages\\en_us.json", "rb") as file:
    LANG = json.load(file)


def load_lang():
    global LANG
    while True:
        try:

            config.read(f"{LOCAL_PATH}\\config.ini")

            if os.path.exists("languages\\" + config["CONFIG"]["lang"].lower() + ".json"):
                with open("languages\\" + config["CONFIG"]["lang"].lower() + ".json", "rb") as file:
                    LANG = json.load(file)
            else:
                with open("languages\\en_us.json", "rb") as file:
                    LANG = json.load(file)
            print(LANG["language_name"])
            print(LANG_DICT)
            break

        except KeyError:
            init_config()
            continue


load_lang()
