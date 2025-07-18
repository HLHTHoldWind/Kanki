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
    while True:
        with open(f"{LOCAL_PATH}\\artist.txt", "rb") as f:
            artist = f.read().decode("utf-8")

        with open(f"{LOCAL_PATH}\\title.txt", "rb") as f:
            title = f.read().decode("utf-8")
        if _ar != artist or _ti != title:
            _ti = title
            _ar = artist
            root.update_infos(title, artist)

        time.sleep(0.1)


def main():
    try:
        start_time = time.time()
        flip = True if CONFIG["CONFIG"]["flip"] == "true" else False
        fps = int(CONFIG["CONFIG"]["fps"])
        Thread(target=kanki.run).start()
        root = gui.MainWindow(flipping=flip, fps=fps)
        Thread(target=get_info, args=(root,)).start()
        debug(f"Starting took {time.time() - start_time} s", COLORS.SUCCESS, "MAIN")
        root.mainloop()
    except Exception as e:
        exc_cont = f"{create_log_time()}"
        LOGGER.critical(str(e), exc_cont + " [MAIN_START]")
        debug(str(e), COLORS.ERROR, "MAIN_START")
