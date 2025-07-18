import random
from ttkbootstrap import *
import time
import threading
import math
import win32api
import pygame
from basic.constants import *
from basic.movement import *

# moving functions
SAMPLE_FUNCTION = ("function definition: def", "x_start: num", "x_end: num", "y_offset: num")
COSINE = (math.cos, math.pi, math.pi * 2, 1)
CUBIC = (ease_in_out_cubic_scaled, 0, 1, 0)
SQUD = (ease_out_quad, 0, 1, 0)
STEP = (smoothstep, 0, 1, 0)
WINDOWS10 = (windows10_cubic_bezier, 0, 1, 0)
WINDOWS11 = (windows11_cubic_bezier, 0, 1, 0)
GOOGLE_IN = (g_moving_in, 0, 1, 0)
GOOGLE_OUT = (g_moving_out, 0, 1, 0)
CHROME = (g_default, 0, 1, 0)
WINDOWS11_BOUNCE = (windows11_bounce_bezier, 0, 1, 0)
ELASTIC_OUT = (ease_out_elastic_gentle, 0, 1, 0)
ELASTIC_IN_OUT = (ease_in_out_elastic, 0, 1, 0)
BOUNCE = (ease_in_out_cubic_bounce, 0, 1, 0)
LINEAR = (lambda x: x, 0, 1, 0)

pygame.init()

M_FUNC = {
    "COSINE": COSINE,
    "CUBIC": CUBIC,
    "SQUD": SQUD,
    "WINDOWS10": WINDOWS10,
    "WINDOWS11": WINDOWS11,
    "GOOGLE": [GOOGLE_IN, GOOGLE_OUT],
    "CHROME": CHROME,
    "BOUNCE": BOUNCE,
    "LINEAR": LINEAR
}

# definitions
def noFun(*event):
    return event


def moving(widget, x=None, y=None, width=None, height=None, delay=0.5, fps=60, start_delay=0.0, advance_delay=None,
           parameters=None, after_functions=None, is_window=False):
    if start_delay:
        accurate_delay(round(start_delay*1000))
    if is_window:
        function = widget.geometry
    else:
        function = widget.place

    original_x = widget.winfo_x()
    original_y = widget.winfo_y()
    original_width = widget.winfo_width()
    original_height = widget.winfo_height()

    if x is None:
        x = original_x
    if y is None:
        y = original_y
    if width is None:
        width = original_width
    if height is None:
        height = original_height

    if "appear" in parameters:
        _x = x + width / 2
        _y = y + height / 2
        _width = 0
        _height = 0
        if "center" in parameters:
            _x = x + width / 2
            _y = y + height / 2
            _width = 0
            _height = 0
        if "ns" in parameters or "sn" in parameters:
            _x = x
            _y = y + height / 2
            _width = width
            _height = 0
        if "we" in parameters or "ew" in parameters:
            _x = x + width / 2
            _y = y
            _width = 0
            _height = height
        if "n" in parameters:
            _x = x
            _y = y
            _width = width
            _height = 0
        if "s" in parameters:
            _x = x
            _y = y + width
            _width = width
            _height = 0
        if "e" in parameters:
            _x = x + width
            _y = y
            _width = 0
            _height = height
        if "w" in parameters:
            _x = x
            _y = y
            _width = 0
            _height = height

        function(x=round(_x), y=round(_y), width=round(_width), height=round(_height)) if not is_window else \
            function(f"{round(_width)}x{round(_height)}+{round(_x)}+{round(_y)}")

        if x == original_x:
            x = _x
        if y == original_y:
            y = _y
        if width == original_width:
            width = _width
        if height == original_height:
            height = _height

        original_x = _x
        original_y = _y
        original_width = _width
        original_height = _height

    if delay < 0:
        raise ValueError(f'Function "move_to()": parameter "delay" must >= 0.')

    if fps <= 0:
        raise ValueError(f'Function "move_to()": parameter "fps" must > 0.')

    direction_x = 1 if x >= original_x else -1
    direction_y = 1 if y >= original_y else -1
    direction_width = 1 if width >= original_width else -1
    direction_height = 1 if height >= original_height else -1

    length_x = abs(original_x - x)
    length_y = abs(original_y - y)
    length_width = abs(original_width - width)
    length_height = abs(original_height - height)

    fps_delay = get_frame_rate_delay(fps)

    FUNC = M_FUNC["GOOGLE"]
    if isinstance(FUNC, list):
        if direction_width == -1 or direction_height == -1:
            FUNC = FUNC[1]
        else:
            FUNC = FUNC[0]

    if isinstance(advance_delay, dict):
        velocity_x = get_func_velocities(length_x, advance_delay["x"], fps_delay, FUNC)
        velocity_y = get_func_velocities(length_y, advance_delay["y"], fps_delay, FUNC)
        velocity_width = get_func_velocities(length_width, advance_delay["width"], fps_delay, FUNC)
        velocity_height = get_func_velocities(length_height, advance_delay["height"], fps_delay, FUNC)

    else:
        velocity_x = get_func_velocities(length_x, delay, fps_delay, FUNC)
        velocity_y = get_func_velocities(length_y, delay, fps_delay, FUNC)
        velocity_width = get_func_velocities(length_width, delay, fps_delay, FUNC)
        velocity_height = get_func_velocities(length_height, delay, fps_delay, FUNC)

    total_frames = round(delay / fps_delay)
    start_time = time.time()
    times = 1
    for i in range(total_frames):
        start = time.time()
        _x = original_x + velocity_x[min(times - 1, len(velocity_x) - 1)] * direction_x
        _y = original_y + velocity_y[min(times - 1, len(velocity_y) - 1)] * direction_y
        _width = original_width + velocity_width[min(times - 1, len(velocity_width) - 1)] * direction_width
        _height = original_height + velocity_height[min(times - 1, len(velocity_height) - 1)] * direction_height
        function(x=round(_x), y=round(_y), width=round(_width), height=round(_height)) if not is_window else \
            function(f"{round(_width)}x{round(_height)}+{round(_x)}+{round(_y)}")
        end = time.time()

        if end - start <= fps_delay and times >= (end - start_time) / fps_delay:
            accurate_delay(int(round(fps_delay - (end - start), 3)*1000))

        times += 1
    function(x=x, y=y, width=width, height=height) if not is_window else \
        function(f"{round(width)}x{round(height)}+{round(x)}+{round(y)}")

    for i in after_functions:
        i()


def move_to(widget, x=None, y=None, width=None, height=None, delay=0.5, fps=60, start_delay=0.0, advance_delay=None,
            parameters=None, after_functions=None, is_windows=False):
    if after_functions is None:
        after_functions = [noFun]
    if parameters is None:
        parameters = []
    if advance_delay is None:
        advance_delay = []

    move_thread = threading.Thread(target=moving, args=[widget, x, y, width, height,
                                                        delay, fps, start_delay, advance_delay,
                                                        parameters, after_functions, is_windows])
    move_thread.start()
    return move_thread


def withdraw(widget, direction="center", delay=0.5, fps=60, start_delay=0.0, advance_delay=None, is_windows=False, after_funtions=None):
    original_x = widget.winfo_x()
    original_y = widget.winfo_y()
    original_width = widget.winfo_width()
    original_height = widget.winfo_height()

    x = original_x + original_width / 2
    y = original_y + original_height / 2
    width = 0
    height = 0

    if direction == "center":
        x = original_x + original_width / 2
        y = original_y + original_height / 2
        width = 0
        height = 0
    if direction == "ns" or direction == "sn":
        x = original_x
        y = original_y + original_height / 2
        width = original_width
        height = 0
    if direction == "we" or direction == "ew":
        x = original_x + original_width / 2
        y = original_y
        width = 0
        height = original_height
    if direction == "n":
        x = original_x
        y = original_y
        width = original_width
        height = 0
    if direction == "s":
        x = original_x
        y = original_y + original_height
        width = original_width
        height = 0
    if direction == "e":
        x = original_x + original_width
        y = original_y
        width = 0
        height = original_height
    if direction == "w":
        x = original_x
        y = original_y
        width = 0
        height = original_height

    withdraw_thread = move_to(widget=widget, x=x, y=y, width=width, height=height,
                              delay=delay, fps=fps, start_delay=start_delay, advance_delay=advance_delay,
                              after_functions=after_funtions, is_windows=is_windows)

    return withdraw_thread


def zoom(widget, originals, ratio, delay=0.5, fps=60, start_delay=0.0, advance_delay=None):
    original_x = originals["x"]
    original_y = originals["y"]
    original_width = originals["width"]
    original_height = originals["height"]

    x = original_x + ((original_width - (original_width * ratio)) / 2)
    y = original_y + ((original_height - (original_height * ratio)) / 2)
    width = original_width * ratio
    height = original_height * ratio

    zoom_thread = move_to(widget, x=x, y=y, width=width, height=height,
                          delay=delay, fps=fps, start_delay=start_delay, advance_delay=advance_delay)

    return zoom_thread


def unzoom(widget, originals, delay=0.5, fps=60, start_delay=0.0, advance_delay=None):
    x = originals["x"]
    y = originals["y"]
    width = originals["width"]
    height = originals["height"]

    zoom_thread = move_to(widget, x=x, y=y, width=width, height=height,
                          delay=delay, fps=fps, start_delay=start_delay, advance_delay=advance_delay)

    return zoom_thread


def label_print(widget, string: str, during=0.25, step=True, step_delay=0.75, FPS=30):
    chars = []
    length = 0
    delay = 1 / FPS
    if step:
        wait_time = step_delay / len(string) if len(string) > 0 else 0
        wait_step = round(wait_time / delay)
    else:
        wait_step = 0

    times = 0
    for i in string:
        if i in [" ", "\n", "\r", "\b", "	"]:
            chars.append([i] * round(during / delay + round(wait_step * times)))

        elif i not in C_LIST + J_LIST + P_LIST + R_LIST:
            c_l = []
            path_l = ord(i)
            step_l = max(1.0, path_l / (during / delay + round(wait_step * times)))
            if path_l <= during / delay:
                step_l = 1
            index = 32
            while True:
                c_l.append(chr(round(index)))
                index += step_l
                if index >= path_l:
                    if i != c_l[-1]:
                        c_l.append(i)
                    break

            if len(c_l) < (during / delay) + round(wait_step * times):
                remains = ((during / delay) + round(wait_step * times)) - len(c_l)
                if int(remains) != remains:
                    remains = int(remains) + 1
                else:
                    remains = int(remains)

                for _chr in range(remains):
                    c_l.insert(0, chr(random.randint(32, 127)))
            if len(c_l) > ((during / delay) + round(wait_step * times)):
                while len(c_l) > ((during / delay) + round(wait_step * times)):
                    c_l.pop(0)

            chars.append(c_l)

            if len(c_l) > length:
                length = len(c_l)

        else:
            LIST = C_LIST
            for li in [C_LIST, J_LIST, P_LIST, R_LIST]:
                if i in li:
                    LIST = li
            c_l = []
            path_l = LIST.index(i) + 1
            step_l = max(1.0, path_l / (during / delay + round(wait_step * times)))
            if path_l <= during / delay:
                step_l = 1
            index = 0
            while True:
                c_l.append(LIST[round(index)])
                index += step_l
                if index >= path_l:
                    if i != c_l[-1]:
                        c_l.append(i)
                    break

            remains = 0
            if len(c_l) < ((during / delay) + round(wait_step * times)):
                remains = ((during / delay) + round(wait_step * times)) - len(c_l)
                if int(remains) != remains:
                    remains = int(remains) + 1
                else:
                    remains = int(remains)

                for _chr in range(remains):
                    c_l.insert(0, random.choice(LIST))
            if len(c_l) > ((during / delay) + round(wait_step * times)):
                while len(c_l) > ((during / delay) + round(wait_step * times)):
                    c_l.pop(0)
            chars.append(c_l)

            if len(c_l) > length:
                length = len(c_l)
        times += 1

    times = 0
    firstStart = time.time()
    c_content = ""
    loc = 0
    while True:
        start = time.time()
        content = ""
        temp_range = chars[loc:loc + 2]
        for i in temp_range:
            try:
                i[min(times, len(i) - 1)].encode("utf-8")
                if len(i) - 1 <= times:
                    # print(i[-1], end="", flush=False)
                    c_content += i[-1]
                    loc += 1
                else:
                    content += i[min(times, len(i) - 1)]

            except UnicodeEncodeError:
                content += chr(random.randint(32, 127))

        widget.configure(text=c_content + content)
        widget.update()
        end = time.time()

        if delay >= 0.0001:
            passed = end - start
            totalTime = end - firstStart
            if passed <= delay and times + 1 >= totalTime / delay:
                accurate_delay(max(round((delay - passed) * 1000), 0))
        times += 1
        if times == length:
            content = ""
            for i in chars:
                content += i[-1]
            widget.configure(text=content)
            break
        else:
            pass


def accurate_delay(delay):
    """ Function to provide accurate time delay in millisecond"""
    pygame.time.wait(delay)


def get_moving_velocity(length, delay, fps_delay):
    total_frames = round(delay / fps_delay)
    return length / total_frames


def get_frame_rate_delay(fps):
    return round(1 / fps, 3)


def get_func_velocities(length, delay, fps_delay, func):
    if delay == 0:
        return [length]
    function, x_start, x_end, y_offset = func

    total_frames = round(delay / fps_delay)
    func_delay = (x_end - x_start) / total_frames
    total_velocities = []

    for i in range(total_frames):
        x = x_start + func_delay * i
        ratio = (function(x) + y_offset) / (function(x_end) + y_offset)
        total_velocities.append(length * ratio)

    return total_velocities


def test():
    root = Window()
    button = Button(root, text="Testing")
    button.place(x=50, y=50, width=100, height=50)
    texts = Text(root, borderwidth=0)
    texts.insert("end", "item1\nitem2\nitem3\nitem4\nitem5\nitem6\n")
    texts.place(x=50, y=150, width=0, height=0)

    refresh_rate = getattr(win32api.EnumDisplaySettings(win32api.EnumDisplayDevices().DeviceName, -1),
                           'DisplayFrequency')

    def motion(event=None):
        root.focus_set()
        button.unbind("<Enter>")
        button.unbind("<Leave>")
        move_to(button, x=50, y=50, width=200, height=100, delay=0.25, fps=refresh_rate)
        move_to(texts, x=50, y=150, width=200, height=300, delay=0.25, fps=refresh_rate, start_delay=0.25,
                advance_delay={"x": 0.25, "y": 0.25, "width": 0, "height": 0.25})
        button.configure(command=motion2)
        return event

    def motion2(event=None):
        root.focus_set()
        button.bind("<Enter>", zoom_in)
        button.bind("<Leave>", zoom_out)
        move_to(texts, x=50, y=150, width=200, height=0, delay=0.25, fps=refresh_rate)
        move_to(texts, x=50, y=150, width=0, height=0, delay=0.01, fps=refresh_rate, start_delay=0.24)
        move_to(button, x=50, y=50, width=100, height=50, delay=0.25, fps=refresh_rate, start_delay=0.25)
        button.configure(command=motion)
        return event

    def zoom_in(event=None):
        zoom(button, ratio=1.1, delay=0.1, fps=refresh_rate)
        return event

    def zoom_out(event=None):
        unzoom(button, ratio=1.1, delay=0.1, fps=refresh_rate)
        return event

    button.configure(command=motion)
    button.bind("<Enter>", zoom_in)
    button.bind("<Leave>", zoom_out)

    root.mainloop()


if __name__ == "__main__":
    test()
