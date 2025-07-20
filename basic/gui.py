import basic.libimport
basic.libimport.set_import_lib()
from PyQt5.QtSvg import QSvgRenderer
import io
from basic.widget import HQEndlessAnimation, HQPrinter, HQAnimate, HQFade, HBoolean, HQNormalAnimation
import ctypes
import sys
from threading import Thread
import importlib
import time
import subprocess
import urllib
import zipfile
from basic.updater import check_version
import os
import asyncio
from PIL import ImageSequence, Image
import PyQt5.QtWidgets as qt
from PyQt5.QtGui import QIcon, QPixmap, QFont, QImage, QFontMetrics, QCloseEvent, QCursor, QPainter, QTransform
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QThread, QObject, QBuffer, QIODevice
import basic.widget as widget
import basic.kanki as kanki
import pystray
import pywinstyles
import basic.lang as lang
from basic.constants import *
from ttkbootstrap import *
import tkinter as tk

lang2 = lang

winapi = ctypes.windll.user32
trueWidth = winapi.GetSystemMetrics(0)

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ZOOM = round((winapi.GetSystemMetrics(0) / trueWidth) + (0.1 * ((winapi.GetSystemMetrics(0) / trueWidth) / 2)), 1)
print(ZOOM)

IMG_CACHE = []
IMG_CACHE2 = []
IMG_CACHE3 = []
GLOBAL_IMG_CACHE = {}
IN_CONFIG = False
FPS = 120


class MainWindow(qt.QMainWindow):
    update_infos_signal = pyqtSignal(str, str)
    delete_signal = pyqtSignal()
    pause_signal = pyqtSignal(bool)
    updater_signal = pyqtSignal(str, str)

    def __init__(self, flipping=False, fps=120, app=None):
        global FPS
        start_time = time.time()
        qt.QMainWindow.__init__(self)
        self.hide()
        self.length = 0
        self.length2 = 0
        self.stop_scrolling = False
        self.restart = False
        self.paused = HBoolean(False)
        self.toolbar = False
        self.stop_gyrate = False
        self.need_update = False
        self.working = True
        self.app = app
        self.flipping_text = flipping
        self.title = ""
        self.artist = ""
        self.covered = False
        self.switching = HBoolean(False)
        FPS = fps

        if check_version():
            self.need_update = True

        with open(f"{LOCAL_PATH}\\paused.txt", "rb") as f:
            if f.read().decode("utf-8") == "paused":
                self.paused.set(True)
            else:
                self.paused.set(False)

        windowInit(self, 300, 300, False, "Kanki", "assets\\music_icon.ico")
        self.icon = Image.open("assets\\music_icon.png").resize((zoom(100), zoom(100)))
        self.ring = Image.open("assets\\kanki_ring.png").resize((zoom(100), zoom(100)))
        self.inner = Image.open("assets\\kanki_inner.png").resize((zoom(100), zoom(100)))
        self.small = SmallIcon(self, name="Main", icon=Image.open("assets\\music_icon.ico"), title="Kanki")
        self.small.run_detached()
        icon = pil_image_to_qpixmap(self.icon.resize((zoom(75), zoom(75))))
        IMG_CACHE.append(icon)

        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setEnabled(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        x = self.winfo_screenwidth() - self.width()
        y = self.winfo_screenheight() - self.height() + zoom(100) - zoom(40)

        self.move(x, y)

        self.load_animation()
        self.background_w = qt.QFrame(self)
        self.main_widget = qt.QFrame(self)

        self.font_ti = QFont("Microsoft YaHei UI", 20, QFont.Bold)
        self.font_ar = QFont("Microsoft YaHei UI", 15)
        self.icon_label = ClickableLabel(self.main_widget)
        self.icon_img = ClickableLabel(self.main_widget)
        self.artist_frame = ScrollingFrame(self.main_widget, master=self, type=2)
        self.artist_label = qt.QLabel("Monster Siren Records", parent=self.artist_frame)
        self.artist_label2 = qt.QLabel("Monster Siren Records", parent=self.artist_frame)
        self.title_frame = ScrollingFrame(self.main_widget, master=self)
        self.title_label = qt.QLabel("Scordatura", parent=self.title_frame)
        self.title_label2 = qt.QLabel("Scordatura", parent=self.title_frame)
        self.toolbar_frame = qt.QFrame(self)
        self.stop_button = ClickableLabel(self.toolbar_frame)
        self.prev_button = ClickableLabel(self.toolbar_frame)
        self.next_button = ClickableLabel(self.toolbar_frame)
        self.central = qt.QWidget(self)

        self.layout = qt.QVBoxLayout(self.central)

        # in __init__:
        self.update_infos_signal.connect(self.update_infos)
        self.delete_signal.connect(self.delete)
        self.pause_signal.connect(self.play_toggle_animate)
        self.updater_signal.connect(self.set_updating_info)
        Thread(target=self.tkinter_handler).start()

        debug(f"Generate Main Window use: {time.time() - start_time} s", COLORS.SUCCESS, "GUI")

    def tkinter_handler(self):
        self.config_win = ConfigurateWindow(master=self)
        self.config_win.mainloop()

    def item_configurate(self):
        start_time = time.time()
        self.icon_label.setGeometry(zoom(0), zoom(112), zoom(75), zoom(75))
        # self.icon_label.setStyleSheet("background-color: #1b1b1b; border: none;")
        self.icon_label.setCursor(Qt.PointingHandCursor)
        self.icon_img.setGeometry(zoom(75), zoom(112), zoom(0), zoom(75))
        # self.main_widget.setStyleSheet("background-color: #1b1b1b; border: none;")
        self.artist_label.setFont(QFont("Microsoft Yahei UI", 15))
        self.artist_label.setGeometry(zoom(0), zoom(0), zoom(225), zoom(37))
        self.artist_label.setStyleSheet("""
                   color: #ffffff;
                   border: none;
               """)
        self.artist_label2.setFont(QFont("Microsoft Yahei UI", 15))
        self.artist_label2.setGeometry(zoom(325), zoom(0), zoom(225), zoom(37))
        self.artist_label2.setStyleSheet("""
                   color: #ffffff;
                   border: none;
               """)
        self.title_label.setFont(QFont("Microsoft Yahei UI", 20, QFont.Bold))
        self.title_label.setGeometry(zoom(0), zoom(0), zoom(200), zoom(37))
        self.title_label.setStyleSheet("""
                   color: #ffffff;
                   border: none;
               """)
        self.title_label2.setFont(QFont("Microsoft Yahei UI", 20, QFont.Bold))
        self.title_label2.setGeometry(zoom(325), zoom(0), zoom(200), zoom(37))
        self.title_label2.setStyleSheet("""
                         color: #ffffff;
                         border: none;
                     """)
        img = IMG_CACHE2[0] if self.paused.get() else IMG_CACHE2[-1]
        self.prev_button.setPixmap(IMG_CACHE3[0])
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setPixmap(img)
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.next_button.setPixmap(IMG_CACHE3[1])
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setGeometry(zoom(55), zoom(5), zoom(40), zoom(40))
        self.prev_button.setGeometry(zoom(10), zoom(10), zoom(30), zoom(30))
        self.next_button.setGeometry(zoom(110), zoom(10), zoom(30), zoom(30))
        self.artist_frame.setGeometry(zoom(80), zoom(150), zoom(225), zoom(37))
        self.title_frame.setGeometry(zoom(80), zoom(117), zoom(225), zoom(37))
        self.main_widget.setGeometry(0, zoom(100), zoom(75), self.height())
        self.background_w.setGeometry(0, 0, self.width(), self.height())
        self.toolbar_frame.setGeometry(zoom(75), zoom(100), zoom(150), zoom(0))
        self.icon_label.clicked.connect(self.toggle_toolbar)
        self.icon_label.setCursor(Qt.PointingHandCursor)
        self.icon_label.rightClicked.connect(self.toggle_pausing)
        self.icon_img.clicked.connect(self.toggle_toolbar)
        self.icon_img.setCursor(Qt.PointingHandCursor)
        self.icon_img.rightClicked.connect(self.toggle_pausing)
        self.stop_button.clicked.connect(self.toggle_pausing)
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.clicked.connect(self.skip_previous)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.next_button.clicked.connect(self.skip_next)
        self.next_button.setCursor(Qt.PointingHandCursor)

        # Step 3: Add widgets into the layout
        # self.layout.addWidget(self.main_widget)
        # self.layout.addWidget(self.background_w)
        # self.layout.addWidget(self.toolbar_frame)

        # self.central.setLayout(self.layout)
        self.setCentralWidget(self.central)
        self.central.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        debug(f"Finished widget config and logic bind in: {time.time() - start_time} s", COLORS.SUCCESS, "GUI")

    def animate_binding(self):
        # Animation registering
        start_time = time.time()
        self.gyrator = HQEndlessAnimation(self.icon_label, IMG_CACHE, 60, self.paused, have_reset=True)
        self.title_flipper = HQPrinter(self.title_label, "")
        self.artist_flipper = HQPrinter(self.artist_label, "")
        self.main_mover = HQAnimate(self.main_widget, self.main_widget.geometry(), LOCK=self.switching)
        self.cover_mover = HQAnimate(self.icon_img, self.icon_img.geometry(), LOCK=self.switching)
        self.trans_key = HQFade(self, 0, 1, fade_in=True)
        self.self_mover = HQAnimate(self, self.geometry())
        self.tool_mover = HQAnimate(self.toolbar_frame, self.toolbar_frame.geometry())
        self.pause_player = HQNormalAnimation(self.stop_button, IMG_CACHE, 60)

        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.raise_()  # Bring window to front
        self.activateWindow()

        if self.need_update:
            Thread(target=self.update_version).start()
            debug("Starting Update", COLORS.SUCCESS, "GUI")
        else:
            self.title_frame.start(self.title_label, self.title_label2, 0)
            self.artist_frame.start(self.artist_label, self.artist_label2, 0)
            # WorkerThread(target=self.check_pause).start()

    def display_all(self, get_info):
        start_time = time.time()
        self.stop_button.show()
        self.prev_button.show()
        self.next_button.show()
        self.title_label.show()
        self.title_label2.show()
        self.artist_label.show()
        self.artist_label2.show()
        self.icon_label.show()
        self.icon_img.show()
        self.artist_frame.show()
        self.title_frame.show()
        self.main_widget.show()
        self.background_w.show()
        self.toolbar_frame.show()
        ti_measure = QFontMetrics(self.font_ti)
        self.length = length = ti_measure.horizontalAdvance("a（いwadszcxw")
        self.title_label.setText("a（いwadszcxw")
        self.title_label.setGeometry(zoom(0), zoom(0), length, zoom(37))
        width = self.width()
        height = self.height()
        self.icon_label.setVisible(True)
        self.icon_label.setEnabled(True)
        self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.main_widget.setGeometry(QRect(0, zoom(100), length, zoom(37)))

        def finish_launch():

            self.gyrator.start()
            self.gyrator.current_frame = 1
            self.title_label.setText("        ")
            self.artist_label.setText("        ")

            self.setWindowOpacity(0.0)
            self.main_widget.setGeometry(0, zoom(100), zoom(100), self.height())
            self.show()
            self.trans_key.fade_in()
            self.main_mover.force_in = True
            self.icon_label.raise_()
            self.icon_img.raise_()
            Thread(target=get_info, args=[self]).start()
            Thread(target=self.check_pause).start()
            print('Final')
            debug(f"GUI init completed in {time.time() - start_time} s", COLORS.SUCCESS, "GUI")

        self.title_flipper.print("a（いwadszcxw", funcs=[finish_launch])
        # finish_launch()

    def on_update_icon(self, pixmap):
        self.icon_label.setPixmap(pixmap)

    def set_updating_info(self, title, artist):
        self.title_label.setGeometry(zoom(0), zoom(0), zoom(400), zoom(37))
        self.artist_label.setGeometry(zoom(0), zoom(0), zoom(400), zoom(37))
        self.title_label.show()
        self.artist_label.show()
        self.title_label.setText(title)
        self.artist_label.setText(artist)

    def update_version(self):
        # time.sleep(2)
        speed_time = 0
        speed_size = 0
        speed_timer = 0
        speed = 0
        self.paused.set(False)

        def _download_listener(blocknum, bs, size):
            nonlocal speed_time, speed_size, speed_timer, speed
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

            self.updater_signal.emit(
                f"{lang.LANG['main.interface.updating']}",
                f"{division(now_value, size) * 100:.2f}% {speed} Mbps"
            )
            # debug(f"{division(now_value, size) * 100:.2f}% {speed} Mbps")

        URL = f'{ARCHIVE_HOST}/archives/kanki_package.zip'
        debug("Downloading Kanki Package", COLORS.INFO, "UPDATER")
        self.working = False
        x = 0
        y = 0
        width = self.width()
        height = self.height()

        self.updater_signal.emit(
            lang.LANG['main.interface.updating'],
            "----"
        )

        urllib.request.urlretrieve(URL, f"{TEMP_PATH}\\main_package.zip", reporthook=_download_listener)

        def extractor(src, dst, mod=False):
            nonlocal speed_time, speed_size, speed_timer, speed

            def division(x, y):
                if 0 not in (x, y):
                    return x / y
                else:
                    return 0

            with zipfile.ZipFile(src, "r") as zip_ref:
                now_size = 0
                max_size = len(zip_ref.namelist())
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
                    now_size += 1
                    self.updater_signal.emit(
                        f"{lang.LANG['main.interface.extracting']}",
                        f"{division(now_size, max_size) * 100:.2f}%"
                    )

        extractor(f"{TEMP_PATH}\\main_package.zip", RUN_PATH)
        restart()

    def set_japanese_mode(self):
        self.font_ti = QFont("Yu Gothic", 22, QFont.Bold)
        self.font_ar = QFont("Yu Gothic", 16)
        self.artist_label.setFont(self.font_ar)
        self.artist_label2.setFont(self.font_ar)
        self.title_label.setFont(self.font_ti)
        self.title_label2.setFont(self.font_ti)

    def set_normal_mode(self, index=0):
        self.font_ti = QFont("Microsoft Yahei UI", 20, QFont.Bold)
        self.font_ar = QFont("Microsoft Yahei UI", 15)
        self.artist_label.setFont(self.font_ar)
        self.artist_label2.setFont(self.font_ar)
        self.title_label.setFont(self.font_ti)
        self.title_label2.setFont(self.font_ti)

    def closeEvent(self, event: QCloseEvent):
        self.delete()
        event.ignore()

    def delete(self, event=None):
        self.toolbar = False
        self.tool_mover.play(QRect(zoom(75), zoom(100), zoom(150), zoom(0)))
        x = 0
        y = 0
        width = self.width()
        height = self.height()

        def delete3():
            self.app.quit()
            os._exit(114514)
            self.close()

        def delete2():
            self.self_mover.withdraw(direction="e", fps=FPS, functions=[delete3])
            self.trans_key.fade_out()

        self.main_mover.play(QRect(x, y, zoom(75), height), functions=[delete2])

    def fade_out(self, light=1.0, during=0.5, fps=FPS):
        def func(light, during, fps):
            # step = round(light / fps / during, 4)
            widget.accurate_delay(10)
            step = round(light / fps / during, 4)
            fps_delay = widget.get_frame_rate_delay(fps)
            start_time = time.time()
            for f in range(fps):
                start = time.time()
                self.setWindowOpacity(light)
                light -= step
                light = max(light, 0)
                end = time.time()
                if end - start <= fps_delay and f >= (end - start_time) / fps_delay:
                    widget.accurate_delay(int(round(fps_delay - (end - start), 3) * 1000))

        WorkerThread(target=func, args=(light, during, fps)).start()

    def fade_in(self, light=1.0, during=0.5, fps=FPS):
        def func(light, during, fps):
            # step = round(light / fps / during, 4)
            _light = 0
            widget.accurate_delay(10)
            step = round(light / fps / during, 4)
            fps_delay = widget.get_frame_rate_delay(fps)
            start_time = time.time()
            for f in range(fps):
                start = time.time()
                self.setWindowOpacity(_light)
                _light += step
                _light = min(_light, light)
                end = time.time()
                if end - start <= fps_delay and f >= (end - start_time) / fps_delay:
                    widget.accurate_delay(int(round(fps_delay - (end - start), 3) * 1000))

        WorkerThread(target=func, args=(light, during, fps)).start()

    def prepare_image_premultiplied(self, path, size):
        img = Image.open(path).resize(size, resample=Image.BILINEAR).convert("RGBA")

        # Premultiply alpha (so edge pixels are not "white-on-black" but "white-on-transparent")
        r, g, b, a = img.split()
        r = r.point(lambda i: i * (a.getpixel((0, 0)) / 255))
        g = g.point(lambda i: i * (a.getpixel((0, 0)) / 255))
        b = b.point(lambda i: i * (a.getpixel((0, 0)) / 255))
        premultiplied = Image.merge("RGBA", (r, g, b, a))

        # Composite onto truly transparent canvas (not needed if alpha already clean)
        final = Image.new("RGBA", img.size, (0, 0, 0, 0))
        final.alpha_composite(premultiplied)

        return pil_image_to_qpixmap(final)

    def premultiply_alpha(self, image: Image.Image) -> Image.Image:
        """Convert image to premultiplied alpha (to remove dark edge halos)."""
        image = image.convert("RGBA")
        pixels = image.load()
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    pixels[x, y] = (0, 0, 0, 0)
                else:
                    r = int(r * a / 255)
                    g = int(g * a / 255)
                    b = int(b * a / 255)
                    pixels[x, y] = (r, g, b, a)
        return image

    def generate_sprite_sheet(self, path="assets\\gyrating\\sprite.png", frame_count=600):
        zoomed = zoom(75)
        sprite_size = (zoomed, zoomed * frame_count)

        sprite = Image.new("RGBA", sprite_size, (0, 0, 0, 0))
        for i in range(frame_count):
            angle = i * 0.6 * -1
            ring_rotated = self.ring.rotate(angle, resample=Image.BICUBIC)
            frame = Image.new("RGBA", (self.ring.width, self.ring.height), (0, 0, 0, 0))
            frame.paste(ring_rotated, (0, 0), ring_rotated)
            frame = frame.resize((zoomed, zoomed), resample=Image.BICUBIC)

            sprite.paste(frame, (0, zoomed * i))

        sprite.save(path, "PNG")

    def load_animation(self):
        global IMG_CACHE, IMG_CACHE2, IMG_CACHE3
        IMG_CACHE = []
        base = self.inner
        start_time = time.time()

        zoomed = zoom(75)
        renderer = QSvgRenderer("assets\\kanki_ring.svg")

        for i in range(600):
            angle = i * 0.6

            # Create a fixed-size canvas
            frame = QPixmap(zoomed, zoomed)
            frame.fill(Qt.transparent)

            # Rotate the painter, not the image
            painter = QPainter(frame)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.translate(zoomed / 2, zoomed / 2)
            painter.rotate(angle)
            painter.translate(-zoomed / 2, -zoomed / 2)

            # Render SVG freshly each time (no wobble)
            renderer.render(painter)
            painter.end()

            IMG_CACHE.append(frame)

        IMG_CACHE2 = []
        im = Image.open("assets\\pausing.gif")
        _iter = ImageSequence.Iterator(im)
        for i in _iter:
            img = pil_image_to_qpixmap(i.resize((zoom(40), zoom(40))))
            IMG_CACHE2.append(img)

        IMG_CACHE3.append(pil_image_to_qpixmap(Image.open("assets\\previous.png").resize((zoom(30), zoom(30)))))
        IMG_CACHE3.append(pil_image_to_qpixmap(Image.open("assets\\next.png").resize((zoom(30), zoom(30)))))
        debug(f"Load image resources took {time.time() - start_time} s", COLORS.SUCCESS, "GUI")

    def toggle_toolbar(self, event=None):
        if self.toolbar:
            self.toolbar = False
            self.tool_mover.play(QRect(zoom(75), zoom(100), zoom(150), zoom(0)),
                                 duration=0.25, fps=FPS)

            covered = False
            if CONFIG["CONFIG"]["album"] == "true":
                covered = True

            if covered:
                if covered:
                    self.cover_mover.play(QRect(zoom(75)+1, zoom(112), zoom(0), zoom(75)),
                                          fps=FPS, functions=[self.icon_img.hide])
                else:
                    self.icon_img.hide()
        else:
            self.toolbar = True
            self.tool_mover.play(QRect(zoom(75), zoom(75), zoom(150), zoom(40)),
                                 duration=0.25, fps=FPS)
            covered = False
            if CONFIG["CONFIG"]["album"] == "true":
                covered = True

            if covered:
                if covered:
                    self.icon_img.show()
                    self.icon_img.setGeometry(zoom(75), zoom(112), zoom(0), zoom(75))
                    self.cover_mover.play(QRect(zoom(0), zoom(112), zoom(75)+1, zoom(75)),
                                          fps=FPS)
                else:
                    self.icon_img.hide()

    def update_infos(self, title, artist):
        debug(f"Updating infos for {title}, {artist}", COLORS.INFO, "GUI")
        self.switching.set(True)
        x = 0
        y = 0
        width = self.width()
        height = self.height()
        self.title = title
        self.artist = artist
        self.gyrator.reset()

        self.stop_scrolling = True
        func_list = [lambda: self.update_info2(title, artist)]

        if not title:
            title = "----"
        if not artist:
            artist = "----"

        if self.main_mover.isRunning():  # You need to implement this method
            self.main_mover.stop()
        if self.title_flipper.isRunning(): self.title_flipper.stop()
        if self.artist_flipper.isRunning(): self.artist_flipper.stop()
        if self.cover_mover.isRunning(): self.cover_mover.stop()

        self.switching.set(False)
        if self.icon_img.isVisible():
            self.cover_mover.play(QRect(zoom(75)+1, zoom(112), 0, zoom(75)),
                                  functions=[self.icon_img.hide])
        self.main_mover.play(QRect(x, y, zoom(75), height), functions=func_list, func_delay=250)
        # widget.move_to(self.icon_img, fps=FPS, x=zoom(75), y=zoom(112), width=zoom(0), height=zoom(75))

    def update_info2(self, title, artist):
        self.main_mover.force_in = False
        x = 0
        y = 0
        width = self.width()
        height = self.height()
        covered = False
        if self.switching.get():
            return
        if os.path.exists(f"{LOCAL_PATH}\\cover.png"):
            try:
                if self.switching.get():
                    return
                icon_img = Image.open(f"{LOCAL_PATH}\\cover.png")
                icon_img.load()
                # icon_img.show()
                icon_img = icon_img.convert("RGBA").resize((zoom(75), zoom(75)), resample=Image.BILINEAR)
                icon_tk = pil_image_to_qpixmap(icon_img)
                GLOBAL_IMG_CACHE[f"{LOCAL_PATH}\\cover.png"] = icon_tk
                self.icon_img.setPixmap(icon_tk)
                covered = True
            except Exception as e:
                debug(e, COLORS.ERROR, "GUI")

        if self.switching.get():
            return
        if CONFIG["CONFIG"]["album"] != "true":
            covered = False
        if check_japanese(title) or check_japanese(artist):
            self.set_japanese_mode()
        else:
            self.set_normal_mode()
        self.covered = covered
        if self.switching.get():
            return
        ti_measure = QFontMetrics(self.font_ti)
        ar_measure = QFontMetrics(self.font_ar)
        self.artist_frame.idle = True
        self.title_frame.idle = True
        self.title_frame.tick = 480
        self.artist_frame.tick = 480
        self.title_frame.pos = 0
        self.artist_frame.pos = 0
        self.length = length = ti_measure.horizontalAdvance(title)
        self.length2 = length2 = ar_measure.horizontalAdvance(artist)
        if self.switching.get():
            return
        self.title_label.setText(title)
        self.title_label2.setText(title)
        self.title_label.setGeometry(zoom(0), zoom(0), length, zoom(37))
        self.title_label2.setGeometry(zoom(100) + length, zoom(0), length, zoom(37))
        self.icon_img.setGeometry(zoom(75), zoom(112), zoom(0), zoom(75))
        self.title_label.show()
        self.title_label2.show()
        if self.switching.get():
            return
        if self.length < zoom(225):
            self.title_label2.hide()
        self.artist_label.setText(artist)
        self.artist_label2.setText(artist)
        self.artist_label.setGeometry(zoom(0), zoom(0), length2, zoom(37))
        self.artist_label2.setGeometry(zoom(100) + length2, zoom(0), length2, zoom(37))
        if self.length2 < zoom(225):
            self.artist_label2.hide()
        if self.switching.get():
            return

        if self.flipping_text:
            self.title_label.setText("")
            self.artist_label.setText("")
            delay = 0.75 if len(title) > 20 else 0.25
            fps = 60 if len(title) > 20 else 45
            if self.switching.get():
                return
            self.title_flipper.configure(title, delay, True, 0.75, fps)
            artist = self.artist
            covered = self.covered
            delay = 0.75 if len(artist) > 20 else 0.25
            fps = 60 if len(artist) > 20 else 45
            if self.switching.get():
                return
            self.artist_flipper.configure(artist, delay, True, 0.75, fps)
        if self.switching.get():
            return
        self.main_mover.play(QRect(x, y, width, height))
        if self.switching.get():
            return
        if covered:
            def remove_cover():
                if self.switching.get():
                    return
                self.cover_mover.play(QRect(zoom(75)+1, zoom(112), 0, zoom(75)),
                                      functions=[self.icon_img.hide])

            if self.switching.get():
                return
            funcs = [remove_cover]
            if self.toolbar:
                print("Tool on")
                funcs = []
            if self.switching.get():
                return
            self.icon_img.setGeometry(zoom(75), zoom(112), zoom(0), zoom(75))
            self.cover_mover.play(QRect(zoom(0), zoom(112), zoom(75)+1, zoom(75)), functions=funcs,
                                  func_delay=1500)
        else:
            if self.switching.get():
                return
            self.icon_img.hide()
        if self.flipping_text:
            if self.switching.get():
                return
            self.title_flipper.start()
            self.artist_flipper.start()
        self.stop_scrolling = False
        if self.switching.get():
            return

    def topMost(self):
        while True:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.raise_()  # Bring window to front
            self.activateWindow()
            time.sleep(0.01)

    def scrolling_t(self):
        while True:
            if self.length > zoom(225):
                time.sleep(1)
                pos = 0
                while self.length > zoom(225) and (not self.stop_scrolling):
                    self.title_label.setGeometry(zoom(0) - pos, zoom(0), self.length, zoom(37))
                    self.title_label2.setGeometry(zoom(100) + self.length - pos, zoom(0), self.length, zoom(37))

                    if pos >= self.length + zoom(100):
                        self.title_label.setGeometry(zoom(0), zoom(0), self.length, zoom(37))
                        self.title_label2.setGeometry(zoom(100) + self.length, zoom(0), self.length, zoom(37))
                        time.sleep(7)
                        break
                    pos += 1
                    widget.accurate_delay(8)

            else:
                time.sleep(0.5)

    def scrolling_a(self):
        while True:
            if self.length2 > zoom(225):
                time.sleep(1)
                pos = 0
                while self.length2 > zoom(225) and (not self.stop_scrolling):
                    self.artist_label.setGeometry(zoom(0) - pos, zoom(0), self.length2, zoom(37))
                    self.artist_label2.setGeometry(zoom(100) + self.length2 - pos, zoom(0), self.length2, zoom(37))

                    if pos >= self.length2 + zoom(100):
                        self.artist_label.setGeometry(zoom(0), zoom(0), self.length2, zoom(37))
                        self.artist_label2.setGeometry(zoom(100) + self.length2, zoom(0), self.length2, zoom(37))
                        time.sleep(7)
                        break
                    pos += 1
                    widget.accurate_delay(8)

            else:
                time.sleep(0.5)

    def play_toggle_animate(self, event):
        print(event)
        if event:
            self.play_toggle_animate_pause()
        else:
            self.play_toggle_animate_play()

    def play_toggle_animate_pause(self):
        imgs = IMG_CACHE2.copy()
        imgs.reverse()
        self.pause_player.play(imgs, 120)

    def play_toggle_animate_play(self):
        imgs = IMG_CACHE2.copy()
        self.pause_player.play(imgs, 120)

    def toggle_pausing(self, event=None):
        # m_x, m_y = event.x, event.y
        #
        # if self.stop_button.winfo_x() <= m_x <= self.stop_button.winfo_x() + self.stop_button.width() and \
        #         self.stop_button.winfo_y() <= m_y <= self.stop_button.winfo_y() + self.stop_button.height():

        self.setFocus()
        self.stop_gyrate = True
        try:
            artist, title, info, session, paused = asyncio.run(kanki.get_media_info())
            if not paused:
                kanki.pause(session)
            else:
                kanki.play(session)
        except (TypeError, AttributeError) as e:
            debug(f"{e}", COLORS.ERROR, "GUI")

        self.stop_gyrate = False

    def skip_next(self, event=None):
        self.setFocus()
        try:
            artist, title, info, session, paused = asyncio.run(kanki.get_media_info())
            kanki.next_s(session)
        except (TypeError, AttributeError) as e:
            debug(f"{e}", COLORS.ERROR, "GUI")

    def skip_previous(self, event=None):
        self.setFocus()
        try:
            artist, title, info, session, paused = asyncio.run(kanki.get_media_info())
            kanki.previous(session)
        except (TypeError, AttributeError) as e:
            debug(f"{e}", COLORS.ERROR, "GUI")

    def check_pause(self):
        while True:
            with open(f"{LOCAL_PATH}\\paused.txt", "r") as f:
                status = f.read()
                if status == "paused" and not self.paused.get():
                    self.paused.set(True)
                    self.pause_signal.emit(self.paused.get())
                elif status == "play" and self.paused.get():
                    self.paused.set(False)
                    self.pause_signal.emit(self.paused.get())
            # print(self.toolbar)
            # print("Label geometry:", self.icon_label.geometry())
            # print("Label size hint:", self.icon_label.sizeHint())
            # print("Under mouse:", self.icon_label.underMouse())
            # widget = self.app.widgetAt(QCursor.pos())
            # print("Widget under cursor:", widget)
            # print("Widget Class:", widget.__class__.__name__)
            # print("Label object:", self.icon_label)
            # print("Match:", widget == self.icon_label)
            time.sleep(0.01)

    def gyrating(self):
        def accurate_delay(delay):
            """ Function to provide accurate time delay in millisecond"""
            winmm = ctypes.windll.winmm
            winmm.timeBeginPeriod(1)
            time.sleep(delay / 1000)
            winmm.timeEndPeriod(1)

        times = 0
        while True:
            if self.stop_gyrate:
                continue
            if not self.paused.get():
                icon = IMG_CACHE[times]
                # x = self.icon_label.width() // 2
                # self.icon_label.delete("all")
                # self.icon_label.create_image((x, x), image=icon)
                self.icon_label.setPixmap(icon)
                self.icon_label.repaint()
                times += 1
                if times > 599:
                    times = 0

            if self.restart:
                if times > 300:
                    gap = max(round((599 - times) / 60), 1)
                    while times <= 599:
                        icon = IMG_CACHE[times]
                        self.icon_label.setPixmap(icon)
                        self.icon_label.repaint()
                        times += gap
                        accurate_delay(8)
                else:
                    gap = max(round(times / 60), 1)
                    while times >= 0:
                        icon = IMG_CACHE[times]
                        self.icon_label.setPixmap(icon)
                        self.icon_label.repaint()
                        times -= gap
                        accurate_delay(8)
                times = 0
                icon = IMG_CACHE[times]
                self.icon_label.setPixmap(icon)
                self.icon_label.repaint()
                self.restart = False
            accurate_delay(16)

    def winfo_screenwidth(self, event=None):
        return winapi.GetSystemMetrics(0)

    def winfo_screenheight(self, event=None):
        return winapi.GetSystemMetrics(1)


class ConfigurateWindow(Window):
    def __init__(self, master=None):
        Window.__init__(self, themename="darkly2")
        self.withdraw()
        self._master = master
        self.protocol("WM_DELETE_WINDOW", self.disappear)
        windowInitTk(self, 400, 0, False, lang.LANG["main.title"], "assets\\music_icon.ico")
        self.icon = Image.open("assets\\music_icon.png")
        self.cross = ImageTk.PhotoImage(Image.open("assets\\cross.png").resize((zoom(16), zoom(16))), master=self)
        self.ti_icon = ImageTk.PhotoImage(self.icon.resize((zoom(16), zoom(16))), master=self)
        self.ti_icon_la = ImageTk.PhotoImage(self.icon.resize((zoom(150), zoom(150))), master=self)
        self.thanks_tk = ImageTk.PhotoImage(Image.open("assets\\07222024_2.png").resize((zoom(100), zoom(100))),
                                            master=self)
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
        self.ui_lang_tip = Label(self.ui_lang_frame, text=lang.LANG["config.lang"] + "*", style="normal.TLabel")
        langs = list(LANG_DICT.keys())
        # print(langs)
        self.ui_lang_box = Combobox(self.ui_lang_frame, state="readonly", values=langs)
        self.ui_lang_box.bind("<<ComboboxSelected>>", self.change_lang)
        self.ui_lang_box.bind("<FocusOut>", self.on_combobox_close)
        self.ui_lang_box.bind("<Button-1>", self.on_combobox_open)
        self.ui_lang_box.current(langs.index(lang.LANG["language_name"]))

        self.flip_frame = Frame(self.inter_frame)
        self.flip_bool = BooleanVar(self)
        self.album_bool = BooleanVar(self)
        self.flip_bool.set(True) if CONFIG["CONFIG"]["flip"] == "true" else self.flip_bool.set(False)
        self.album_bool.set(True) if CONFIG["CONFIG"]["album"] == "true" else self.album_bool.set(False)
        self.flip_chk = Checkbutton(self.flip_frame, style="success.Roundtoggle.Toolbutton", command=self.set_flip,
                                    text=lang.LANG["config.interface.flip"], variable=self.flip_bool)

        self.album_chk = Checkbutton(self.flip_frame, style="success.Roundtoggle.Toolbutton", command=self.set_album,
                                     text=lang.LANG["config.interface.album"], variable=self.album_bool)

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
        self.flip_frame.place(x=zoom(0), y=zoom(0), width=zoom(200), height=zoom(50))
        self.flip_chk.place(x=zoom(0), y=zoom(0), width=zoom(150), height=zoom(25))
        self.album_chk.place(x=zoom(0), y=zoom(25), width=zoom(150), height=zoom(25))
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

    def on_combobox_open(self, event=None):
        # self.attributes("-topmost", False)
        pass

    def on_combobox_close(self, event=None):
        # self.attributes("-topmost", True)
        pass

    def topMost(self):
        while self.on_run:
            try:
                self.attributes('-topmost', True)
                self.lift()
                time.sleep(0.1)
            except tk.TclError as e:
                debug(f"tk.TclError: {e}", COLORS.ERROR, "GUI")

    def set_flip(self, event=None):
        p_state = self.flip_bool.get()
        if p_state:
            self._master.flipping_text = True
            self.flip_chk.update()
            CONFIG["CONFIG"]["flip"] = "true"
        else:
            self._master.flipping_text = False
            self.flip_chk.update()
            CONFIG["CONFIG"]["flip"] = "false"

        with open(f"{LOCAL_PATH}\\config.ini", "w") as config_f:
            CONFIG.write(config_f)

    def set_album(self, event=None):
        p_state = self.album_bool.get()
        if p_state:
            self.album_chk.update()
            CONFIG["CONFIG"]["album"] = "true"
        else:
            self.album_chk.update()
            CONFIG["CONFIG"]["album"] = "false"

        with open(f"{LOCAL_PATH}\\config.ini", "w") as config_f:
            CONFIG.write(config_f)

    def change_lang(self, event=None):
        global lang
        self.on_combobox_close()
        language = self.ui_lang_box.get()
        CONFIG["CONFIG"]["lang"] = LANG_DICT[language]
        with open(f"{LOCAL_PATH}\\config.ini", "w") as config_f:
            CONFIG.write(config_f)
        lang = importlib.reload(lang2)
        lang.load_lang()
        self.update()

    def appear(self):
        self.on_run = True
        # Thread(target=self.topMost).start()
        self.grab_set()
        middleTk(self, zoom(400), 0)
        self.configure(width=zoom(400), height=0)
        winX = zoom(400)
        winY = zoom(525)
        maxX = winapi.GetSystemMetrics(0)
        maxY = winapi.GetSystemMetrics(1)
        x = maxX // 2 - winX // 2
        y = maxY // 2 - winY // 2
        self.deiconify()
        self.ui_lang_box.lift()
        widget.move_to(self, x, y, zoom(400), zoom(525), fps=FPS, is_windows=True)
        self.attributes("-topmost", True)

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
        widget.move_to(self, x, maxY + 1, zoom(400), zoom(0), fps=FPS, is_windows=True)


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
        self.master.delete_signal.emit()

    def setting_window(self):
        global IN_CONFIG
        if not IN_CONFIG:
            IN_CONFIG = True
            self.master.config_win.appear()
        else:
            pass

    def show_window(self):
        if not self.show:
            x = winapi.GetSystemMetrics(0) - zoom(300)
            y = winapi.GetSystemMetrics(1) - zoom(300) + zoom(100) - zoom(40)
            self.master.show()
            self.master.fade_in(1.0, 0.25, FPS)
            widget.move_to(self.master, fps=FPS, x=x, y=y, width=zoom(300), height=zoom(300), is_windows=True)
            self.show = True
        else:
            self.master.fade_out()
            widget.withdraw(self.master, fps=FPS, is_windows=True, direction="e")
            time.sleep(0.5)
            self.master.hide()
            self.show = False


class ClickableLabel(qt.QLabel):
    clicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)


class MyComboBox(qt.QComboBox):
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # Call your handler
        self.parent().on_combobox_close(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Call your handler
        self.parent().on_combobox_open(event)


class WorkerThread(QThread):
    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.target(*self.args, **self.kwargs)

    start = run


class GyrateWorker(QThread):
    update_icon = pyqtSignal(object)  # Signal to send new pixmap to main thread

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stop_gyrate = False
        self.paused = False
        self.restart = False

    def accurate_delay(self, delay_ms):
        winmm = ctypes.windll.winmm
        winmm.timeBeginPeriod(1)
        time.sleep(delay_ms / 1000)
        winmm.timeEndPeriod(1)

    def run(self):
        times = 0
        while True:
            if self.stop_gyrate:
                self.accurate_delay(16)
                continue
            if not self.paused:
                icon = IMG_CACHE[times]
                # Instead of setting pixmap here, emit signal:
                self.update_icon.emit(icon)
                times += 1
                if times > 599:
                    times = 0

            if self.restart:
                if times > 300:
                    gap = max(round((599 - times) / 60), 1)
                    while times <= 599:
                        icon = IMG_CACHE[times]
                        self.update_icon.emit(icon)
                        times += gap
                        self.accurate_delay(8)
                else:
                    gap = max(round(times / 60), 1)
                    while times >= 0:
                        icon = IMG_CACHE[times]
                        self.update_icon.emit(icon)
                        times -= gap
                        self.accurate_delay(8)
                times = 0
                icon = IMG_CACHE[times]
                self.update_icon.emit(icon)
                self.restart = False

            self.accurate_delay(16)


class ScrollingFrame(qt.QFrame):
    def __init__(self, parent=None, master=None, type=1):
        super().__init__(parent)
        self.label_1 = None
        self.label_2 = None
        self.length = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.tick = 0
        self.pos = 0
        self.idle = False
        self.master = master
        self.type = type

    def start(self, label_1, label_2, length):
        self.label_1 = label_1
        self.label_2 = label_2
        self.length = length
        self.timer.start(1000 // 120)

    def reset(self, new_length):
        self.length = new_length
        self.tick = 0
        self.pos = 0

    def update_frame(self):
        if self.type == 1:
            self.length = self.master.length
        else:
            self.length = self.master.length2
        if self.master.stop_scrolling:
            # debug("ScrollingFrame Ticking stopped")
            return 0
        # debug(str(self.length)+" "+str(zoom(225)))
        if self.length > zoom(225):
            # debug("ScrollingFrame Ticking")

            if self.tick >= 840:
                self.tick = 0
                self.idle = False
            if self.idle:
                self.tick += 1
                return 0
            self.label_1.setGeometry(zoom(0) - self.pos, zoom(0), self.length, zoom(37))
            self.label_2.setGeometry(zoom(100) + self.length - self.pos, zoom(0), self.length, zoom(37))
            self.pos += 1
            if self.pos >= self.length + zoom(100):
                self.label_1.setGeometry(zoom(0), zoom(0), self.length, zoom(37))
                self.label_2.setGeometry(zoom(100) + self.length, zoom(0), self.length, zoom(37))
                self.idle = True
                self.tick = 0
                self.pos = 0
        else:
            pass


def check_japanese(string):
    for i in string:
        if i in J_LIST:
            return True
    return False


def pil_image_to_qpixmap(pil_image: Image.Image):
    # Convert PIL Image to bytes buffer in PNG format
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)

    # Load QImage from bytes
    qimage = QImage()
    qimage.loadFromData(buffer.read())

    # Convert QImage to QPixmap
    return QPixmap.fromImage(qimage)


def windowInit(master, width: int, height: int, canResize: bool, title: str, icon: str):
    master.resize(zoom(width), zoom(height))
    if not canResize:
        master.setFixedSize(zoom(width), zoom(height))
    master.setWindowTitle(title)
    master.setWindowIcon(QIcon(icon))


def windowInitTk(master, width: int, height: int, canResize: bool, title: str, icon: str):
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
        winX = master.width()
        winY = master.height()
    x = maxX // 2 - winX // 2
    y = maxY // 2 - winY // 2
    master.move(x, y)


def middleTk(master, width=None, height=None):
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


def make_window_transparent(root, alpha=220, click_through=False):
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_TRANSPARENT = 0x00000020
    LWA_COLORKEY = 0x00000001
    LWA_ALPHA = 0x00000002

    # Get Win32 API functions
    SetWindowLong = ctypes.windll.user32.SetWindowLongW
    GetWindowLong = ctypes.windll.user32.GetWindowLongW
    SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes
    hwnd = root.winfo_id()
    ex_style = GetWindowLong(hwnd, GWL_EXSTYLE)
    ex_style |= WS_EX_LAYERED
    if click_through:
        ex_style |= WS_EX_TRANSPARENT
    SetWindowLong(hwnd, GWL_EXSTYLE, ex_style)

    # Set the transparency: alpha 0-255, lower is more transparent
    SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)


def is_windows():
    if os.name == "nt":
        return True
    return False


def zoom(data) -> int:
    return round(data * ZOOM)


def restart():
    debug("Hard restarting via command line...", COLORS.WARNING, "MAIN")
    try:
        subprocess.Popen([f"{RUN_PATH}\\Python310\\pythonw.exe", f"{RUN_PATH}\\main.pyw"])
        os._exit(114514)  # Immediate process exit, no cleanup
    except Exception as e:
        exc_cont = f"{create_log_time()}"
        LOGGER.critical(str(e), exc_cont + " [MAIN]")
        debug(f"Restart failed: {e}", COLORS.ERROR, "MAIN")
