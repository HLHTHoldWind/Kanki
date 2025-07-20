import basic.libimport
from PyQt5.QtWidgets import QApplication

basic.libimport.set_import_lib()
import asyncio
import time
import basic.kanki as kanki
import basic.gui as gui
from basic.constants import *
from basic.updater import check_version
from threading import Thread


def get_info(root):
    _ti = ""
    _ar = ""
    while root.working:
        with open(f"{LOCAL_PATH}\\artist.txt", "rb") as f:
            artist = f.read().decode("utf-8")

        with open(f"{LOCAL_PATH}\\title.txt", "rb") as f:
            title = f.read().decode("utf-8")
        if _ar != artist or _ti != title:
            _ti = title
            _ar = artist
            root.update_infos_signal.emit(title, artist)

        time.sleep(0.1)


def main():
    try:
        import sys
        import traceback

        def my_exception_hook(exctype, value, tb):
            debug("Uncaught exception:" + ''.join(traceback.format_exception(exctype, value, tb)),
                  COLORS.ERROR, "CORE")
            sys.__excepthook__(exctype, value, tb)

        sys.excepthook = my_exception_hook
        start_time = time.time()
        flip = True if CONFIG["CONFIG"]["flip"] == "true" else False
        fps = int(CONFIG["CONFIG"]["fps"])
        Thread(target=kanki.run).start()
        app = QApplication([])
        root = gui.MainWindow(flipping=flip, fps=fps, app=app)
        root.item_configurate()
        root.animate_binding()
        root.display_all(get_info)
        debug(f"Starting took {time.time() - start_time} s", COLORS.SUCCESS, "MAIN")
        app.exec_()
        root.config_win.mainloop()
    except Exception as e:
        exc_cont = f"{create_log_time()}"
        LOGGER.critical(str(e), exc_cont + " [MAIN_START]")
        debug(str(e), COLORS.ERROR, "MAIN_START")
