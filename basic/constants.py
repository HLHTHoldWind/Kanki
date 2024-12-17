import ctypes
import locale
import os
import configparser
import json
WORK_PATH = os.getcwd()
USER_PATH = os.path.expanduser('~')
CONFIG = configparser.ConfigParser()


class Color:

    def __init__(self, color, name, code):
        self.color = color
        self.name = name
        self.color_code = code


class COLORS:
    PINK = Color('[95m', "INFO", "#e4007f")
    BLUE = Color('[94m', "INFO", "#00a0e9")
    CYAN = Color('[96m', "INFO", "#00f0e8")
    GREEN = INFO = SUCCESS = Color('[92m', "INFO", "#4add43")
    YELLOW = WARNING = Color('[93m', "WARNING", "#ffff00")
    RED = ERROR = Color('[91m', "ERROR", "#ff0000")
    LIGHT_GRAY = Color('[37m', "COMMAND", "#c8c3bc")
    NONE = Color('[0m', "INFO", "#ffffff")
    BOLD = Color('[1m', "INFO", "#fffffe")
    UNDERLINE = Color('[4m', "INFO", "#fffffd")
    LIGHT_BLUE = Color('[4m', "INFO", "#a0c3fb")
    LIGHT_GREEN = Color('[4m', "INFO", "#41ff41")
    LIGHT_YELLOW = Color('[4m', "INFO", "#ffdf94")
    colors = [PINK, BLUE, CYAN, GREEN, YELLOW, RED, LIGHT_GRAY,
              NONE, BOLD, UNDERLINE, LIGHT_BLUE, LIGHT_GREEN, LIGHT_YELLOW]


if os.name == 'nt':
    kernel32 = ctypes.windll.kernel32
    kernel32.GetUserDefaultUILanguage()
    default_lang = locale.windows_locale[kernel32.GetUserDefaultUILanguage()]

else:
    default_lang = locale.getdefaultlocale()[0]

language_lib = []

for file in os.listdir(f"{WORK_PATH}\\languages"):
    if file.endswith(".json"):
        language_lib.append(os.path.basename(file).replace(".json", "").lower())

if default_lang.lower() not in language_lib:
    default_lang = "en_us"

LANG_DICT = {}

for lang_file in os.listdir(f"{WORK_PATH}\\languages"):
    if lang_file.endswith(".json"):
        with open(f"{WORK_PATH}\\languages\\{lang_file}", 'rb') as file:
            # print(file.read())
            content = json.load(file)
            lang_code = lang_file.lower().replace(".json", "")
            LANG_DICT[content["language_name"]] = f"{lang_code}"

TEMP_PATH = f"{USER_PATH}\\AppData\\Local\\Temp"
LOCAL_PATH = f"{USER_PATH}\\AppData\\Local\\HLHT\\KANKI"
DEFAULT_URL = "translate.google.com"

LANGUAGE_CODES = {"english": "en", "japanese": "ja", "chinese": "zh-cn",
                  "schinese": "zh-cn", "tchinese": "zh-tw", "latin": "la",
                  "italian": "it", "french": "fr", "korean": "ko", "esperanto": "eo",
                  "russian": "ru", "turkish": "tr"}


def init_config():
    if not os.path.exists(TEMP_PATH):
        os.makedirs(TEMP_PATH, exist_ok=True)
    if not os.path.exists(LOCAL_PATH):
        os.makedirs(LOCAL_PATH, exist_ok=True)
    with open(f"{LOCAL_PATH}\\config.ini", "w") as configfile:
        CONFIG["CONFIG"] = {
            "lang": default_lang,
            "flip": "false",
            "fps": "120"
        }
        CONFIG.write(configfile)
    CONFIG.read(f"{LOCAL_PATH}\\config.ini")


def test_config():
    try:
        CONFIG.read(f"{LOCAL_PATH}\\config.ini")
        awa = CONFIG["CONFIG"]["lang"]
        # awa = CONFIG["CONFIG"]["theme"]
    except KeyError:
        init_config()


test_config()
