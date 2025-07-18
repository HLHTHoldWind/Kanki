import requests
import threading
import subprocess
from basic.constants import *


def stop_all_known_threads():
    for thread in threading.enumerate():
        if thread is threading.main_thread():
            continue
        if hasattr(thread, "stop"):
            thread.stop()
        elif hasattr(thread, "running"):
            thread.running = False


def restart():
    debug("Hard restarting via command line...", COLORS.WARNING, "MAIN")
    try:
        subprocess.Popen([f"{RUN_PATH}\\system\\Python\\pythonw.exe", f"{RUN_PATH}\\main.py"])
        os._exit(114514)  # Immediate process exit, no cleanup
    except Exception as e:
        exc_cont = f"{create_log_time()}"
        LOGGER.critical(str(e), exc_cont + " [MAIN]")
        debug(f"Restart failed: {e}", COLORS.ERROR, "MAIN")


def version_formatter(version: int):
    if 100 <= version <= 999:
        # Convert the number to a string and format it as x.x.x
        formatted = f"{str(version)[0]}.{str(version)[1]}.{str(version)[2]}"
        return formatted
    else:
        raise ValueError("The number must be a 3-digit integer.")


def check_version():
    if os.path.exists(f"{RUN_PATH}\\donotcheckupdate.txt"):
        return False
    try:
        debug("Checking for updates...", COLORS.YELLOW, "UPDATER")
        version = int(requests.get(f'{ARCHIVE_HOST}/archives/kanki_version.txt').text)
        if version > MAIN_VERSION:
            debug(f"Found newer version: {version_formatter(version)}", COLORS.WARNING, "UPDATER")
            return True
        else:
            return False
    except:
        debug("Failed to check updates", COLORS.WARNING, "UPDATER")
        return False
