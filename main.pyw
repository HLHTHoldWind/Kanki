import asyncio
import time

import basic.kanki as kanki
import basic.gui as gui
from basic.constants import *
from threading import Thread


def get_info(root):
    _ti = ""
    _ar = ""
    while True:
        with open("basic\\artist.txt", "rb") as f:
            artist = f.read().decode("utf-8")

        with open("basic\\title.txt", "rb") as f:
            title = f.read().decode("utf-8")
        if _ar != artist or _ti != title:
            _ti = title
            _ar = artist
            root.update_infos(title, artist)

        time.sleep(0.1)


def main():
    flip = True if CONFIG["CONFIG"]["flip"] == "true" else False
    fps = int(CONFIG["CONFIG"]["fps"])
    Thread(target=kanki.run).start()
    root = gui.MainWindow(flipping=flip, fps=fps)
    Thread(target=get_info, args=(root,)).start()
    root.mainloop()


if __name__ == '__main__':
    main()
