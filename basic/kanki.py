import win32gui
import requests
from io import BytesIO
import asyncio
import os
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSession as MediaControl
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from PIL import Image
from basic.constants import *
import time
import psutil


async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    # if current_session and ("ZuneMusic" in current_session.source_app_user_model_id or
    #                         "Spotify" in current_session.source_app_user_model_id):
    # print(current_session.source_app_user_model_id)
    try:
        info = await current_session.try_get_media_properties_async()
        # print(dir(info))
        paused = get_paused(current_session)
        return info.artist, info.title, info, current_session, paused
    except AttributeError as e:
        debug(f"{e}", COLORS.ERROR, "CORE")
        return "", "", None, current_session, True


async def get_album_cover_image(info):
    if info.thumbnail is None:
        return None

    # Open thumbnail stream async
    stream = await info.thumbnail.open_read_async()

    # Read stream into buffer
    size = stream.size
    buffer = Buffer(size)
    await stream.read_async(buffer, size, InputStreamOptions.NONE)

    # Use DataReader to get bytes from Buffer
    data_reader = DataReader.from_buffer(buffer)
    bytes_array = bytearray(size)
    data_reader.read_bytes(bytes_array)

    # Convert to PIL Image
    image = Image.open(BytesIO(bytes_array))
    return image


async def read_stream_into_buffer(stream_ref, buffer):
    readable_stream = await stream_ref.open_read_async()
    readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)


async def get_session():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session and ("ZuneMusic" in current_session.source_app_user_model_id or
                            "Spotify" in current_session.source_app_user_model_id or
                            "Musbox" in current_session.source_app_user_model_id or
                            "122165AE053F" in current_session.source_app_user_model_id):
        return current_session


def pause(session):
    session.try_pause_async()
    with open(f"{LOCAL_PATH}\\paused.txt", "w") as f:
        f.write("paused")


def play(session):
    session.try_play_async()
    with open(f"{LOCAL_PATH}\\paused.txt", "w") as f:
        f.write("play")


def previous(session):
    session.try_skip_previous_async()


def next_s(session):
    session.try_skip_next_async()


def get_paused(session):
    data = session.get_playback_info().playback_status
    if int(data) != 4:
        return True
    else:
        return False


def get_tick(session):
    time_info = session.get_timeline_properties()


async def control_main():
    while True:
        with open(f"{LOCAL_PATH}\\paused.txt", "rb") as f:
            if f.read().decode("utf-8") == "paused":
                session = await get_session()
                paused = get_paused(session)
                if not paused:
                    pause(session)
            elif f.read().decode("utf-8") == "unpause":
                session = await get_session()
                paused = get_paused(session)
                if paused:
                    pause(session)
        time.sleep(0.01)


async def main():
    _ti = ""
    _ar = ""
    times = 0
    sessions = await MediaManager.request_async()
    while True:
        start = time.time()
        try:
            net = False
            if not is_netease_running():
                current_session = sessions.get_current_session()
                info = await current_session.try_get_media_properties_async()

                paused = get_paused(current_session)
                artist = info.artist
                title = info.title
                info = info

                session = current_session
                if artist == "":
                    artist = info.album_artist
                with open(f"{LOCAL_PATH}\\paused.txt", "w") as f:
                    if paused:
                        f.write("paused")
                    else:
                        f.write("play")
                if _ar != artist or _ti != title:
                    for i in range(3):
                        try:
                            image = await get_album_cover_image(info)
                            image.save(f"{LOCAL_PATH}\\cover_temp.png")
                            os.replace(f"{LOCAL_PATH}\\cover_temp.png", f"{LOCAL_PATH}\\cover.png")
                            break
                        except Exception as eee:
                            debug(f"{eee}", COLORS.ERROR, "CORE")
                            if os.path.exists(f"{LOCAL_PATH}\\cover.png"):
                                os.remove(f"{LOCAL_PATH}\\cover.png")
                            await asyncio.sleep(0.1)
                    _ti = title
                    _ar = artist
                    with open(f"{LOCAL_PATH}\\artist.txt", "wb") as f:
                        f.write(artist.encode("utf-8"))

                    with open(f"{LOCAL_PATH}\\title.txt", "wb") as f:
                        f.write(title.encode("utf-8"))
            else:
                raise TypeError("Netease")
        except (TypeError, PermissionError, OSError, AttributeError) as e:
            # print(e)
            net = False
            try:
                if is_netease_running():
                    title = get_netease_now_playing()
                    data = parse_netease_title(title)
                    title, artist = data[0:2]
                    # print(title, artist)
                    if _ar != artist or _ti != title:
                        metadata = search_netease_song(artist, title)
                        # if metadata:
                        url = get_album_info(metadata["al_id"])
                        image = fetch_album_art(url)
                        try:
                            image.save(f"{LOCAL_PATH}\\cover_temp.png")
                            os.replace(f"{LOCAL_PATH}\\cover_temp.png", f"{LOCAL_PATH}\\cover.png")
                        except Exception as eee:
                            debug(f"{eee}", COLORS.ERROR, "CORE")
                            net = True
                            if os.path.exists(f"{LOCAL_PATH}\\cover.png"):
                                os.remove(f"{LOCAL_PATH}\\cover.png")

                        _ti = title
                        _ar = artist
                        with open(f"{LOCAL_PATH}\\artist.txt", "wb") as f:
                            f.write(artist.encode("utf-8"))

                        with open(f"{LOCAL_PATH}\\title.txt", "wb") as f:
                            f.write(title.encode("utf-8"))
                    with open(f"{LOCAL_PATH}\\paused.txt", "w") as f:
                        f.write("play")

            except Exception as ee:
                net = True
                debug(f"Failed to get Netease info: {ee}", COLORS.ERROR, "CORE")

        if net:
            await asyncio.sleep(0.5)
        else:
            await asyncio.sleep(0.1)
        # print(f"Time Usage ({times}): {time.time() - start}s")
        times += 1


def list_all_windows():
    windows = []

    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            try:
                title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                if title:
                    result.append((hwnd, title, class_name))
            except Exception:
                pass

    win32gui.EnumWindows(enum_handler, windows)
    return windows


def get_netease_now_playing():
    titles = []

    def enum_handler(hwnd, result):
        try:
            if win32gui.IsWindowVisible(hwnd):
                class_name = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd)
                if class_name == "OrpheusBrowserHost" and title:
                    result.append(title)
        except Exception:
            pass

    win32gui.EnumWindows(enum_handler, titles)
    if titles:
        return titles[0]
    else:
        return None


def parse_netease_title(title):
    parts = title.split(" - ")
    if len(parts) >= 2:
        song = parts[0]
        artist_or_album = " - ".join(parts[1:])
        return song, artist_or_album
    else:
        return title, None


def is_netease_running():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'cloudmusic' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def search_netease_song(artist_or_album, song):
    query = f"{artist_or_album} {song}"
    resp = requests.get(
        "https://music.163.com/api/search/get",
        params={"s": query, "type": 1, "limit": 1}
    )
    data = resp.json()
    songs = data.get("result", {}).get("songs", [])
    if songs:
        track = songs[0]
        # print(track)
        return {
            "track_id": track["id"],
            "title": track["name"],
            "artist": ", ".join(ar["name"] for ar in track["artists"]),
            "album": track["album"]["name"],
            "al_id": track["album"]["id"]
        }
    return None


def get_album_info(album_id):
    url = f"https://music.163.com/api/album/{album_id}"
    headers = {"Referer": "https://music.163.com/"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        album_data = resp.json()
        pic_url = album_data.get('album', {}).get('picUrl')
        return pic_url
    return None


def fetch_album_art(url):
    resp = requests.get(url)
    img = Image.open(BytesIO(resp.content))
    return img


def run():
    with open(f"{LOCAL_PATH}\\paused.txt", "wb") as _f:
        _f.write("paused".encode("utf-8"))

    if not os.path.exists(f"{LOCAL_PATH}\\artist.txt"):
        with open(f"{LOCAL_PATH}\\artist.txt", "w") as _f:
            _f.write("Not Playing")
    if not os.path.exists(f"{LOCAL_PATH}\\title.txt"):
        with open(f"{LOCAL_PATH}\\title.txt", "w") as _f:
            _f.write("Not Playing")
    # asyncio.run(control_main())
    asyncio.run(main())


if __name__ == '__main__':
    run()
