import ctypes
import importlib
import time
from threading import Thread
import os
import asyncio
from PIL import ImageSequence
from ttkbootstrap import *
import tkinter as tk
import basic.widget as widget
import basic.kanki as kanki
import pystray
import basic.lang as lang
from basic.constants import *

lang2 = lang

winapi = ctypes.windll.user32
trueWidth = winapi.GetSystemMetrics(0)

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ZOOM = round((winapi.GetSystemMetrics(0) / trueWidth) + (0.1 * ((winapi.GetSystemMetrics(0) / trueWidth) / 2)), 1)

IMG_CACHE = []
IMG_CACHE2 = []
IMG_CACHE3 = []
GLOBAL_IMG_CACHE = {}
IN_CONFIG = False
FPS = 120


class MainWindow(Window):
    def __init__(self, flipping=False, fps=120):
        global FPS
        Window.__init__(self, themename="darkly2")
        self.withdraw()
        self.length = 0
        self.length2 = 0
        self.stop_scrolling = False
        self.restart = False
        self.paused = False
        self.toolbar = False
        self.stop_gyrate = False
        self.flipping_text = flipping
        FPS = fps

        with open("basic\\paused.txt", "rb") as f:
            if f.read().decode("utf-8") == "paused":
                self.paused = True
            else:
                self.paused = False

        self.protocol("WM_DELETE_WINDOW", self.delete)
        windowInit(self, 300, 300, False, "Kanki", "assets\\music_icon.ico")
        self.icon = Image.open("assets\\music_icon.png").resize((zoom(100), zoom(100)))
        self.overrideredirect(True)
        self.attributes("-toolwindow", True)
        self.small = SmallIcon(self, name="Main", icon=Image.open("assets\\music_icon.ico"), title="Kanki")
        self.small.run_detached()

        self.load_l = Label(self)
        widget.label_print(self.load_l, "ikura（いくら）")

        icon = ImageTk.PhotoImage(self.icon.resize((zoom(75), zoom(75))))
        IMG_CACHE.append(icon)

        self.configure(background="#1b1b1b")

        x = self.winfo_screenwidth() - self.winfo_width()
        y = self.winfo_screenheight() - self.winfo_height() + zoom(100) - zoom(40)

        self.geometry(f"+{x}+{y}")

        self.Style = Style()
        self.Style.configure("TFrame", background="#1b1b1b")

        self.load_animation()

        self.main_widget = Frame(self)

        # self.icon_label = Canvas(self.main_widget, background="#1b1b1b", borderwidth=0, highlightthickness=0)
        self.icon_label = Label(self.main_widget, background="#1b1b1b", borderwidth=0, cursor="hand2")
        self.icon_label.place(x=zoom(0), y=zoom(112), width=zoom(75), height=zoom(75))

        self.artist_frame = Frame(self.main_widget)
        self.artist_label = Label(self.artist_frame, background="#1b1b1b", foreground="#ffffff", borderwidth=0,
                                  font=("Microsoft Yahei UI", 15), text="Monster Siren Records")
        self.artist_label.place(x=zoom(0), y=zoom(0), width=zoom(225), height=zoom(37))
        self.artist_label2 = Label(self.artist_frame, background="#1b1b1b", foreground="#ffffff", borderwidth=0,
                                   font=("Microsoft Yahei UI", 15), text="Monster Siren Records")
        self.artist_label2.place(x=zoom(325), y=zoom(0), width=zoom(225), height=zoom(37))

        self.title_frame = Frame(self.main_widget)
        self.title_label = Label(self.title_frame, background="#1b1b1b", foreground="#ffffff", borderwidth=0,
                                 font=("Microsoft Yahei UI", 20, "bold"), text="Scordatura")
        self.title_label.place(x=zoom(0), y=zoom(0), width=zoom(200), height=zoom(37))

        self.title_label2 = Label(self.title_frame, background="#1b1b1b", foreground="#ffffff", borderwidth=0,
                                  font=("Microsoft Yahei UI", 20, "bold"), text="Scordatura")
        self.title_label2.place(x=zoom(325), y=zoom(0), width=zoom(225), height=zoom(37))

        self.toolbar_frame = Frame(self)
        img = IMG_CACHE2[0] if self.paused else IMG_CACHE2[-1]
        self.stop_button = Label(self.toolbar_frame, image=img, cursor="hand2")
        self.prev_button = Label(self.toolbar_frame, image=IMG_CACHE3[0], cursor="hand2")
        self.next_button = Label(self.toolbar_frame, image=IMG_CACHE3[1], cursor="hand2")

        self.stop_button.place(x=zoom(55), y=zoom(5), width=zoom(40), height=zoom(40))
        self.prev_button.place(x=zoom(10), y=zoom(10), width=zoom(30), height=zoom(30))
        self.next_button.place(x=zoom(110), y=zoom(10), width=zoom(30), height=zoom(30))

        self.attributes("-transparentcolor", "#1b1b1b")

        self.artist_frame.place(x=zoom(80), y=zoom(150), width=zoom(225), height=zoom(37))
        self.title_frame.place(x=zoom(80), y=zoom(117), width=zoom(225), height=zoom(37))
        self.main_widget.place(x=0, y=zoom(100), width=zoom(75), height=self.winfo_height())
        self.toolbar_frame.place(x=zoom(75), y=zoom(100), width=zoom(150), height=zoom(0))

        self.icon_label.bind("<ButtonRelease-1>", self.toggle_toolbar)
        self.stop_button.bind("<ButtonRelease-1>", self.toggle_pausing)
        self.prev_button.bind("<ButtonRelease-1>", self.skip_previous)
        self.next_button.bind("<ButtonRelease-1>", self.skip_next)
        self.icon_label.bind("<ButtonRelease-3>", self.toggle_pausing)

        self.deiconify()
        self.config_win = ConfigurateWindow(master=self)
        Thread(target=self.topMost).start()
        Thread(target=self.gyrating).start()
        Thread(target=self.scrolling_t).start()
        Thread(target=self.scrolling_a).start()
        Thread(target=self.check_pause).start()

    def delete(self, event=None):
        self.toolbar = False
        widget.move_to(self.toolbar_frame, x=zoom(75), y=zoom(100), width=zoom(150), height=zoom(0),
                       fps=FPS, delay=0.25)
        x = 0
        y = 0
        width = self.winfo_width()
        height = self.winfo_height()
        widget.move_to(self.main_widget, fps=FPS, x=x, y=y, width=zoom(75), height=height)
        time.sleep(0.5)
        widget.withdraw(self, fps=FPS, is_windows=True, direction="e")
        time.sleep(0.5)
        self.quit()
        os._exit(114514)
        self.destroy()

    def load_animation(self):
        global IMG_CACHE, IMG_CACHE2, IMG_CACHE3
        IMG_CACHE = []
        for i in range(600):
            name = f"gyrating_{i}"
            if not os.path.exists(f"assets\\gyrating\\{name}"):
                img = self.icon.rotate(i * 0.6 * -1, resample=Image.BILINEAR)
                img.save(f"assets\\gyrating\\{name}", "PNG")
            IMG_CACHE.append(ImageTk.PhotoImage(Image.open(f"assets\\gyrating\\{name}").resize((zoom(75), zoom(75)))))

        IMG_CACHE2 = []
        im = Image.open("assets\\pausing.gif")
        _iter = ImageSequence.Iterator(im)
        for i in _iter:
            img = ImageTk.PhotoImage(i.resize((zoom(40), zoom(40))))
            IMG_CACHE2.append(img)

        IMG_CACHE3.append(ImageTk.PhotoImage(Image.open("assets\\previous.png").resize((zoom(30), zoom(30)))))
        IMG_CACHE3.append(ImageTk.PhotoImage(Image.open("assets\\next.png").resize((zoom(30), zoom(30)))))

    def toggle_toolbar(self, event=None):
        if self.toolbar:
            self.toolbar = False
            widget.move_to(self.toolbar_frame, x=zoom(75), y=zoom(100), width=zoom(150), height=zoom(0),
                           fps=FPS, delay=0.25)
        else:
            self.toolbar = True
            widget.move_to(self.toolbar_frame, x=zoom(75), y=zoom(75), width=zoom(150), height=zoom(40),
                           fps=FPS, delay=0.25)

    def update_infos(self, title, artist):
        x = 0
        y = 0
        width = self.winfo_width()
        height = self.winfo_height()
        self.restart = True
        widget.move_to(self.main_widget, fps=FPS, x=x, y=y, width=zoom(75), height=height)
        self.stop_scrolling = True

        time.sleep(0.75)
        self.length = length = tk.font.Font(family="Microsoft Yahei UI", size=20, weight="bold").measure(title)
        self.length2 = length2 = tk.font.Font(family="Microsoft Yahei UI", size=15).measure(artist)
        self.title_label.configure(text=title)
        self.title_label2.configure(text=title)
        self.title_label.place(x=zoom(0), y=zoom(0), width=length, height=zoom(37))
        self.title_label2.place(x=zoom(100) + length, y=zoom(0), width=length, height=zoom(37))
        if self.length < zoom(225):
            self.title_label2.place_forget()
        self.artist_label.configure(text=artist)
        self.artist_label2.configure(text=artist)
        self.artist_label.place(x=zoom(0), y=zoom(0), width=length2, height=zoom(37))
        self.artist_label2.place(x=zoom(100) + length2, y=zoom(0), width=length2, height=zoom(37))
        if self.length2 < zoom(225):
            self.artist_label2.place_forget()
        widget.move_to(self.main_widget, fps=FPS, x=x, y=y, width=width, height=height)
        if self.flipping_text:
            self.title_label.configure(text="")
            self.artist_label.configure(text="")
            delay = 0.75 if len(title) > 20 else 0.25
            fps = 60 if len(title) > 20 else 30
            Thread(target=widget.label_print, args=(self.title_label, title, delay, True, 0.75, fps)).start()
            time.sleep(0.25)
            Thread(target=widget.label_print, args=(self.artist_label, artist)).start()
        self.stop_scrolling = False

    def topMost(self):
        while True:
            self.attributes('-topmost', True)
            self.lift()
            time.sleep(0.01)

    def scrolling_t(self):
        while True:
            if self.length > zoom(225):
                time.sleep(1)
                pos = 0
                while self.length > zoom(225) and (not self.stop_scrolling):
                    self.title_label.place(x=zoom(0) - pos, y=zoom(0), width=self.length, height=zoom(37))
                    self.title_label2.place(x=zoom(100) + self.length - pos, y=zoom(0), width=self.length,
                                            height=zoom(37))

                    if pos >= self.length + zoom(100):
                        self.title_label.place(x=zoom(0), y=zoom(0), width=self.length, height=zoom(37))
                        self.title_label2.place(x=zoom(100) + self.length, y=zoom(0), width=self.length,
                                                height=zoom(37))
                        time.sleep(7)
                        break
                    pos += 1
                    time.sleep(0.008)

            else:
                time.sleep(0.5)

    def scrolling_a(self):
        while True:
            if self.length2 > zoom(225):
                time.sleep(1)
                pos = 0
                while self.length2 > zoom(225) and (not self.stop_scrolling):
                    self.artist_label.place(x=zoom(0) - pos, y=zoom(0), width=self.length2, height=zoom(37))
                    self.artist_label2.place(x=zoom(100) + self.length2 - pos, y=zoom(0), width=self.length2,
                                             height=zoom(37))

                    if pos >= self.length2 + zoom(100):
                        self.artist_label.place(x=zoom(0), y=zoom(0), width=self.length2, height=zoom(37))
                        self.artist_label2.place(x=zoom(100) + self.length2, y=zoom(0), width=self.length2,
                                                 height=zoom(37))
                        time.sleep(7)
                        break
                    pos += 1
                    time.sleep(0.008)

            else:
                time.sleep(0.5)

    def play_toggle_animate(self):
        imgs = IMG_CACHE2.copy()
        if self.paused:
            imgs.reverse()
        index = 0
        while index < len(imgs) - 1:
            self.stop_button.configure(image=imgs[index])
            index += 2
            time.sleep(0.008)
        self.stop_button.configure(image=imgs[-1])

    def play_toggle_animate_pause(self):
        imgs = IMG_CACHE2.copy()
        imgs.reverse()
        index = 0
        while index < len(imgs) - 1:
            self.stop_button.configure(image=imgs[index])
            index += 2
            time.sleep(0.008)
        self.stop_button.configure(image=imgs[-1])

    def play_toggle_animate_play(self):
        imgs = IMG_CACHE2.copy()
        index = 0
        while index < len(imgs) - 1:
            self.stop_button.configure(image=imgs[index])
            index += 2
            time.sleep(0.008)
        self.stop_button.configure(image=imgs[-1])

    def toggle_pausing(self, event=None):
        # m_x, m_y = event.x, event.y
        #
        # if self.stop_button.winfo_x() <= m_x <= self.stop_button.winfo_x() + self.stop_button.winfo_width() and \
        #         self.stop_button.winfo_y() <= m_y <= self.stop_button.winfo_y() + self.stop_button.winfo_height():

        self.focus_set()
        self.stop_gyrate = True
        artist, title, info, session, paused = asyncio.run(kanki.get_media_info())
        if not paused:
            kanki.pause(session)
        else:
            kanki.play(session)

        self.stop_gyrate = False

    def skip_next(self, event=None):
        self.focus_set()
        artist, title, info, session, paused = asyncio.run(kanki.get_media_info())
        kanki.next_s(session)

    def skip_previous(self, event=None):
        self.focus_set()
        artist, title, info, session, paused = asyncio.run(kanki.get_media_info())
        kanki.previous(session)

    def check_pause(self):
        while True:
            with open("basic\\paused.txt", "r") as f:
                status = f.read()
                if status == "paused" and not self.paused:
                    self.paused = True
                    Thread(target=self.play_toggle_animate_pause).start()
                elif status == "play" and self.paused:
                    self.paused = False
                    Thread(target=self.play_toggle_animate_play).start()
            time.sleep(0.01)

    def gyrating(self):
        times = 0
        while True:
            if self.stop_gyrate:
                continue
            if not self.paused:
                icon = IMG_CACHE[times]
                # x = self.icon_label.winfo_width() // 2
                # self.icon_label.delete("all")
                # self.icon_label.create_image((x, x), image=icon)
                self.icon_label.configure(image=icon)
                self.icon_label.update()
                times += 1
                if times > 599:
                    times = 0

            if self.restart:
                if times > 300:
                    gap = max(round((599 - times) / 60), 1)
                    while times <= 599:
                        icon = IMG_CACHE[times]
                        self.icon_label.configure(image=icon)
                        self.icon_label.update()
                        times += gap
                        time.sleep(0.008)
                else:
                    gap = max(round(times / 60), 1)
                    while times >= 0:
                        icon = IMG_CACHE[times]
                        self.icon_label.configure(image=icon)
                        self.icon_label.update()
                        times -= gap
                        time.sleep(0.008)
                times = 0
                icon = IMG_CACHE[times]
                self.icon_label.configure(image=icon)
                self.icon_label.update()
                self.restart = False
            time.sleep(0.016)


class ConfigurateWindow(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master=master)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.disappear)
        windowInit(self, 400, 0, False, lang.LANG["main.title"], "assets\\music_icon.ico")
        self.icon = Image.open("assets\\music_icon.png")
        self.cross = ImageTk.PhotoImage(Image.open("assets\\cross.png").resize((zoom(16), zoom(16))), master=self)
        self.ti_icon = ImageTk.PhotoImage(self.icon.resize((zoom(16), zoom(16))), master=self.master)
        self.ti_icon_la = ImageTk.PhotoImage(self.icon.resize((zoom(150), zoom(150))), master=self)
        self.thanks_tk = ImageTk.PhotoImage(Image.open("assets\\07222024_2.png").resize((zoom(100), zoom(100))), master=self)
        GLOBAL_IMG_CACHE["cross"] = self.cross
        GLOBAL_IMG_CACHE["ti_icon"] = self.ti_icon
        GLOBAL_IMG_CACHE["thanks"] = self.thanks_tk
        self.overrideredirect(True)
        self.attributes("-toolwindow", False)

        self.Style = Style()
        self.Style.configure("TFrame", background="#1b1b1b")
        self.Style.configure("title.TLabel", font=("Microsoft Yahei UI", 10, "bold"))
        self.Style.configure("normal.secondary.Link.TButton", focusthickness=0, relief="flat")
        self.Style.configure("normal.TLabel", font=("arial", "10"))
        self.Style.configure("redtip.danger.TLabel", font=("arial", "6"), )
        self.Style.configure("e.info.TLabel", anchor="e", font=("arial", "15", "bold"))
        self.Style.configure("green.success.Roundtoggle.Toolbutton", font=("arial", "10"))

        self.titleFrame = Frame(self)
        self.mainFrame = Frame(self)
        self.iconLabel = Label(self.titleFrame, image=self.ti_icon)
        self.titleLabel = Label(self.titleFrame, text=lang.LANG["main.setting"].upper(), style="title.TLabel")
        self.closeButton = Button(self.titleFrame, image=self.cross, command=self.disappear)

        self.iconLabel.place(x=zoom(2), y=zoom(0), width=zoom(25), height=zoom(25))
        self.titleLabel.place(x=zoom(27), y=zoom(0), width=zoom(200), height=zoom(25))
        self.closeButton.place(x=zoom(360), y=zoom(0), width=zoom(40), height=zoom(25))
        
        self.titleFrame.place(x=zoom(0), y=zoom(0), width=zoom(400), height=zoom(25))
        self.mainFrame.place(x=zoom(0), y=zoom(25), width=zoom(400), height=zoom(500))

        self.basic_frame = LabelFrame(self.mainFrame, text=lang.LANG["config.basic"])
        self.inter_frame = LabelFrame(self.mainFrame, text=lang.LANG["config.interface"])
        self.language_frame = LabelFrame(self.mainFrame, text=lang.LANG["config.interface"])
        self.proxy_frame = LabelFrame(self.mainFrame, text=lang.LANG["config.proxy"])
        self.shortcut_frame = LabelFrame(self.mainFrame, text=lang.LANG["config.shortcut"])

        self.ui_lang_frame = Frame(self.basic_frame)
        self.ui_lang_tip = Label(self.ui_lang_frame, text=lang.LANG["config.ui_lang"] + "*", style="normal.TLabel")
        langs = list(LANG_DICT.keys())
        # print(langs)
        self.ui_lang_box = Combobox(self.ui_lang_frame, values=langs)
        self.ui_lang_box.bind("<<ComboboxSelected>>", self.change_lang)
        self.ui_lang_box.current(langs.index(lang.LANG["language_name"]))

        self.flip_frame = Frame(self.inter_frame)
        self.flip_bool = BooleanVar(self)
        self.flip_bool.set(True) if CONFIG["CONFIG"]["flip"] == "true" else self.flip_bool.set(False)
        self.flip_chk = Checkbutton(self.flip_frame, style="success.Roundtoggle.Toolbutton", command=self.set_flip,
                                    text=lang.LANG["config.interface.flip"], variable=self.flip_bool)

        self.cs_path_frame = Frame(self.basic_frame)
        self.cs_path_tip = Label(self.cs_path_frame, text=lang.LANG["config.game_path"] + "*", style="normal.TLabel")
        self.path = ""
        self.cs_path_box = Entry(self.cs_path_frame)
        self.cs_path_btn = Button(self.cs_path_frame,
                                  text=lang.LANG["config.game_path.btn"], style="normal.info.Link.TButton")
        self.cs_path_box.insert(END, self.path)
        self.cs_path_box.config(state="disabled")

        self.dst_frame = Frame(self.language_frame)
        self.dst_tip = Label(self.dst_frame, text=lang.LANG["config.dst_lang"], style="normal.TLabel")
        self.dst_box = Entry(self.dst_frame)
        self.dst_box.insert(END, "")

        self.ing_frame = Frame(self.language_frame)
        self.ing_tip = Label(self.ing_frame, text=lang.LANG["config.default_lang"], style="normal.TLabel")
        self.ing_box = Entry(self.ing_frame)
        self.ing_box.insert(END, "")

        self.stran_frame = Frame(self.shortcut_frame)
        self.stran_tip = Label(self.stran_frame, text=lang.LANG["config.shortcut.selftrans"], style="normal.TLabel")
        self.stran_box = Entry(self.stran_frame)
        self.stran_box.insert(END, "")

        self.tog_frame = Frame(self.shortcut_frame)
        self.tog_tip = Label(self.tog_frame, text=lang.LANG["config.shortcut.toggle"], style="normal.TLabel")
        self.tog_box = Entry(self.tog_frame)
        self.tog_box.insert(END, "")

        self.pxy_frame = Frame(self.proxy_frame)

        self.thanks_frame = Frame(self.mainFrame)

        self.thanks_tip = Label(self.thanks_frame, text="Thanks for your support", style="e.info.TLabel")
        self.thanks_tip2 = Label(self.thanks_frame, text="made by HoldWind", style="normal.TLabel")
        self.thanks_img = Label(self.thanks_frame, image=self.thanks_tk)

        self.gpowered_frame = Frame(self.mainFrame)
        self.gpowered_img = Label(self.gpowered_frame, font=("Microsoft Yahei UI", 20, "bold"), text="カンキ（監聴）")

        self.misc_frame = LabelFrame(self.mainFrame, text=lang.LANG["config.misc"])
        self.id_frame = Frame(self.misc_frame)
        self.id_tip = Label(self.id_frame, text=lang.LANG["config.account_name"], style="normal.TLabel")
        self.id_box = Entry(self.id_frame)
        self.id_box.insert(END, "")

        self.url_frame = Frame(self.misc_frame)
        self.url_tip2 = Label(self.url_frame, text=lang.LANG["config.custom_url.tip"], style="redtip.danger.TLabel")
        self.url_tip = Label(self.url_frame, text=lang.LANG["config.custom_url"] + "*", style="normal.TLabel")

        self.url_box = Entry(self.url_frame)
        self.url_box.insert(END, "")

        self.star_tip = Label(self.mainFrame, text=lang.LANG["config.restart.tip"], style="warning.TLabel")

        self.basic_frame.place(x=zoom(25), y=zoom(5), width=zoom(345), height=zoom(50))
        self.ui_lang_frame.place(x=zoom(0), y=zoom(0), width=zoom(340), height=zoom(25))
        # self.cs_path_frame.place(x=zoom(0), y=zoom(30), width=zoom(340), height=zoom(25))

        self.ui_lang_tip.place(x=zoom(0), y=zoom(0), width=zoom(150), height=zoom(25))
        self.ui_lang_box.place(x=zoom(150), y=zoom(0), width=zoom(190), height=zoom(25))

        # self.cs_path_tip.place(x=zoom(0), y=zoom(0), width=zoom(140), height=zoom(25))
        # self.cs_path_box.place(x=zoom(140), y=zoom(0), width=zoom(125), height=zoom(25))
        # self.cs_path_btn.place(x=zoom(265), y=zoom(0), width=zoom(75), height=zoom(25))

        # self.language_frame.place(x=zoom(25), y=zoom(85), width=zoom(345), height=zoom(45))
        self.inter_frame.place(x=zoom(25), y=zoom(60), width=zoom(345), height=zoom(75))
        # self.dst_frame.place(x=zoom(0), y=zoom(0), width=zoom(150), height=zoom(25))
        self.flip_frame.place(x=zoom(0), y=zoom(0), width=zoom(200), height=zoom(25))
        self.flip_chk.place(x=zoom(0), y=zoom(0), width=zoom(150), height=zoom(25))
        self.ing_frame.place(x=zoom(150), y=zoom(0), width=zoom(190), height=zoom(25))

        self.dst_tip.place(x=zoom(0), y=zoom(0), width=zoom(100), height=zoom(25))
        self.dst_box.place(x=zoom(100), y=zoom(0), width=zoom(50), height=zoom(25))

        self.ing_tip.place(x=zoom(0), y=zoom(0), width=zoom(140), height=zoom(25))
        self.ing_box.place(x=zoom(140), y=zoom(0), width=zoom(50), height=zoom(25))

        # self.shortcut_frame.place(x=zoom(25), y=zoom(135), width=zoom(345), height=zoom(75))
        self.stran_frame.place(x=zoom(0), y=zoom(0), width=zoom(170), height=zoom(50))
        self.tog_frame.place(x=zoom(170), y=zoom(0), width=zoom(170), height=zoom(50))

        self.stran_tip.place(x=zoom(0), y=zoom(0), width=zoom(170), height=zoom(25))
        self.stran_box.place(x=zoom(0), y=zoom(25), width=zoom(150), height=zoom(25))

        self.tog_tip.place(x=zoom(0), y=zoom(0), width=zoom(170), height=zoom(25))
        self.tog_box.place(x=zoom(0), y=zoom(25), width=zoom(150), height=zoom(25))

        # self.proxy_frame.place(x=zoom(25), y=zoom(215), width=zoom(345), height=zoom(100))
        self.pxy_frame.place(x=zoom(0), y=zoom(0), width=zoom(340), height=zoom(75))

        self.thanks_frame.place(x=zoom(400) - zoom(255),
                                y=zoom(500) - zoom(155), width=zoom(250), height=zoom(175))
        self.thanks_img.place(x=zoom(150), y=zoom(25), width=zoom(100), height=zoom(100))
        self.thanks_tip.place(x=zoom(25), y=zoom(125), width=zoom(225), height=zoom(25))
        self.thanks_tip2.place(x=zoom(140), y=zoom(0), width=zoom(125), height=zoom(25))
        self.gpowered_frame.place(x=zoom(5), y=zoom(500) - zoom(40), width=zoom(175),
                                  height=zoom(35))
        self.gpowered_img.place(x=zoom(0), y=zoom(0), width=zoom(175), height=zoom(35))

        # self.misc_frame.place(x=zoom(25), y=zoom(320), width=zoom(250), height=zoom(120))
        self.id_frame.place(x=zoom(0), y=zoom(0), width=zoom(240), height=zoom(25))
        self.url_frame.place(x=zoom(0), y=zoom(25), width=zoom(240), height=zoom(75))

        self.id_tip.place(x=zoom(0), y=zoom(0), width=zoom(100), height=zoom(25))
        self.id_box.place(x=zoom(100), y=zoom(0), width=zoom(135), height=zoom(25))

        self.url_tip.place(x=zoom(0), y=zoom(0), width=zoom(200), height=zoom(25))
        self.url_tip2.place(x=zoom(0), y=zoom(20), width=zoom(240), height=zoom(30))
        self.url_box.place(x=zoom(0), y=zoom(50), width=zoom(200), height=zoom(25))

        self.star_tip.place(x=zoom(25), y=zoom(440), width=zoom(250), height=zoom(25))

        self.top = Thread(target=self.topMost)
        self.on_run = False
        winX = zoom(400)
        winY = zoom(0)
        maxX = winapi.GetSystemMetrics(0)
        maxY = winapi.GetSystemMetrics(1)
        x = maxX // 2 - winX // 2
        y = maxY // 2 - winY // 2
        self.geometry(f"{zoom(400)}x{zoom(0)}+{x}+{maxY + 1}")
        # self.appear()

    def topMost(self):
        while self.on_run:
            try:
                self.attributes('-topmost', True)
                self.lift()
                time.sleep(0.01)
            except tk.TclError:
                break

    def set_flip(self, event=None):
        p_state = self.flip_bool.get()
        if p_state:
            self.master.flipping_text = True
            self.flip_chk.update()
            CONFIG["CONFIG"]["flip"] = "true"
        else:
            self.master.flipping_text = False
            self.flip_chk.update()
            CONFIG["CONFIG"]["flip"] = "false"

        with open(f"{LOCAL_PATH}\\config.ini", "w") as config_f:
            CONFIG.write(config_f)

    def change_lang(self, event=None):
        global lang
        language = self.ui_lang_box.get()
        CONFIG["CONFIG"]["lang"] = LANG_DICT[language]
        with open(f"{LOCAL_PATH}\\config.ini", "w") as config_f:
            CONFIG.write(config_f)
        lang = importlib.reload(lang2)
        lang.load_lang()
        self.update()

    def appear(self):
        self.on_run = True
        Thread(target=self.topMost).start()
        self.grab_set()
        middle(self, zoom(400), 0)
        self.configure(width=zoom(400), height=0)
        winX = zoom(400)
        winY = zoom(525)
        maxX = winapi.GetSystemMetrics(0)
        maxY = winapi.GetSystemMetrics(1)
        x = maxX // 2 - winX // 2
        y = maxY // 2 - winY // 2
        self.deiconify()
        widget.move_to(self, x, y, zoom(400), zoom(525), fps=FPS, is_windows=True)

    def disappear(self):
        global IN_CONFIG
        self.on_run = False
        IN_CONFIG = False
        self.grab_release()
        self.focus_set()
        self.attributes("-toolwindow", False)
        winX = zoom(400)
        winY = zoom(0)
        maxX = winapi.GetSystemMetrics(0)
        maxY = winapi.GetSystemMetrics(1)
        x = maxX // 2 - winX // 2
        y = maxY // 2 - winY // 2
        widget.move_to(self, x, maxY+1, zoom(400), zoom(0), fps=FPS, is_windows=True)


class SmallIcon(pystray.Icon):

    def __init__(self, master, name, icon=None, title=None, menu=None, **kwargs):
        self.show = True
        if menu is None:
            menu = (pystray.MenuItem(lang.LANG["miniicon.show"], self.show_window),
                    pystray.MenuItem(lang.LANG["main.setting"], self.setting_window),
                    pystray.MenuItem(lang.LANG["miniicon.quit"], self.quit_window))
        pystray.Icon.__init__(self, name=name, icon=icon, title=title, menu=menu, **kwargs)
        self.master = master

    def quit_window(self):
        self.visible = False
        self.stop()
        self.master.delete()

    def setting_window(self):
        global IN_CONFIG
        if not IN_CONFIG:
            IN_CONFIG = True
            self.master.config_win.appear()
        else:
            pass

    def show_window(self):
        if not self.show:
            x = self.master.winfo_screenwidth() - zoom(300)
            y = self.master.winfo_screenheight() - zoom(300) + zoom(100) - zoom(40)
            self.master.deiconify()
            widget.move_to(self.master, fps=FPS, x=x, y=y, width=zoom(300), height=zoom(300), is_windows=True)
            self.show = True
        else:
            widget.withdraw(self.master, fps=FPS, is_windows=True, direction="e")
            time.sleep(0.5)
            self.master.withdraw()
            self.show = False


def windowInit(master, width: int, height: int, canResize: bool, title: str, icon: str):
    master.config(width=zoom(width), height=zoom(height))
    if not canResize:
        master.resizable(width=False, height=False)
    master.title(title)
    master.iconbitmap(icon)


def middle(master, width=None, height=None):
    winX = width
    winY = height
    maxX = winapi.GetSystemMetrics(0)
    maxY = winapi.GetSystemMetrics(1)
    if winX is None:
        winX = master.winfo_width()
        winY = master.winfo_height()
    x = maxX // 2 - winX // 2
    y = maxY // 2 - winY // 2
    master.geometry(f"+{int(x)}+{int(y)}")


def noFun(*event):
    return event


def darkWindow(win):
    win.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ctypes.windll.user32.GetParent
    hwnd = get_parent(win.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ctypes.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ctypes.byref(value),
                         ctypes.sizeof(value))


def is_windows():
    if os.name == "nt":
        return True
    return False


def zoom(data) -> int:
    return round(data * ZOOM)
