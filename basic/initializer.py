import basic.libimport
basic.libimport.set_import_lib()
import subprocess
import time
import os
from tkinter.ttk import Progressbar
from threading import Thread
import ctypes
import urllib.request
import zipfile
from tkinter import *
from PIL import Image, ImageTk

winapi = ctypes.windll.user32
trueWidth = winapi.GetSystemMetrics(0)

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ZOOM = round((winapi.GetSystemMetrics(0) / trueWidth) + (0.1 * ((winapi.GetSystemMetrics(0) / trueWidth) / 2)), 1)


class BasicInitializer(Tk):

    def __init__(self):
        super().__init__()
        self.IMG_CACHE = []
        self.restart = False
        self.paused = False
        self.stop_gyrate = False
        self.withdraw()
        self.ring = Image.open("assets\\kanki_ring.png").resize((200, 200))
        self.animate_loader()
        windowInit(self, 800, 400, False, "Initializing", "assets\\music_icon.ico")
        middle(self, 800, 400)

        darkWindow(self)

        self.title_label = Label(self, text="KANKI", font=("Arial", 48, "bold"), bg="#1b1b1b", fg="white")
        self.progress = Frame(self, bg="#1b1b1b")
        self.progress_bar = Progressbar(self.progress, orient=HORIZONTAL)
        self.progress_label = Label(self.progress, font=("Arial", 12, "bold"),
                                    anchor="center", justify="center", bg="#1b1b1b", fg="white")
        self.progress_title = Label(self.progress, font=("Arial", 12), anchor="center", justify="center", bg="#1b1b1b",
                                    fg="white")
        self.icon_label = Label(self, bg="#1b1b1b")
        self.configure(background="#1b1b1b")

        self.icon_label.place(x=150, y=50, width=150, height=150)
        self.title_label.place(x=300, y=50, width=400, height=150)
        self.progress.place(x=100, y=250, width=600, height=100)
        self.progress_title.place(x=0, y=0, width=600, height=25)
        self.progress_bar.place(x=0, y=30, width=600, height=25)
        self.progress_label.place(x=0, y=60, width=600, height=25)

        Thread(target=self.gyrating).start()
        self.deiconify()

    def animate_loader(self):

        if not os.path.exists("assets\\gyrating\\sprite2.png"):
            os.makedirs("assets\\gyrating", exist_ok=True)
            self.generate_sprite_sheet()
        sprite = Image.open("assets\\gyrating\\sprite2.png")
        zoomed = 150
        if sprite.width != zoomed or sprite.height != zoomed * 600:
            self.generate_sprite_sheet()

        for i in range(600):
            frame = sprite.crop((0, zoomed * i, zoomed, zoomed * (i + 1)))
            self.IMG_CACHE.append(ImageTk.PhotoImage(frame))

    def generate_sprite_sheet(self, path="assets\\gyrating\\sprite2.png", frame_count=600):
        zoomed = 150
        sprite_size = (zoomed, zoomed * frame_count)

        sprite = Image.new("RGBA", sprite_size, (0, 0, 0, 0))
        for i in range(frame_count):
            angle = i * 0.6 * -1
            ring_rotated = self.ring.rotate(angle, resample=Image.BILINEAR)
            frame = Image.new("RGBA", (self.ring.width, self.ring.height), (0, 0, 0, 0))
            frame.paste(ring_rotated, (0, 0), ring_rotated)
            frame = frame.resize((zoomed, zoomed), resample=Image.BILINEAR)

            sprite.paste(frame, (0, zoomed * i))

        sprite.save(path, "PNG")

    def update_version(self):
        self.progress_title.configure(text="Downloading Dependence")
        self.progress_label.configure(text="----")
        self.updating(self.progress_bar, self.progress_label)

    def updating(self, p_bar: Progressbar, p_t: Label):
        speed_time = 0
        speed_size = 0
        speed_timer = 0
        speed = 0

        def _download_listener(blocknum, bs, size):
            nonlocal speed_time, speed_size, speed_timer, speed, p_bar, p_t
            if speed_time == 0:
                speed_time = time.time()

            def division(x, y):
                if 0 not in (x, y):
                    return x / y
                else:
                    return 0

            speed_size += bs
            speed_timer += 1

            if speed_timer > 100:
                duration = time.time() - speed_time
                speed_time = 0
                speed = round(speed_size / (1024 * 1024 * duration) * 8, 2) if duration > 0 else 0
                speed_size = 0
                speed_timer = 0

            now_value = min(size, round(blocknum * bs))
            p_bar["value"] = now_value
            p_bar["maximum"] = size
            p_t.configure(text=f"Downloading... " +
                               f"{division(now_value, size) * 100:.2f}% {speed} Mbps")

        URL = f'https://files.hlhtstudios.com/archives/kanki_depend.zip'
        USER_PATH = os.path.expanduser('~')
        TEMP_PATH = f"{USER_PATH}\\AppData\\Local\\Temp"
        urllib.request.urlretrieve(URL, f"{TEMP_PATH}\\kanki_depend.zip", reporthook=_download_listener)

        def extractor(src, dst, mod=False):
            nonlocal speed_time, speed_size, speed_timer, speed, p_bar, p_t

            def division(x, y):
                if 0 not in (x, y):
                    return x / y
                else:
                    return 0

            with zipfile.ZipFile(src, "r") as zip_ref:
                p_bar["value"] = 0
                p_bar["maximum"] = len(zip_ref.namelist())
                for z_file in zip_ref.namelist():
                    try:
                        file_path = os.path.join(dst, z_file)

                        # Check if the file already exists
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            # Remove the existing file
                            os.remove(file_path)
                        zip_ref.extract(member=z_file, path=dst)
                    except PermissionError:
                        pass

                    p_bar["value"] += 1
                    p_t.configure(
                        text="Extracting... " +
                             f" {division(p_bar['value'], p_bar['maximum']) * 100:.2f}%")

        LIB_PATH = f"{USER_PATH}\\AppData\\Local\\HLHT\\KANKI\\lib"
        os.makedirs(LIB_PATH, exist_ok=True)
        extractor(f"{TEMP_PATH}\\kanki_depend.zip", LIB_PATH)
        restart()

    def gyrating(self):
        times = 0
        while True:
            if self.stop_gyrate:
                continue
            if not self.paused:
                icon = self.IMG_CACHE[times]
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
                        icon = self.IMG_CACHE[times]
                        self.icon_label.configure(image=icon)
                        self.icon_label.update()
                        times += gap
                        accurate_delay(8)
                else:
                    gap = max(round(times / 60), 1)
                    while times >= 0:
                        icon = self.IMG_CACHE[times]
                        self.icon_label.configure(image=icon)
                        self.icon_label.update()
                        times -= gap
                        accurate_delay(8)
                times = 0
                icon = self.IMG_CACHE[times]
                self.icon_label.configure(image=icon)
                self.icon_label.update()
                self.restart = False
            accurate_delay(16)


def restart():
    WORK_PATH = os.getcwd()
    print("Hard restarting via command line...")
    try:
        subprocess.Popen([f"{WORK_PATH}\\Python310\\pythonw.exe", f"{WORK_PATH}\\main.pyw"])
        os._exit(114514)  # Immediate process exit, no cleanup
    except Exception as e:
        print(f"Restart failed", e)


def windowInit(master, width: int, height: int, canResize: bool, title: str, icon: str):
    master.config(width=width, height=height)
    if not canResize:
        master.resizable(width=False, height=False)
    master.title(title)
    master.iconbitmap(icon)


def accurate_delay(delay):
    """ Function to provide accurate time delay in millisecond"""
    winmm = ctypes.windll.winmm
    winmm.timeBeginPeriod(1)
    time.sleep(delay / 1000)
    winmm.timeEndPeriod(1)


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
