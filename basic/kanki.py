import asyncio
import os
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSession as MediaControl
from winsdk.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from PIL import Image
import time


async def get_media_info():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    # if current_session and ("ZuneMusic" in current_session.source_app_user_model_id or
    #                         "Spotify" in current_session.source_app_user_model_id):
    # print(current_session.source_app_user_model_id)
    if current_session and ("ZuneMusic" in current_session.source_app_user_model_id or
                            "Spotify" in current_session.source_app_user_model_id or
                            "Musbox" in current_session.source_app_user_model_id or
                            "122165AE053F" in current_session.source_app_user_model_id):
        info = await current_session.try_get_media_properties_async()
        paused = get_paused(current_session)
        return info.artist, info.title, info, current_session, paused


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
    with open("basic\\paused.txt", "w") as f:
        f.write("paused")


def play(session):
    session.try_play_async()
    with open("basic\\paused.txt", "w") as f:
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
        with open("basic\\paused.txt", "rb") as f:
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
            # artist, title, info, session, paused = asyncio.run(get_media_info())
            # asyncio.wait(session)
            current_session = sessions.get_current_session()
            # print(current_session.source_app_user_model_id)
            # if current_session and ("ZuneMusic" in current_session.source_app_user_model_id or
            #                         "Spotify" in current_session.source_app_user_model_id or
            #                         "Musbox" in current_session.source_app_user_model_id or
            #                         "122165AE053F" in current_session.source_app_user_model_id):
            info = await current_session.try_get_media_properties_async()
            paused = get_paused(current_session)
            artist = info.artist
            title = info.title
            info = info
            session = current_session
            # else:
            #     continue
            if artist == "":
                artist = info.album_artist
            with open("basic\\paused.txt", "w") as f:
                if paused:
                    f.write("paused")
                else:
                    f.write("play")
            if _ar != artist or _ti != title:
                _ti = title
                _ar = artist
                with open("basic\\artist.txt", "wb") as f:
                    f.write(artist.encode("utf-8"))

                with open("basic\\title.txt", "wb") as f:
                    f.write(title.encode("utf-8"))
        except (TypeError, PermissionError, OSError, AttributeError):
            pass
        # print(f"Time Usage ({times}): {time.time() - start}s")
        time.sleep(0.1)
        times += 1


def run():
    with open("basic\\paused.txt", "wb") as _f:
        _f.write("paused".encode("utf-8"))

    if not os.path.exists("basic\\artist.txt"):
        with open("basic\\artist.txt", "w") as _f:
            _f.write("Not Playing")
    if not os.path.exists("basic\\title.txt"):
        with open("basic\\title.txt", "w") as _f:
            _f.write("Not Playing")
    # asyncio.run(control_main())
    asyncio.run(main())


if __name__ == '__main__':
    run()
