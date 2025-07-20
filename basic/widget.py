import basic.libimport
basic.libimport.set_import_lib()
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QRect, QObject, QRectF
import time
import threading
import math
import win32api
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


class HBoolean(QObject):
    def __init__(self, value: bool = False):
        super().__init__()
        self._my_bool = value

    @property
    def my_bool(self):
        return self._my_bool

    @my_bool.setter
    def my_bool(self, value):
        self._my_bool = bool(value)

    def get(self) -> bool:
        return self._my_bool

    def set(self, value: bool):
        self._my_bool = value


class HQAnimate(QObject):
    def __init__(self, target, destination: QRect, duration=0.5, fps=120,
                 functions=None, parameters=None, ad_duration=None, func_delay=0, LOCK=HBoolean(False)):
        super(HQAnimate, self).__init__()
        if not parameters:
            parameters = []
        self.target = target
        self.duration = duration
        self.fps = fps
        self.functions = functions
        self.parameters = parameters
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.frames = int(duration * fps)
        self.current_frame = 0

        # Store start and target geometry
        self.start_geom = target.geometry()
        self.destination = destination
        self.ad_duration = ad_duration
        self.func_delay = func_delay

        # Precompute per-frame delta for x, y, width, height
        self.sequence_x = []
        self.sequence_y = []
        self.sequence_w = []
        self.sequence_h = []
        self.force_in = False
        self.running = False
        self.force_stopped = False
        self.LOCK = LOCK

    def generate_frames(self):
        start_time = time.time()
        x = self.destination.x()
        y = self.destination.y()
        width = self.destination.width()
        height = self.destination.height()
        original_x = self.start_geom.x()
        original_y = self.start_geom.y()
        original_width = self.start_geom.width()
        original_height = self.start_geom.height()
        parameters = self.parameters

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

        if self.duration < 0:
            raise ValueError(f'Function "move_to()": parameter "delay" must >= 0.')

        if self.fps <= 0:
            raise ValueError(f'Function "move_to()": parameter "fps" must > 0.')

        direction_x = 1 if x >= original_x else -1
        direction_y = 1 if y >= original_y else -1
        direction_width = 1 if width >= original_width else -1
        direction_height = 1 if height >= original_height else -1

        length_x = abs(original_x - x)
        length_y = abs(original_y - y)
        length_width = abs(original_width - width)
        length_height = abs(original_height - height)

        fps_delay = get_frame_rate_delay(self.fps)

        FUNC = M_FUNC["GOOGLE"]
        if isinstance(FUNC, list):
            if self.force_in:
                FUNC = FUNC[0]
            elif direction_width == -1 or direction_height == -1:
                FUNC = FUNC[1]
            else:
                FUNC = FUNC[0]

        if isinstance(self.ad_duration, dict):
            velocity_x = get_func_velocities(length_x, self.ad_duration["x"], fps_delay, FUNC)
            velocity_y = get_func_velocities(length_y, self.ad_duration["y"], fps_delay, FUNC)
            velocity_width = get_func_velocities(length_width, self.ad_duration["width"], fps_delay, FUNC)
            velocity_height = get_func_velocities(length_height, self.ad_duration["height"], fps_delay, FUNC)

        else:
            velocity_x = get_func_velocities(length_x, self.duration, fps_delay, FUNC)
            velocity_y = get_func_velocities(length_y, self.duration, fps_delay, FUNC)
            velocity_width = get_func_velocities(length_width, self.duration, fps_delay, FUNC)
            velocity_height = get_func_velocities(length_height, self.duration, fps_delay, FUNC)

        total_frames = round(self.duration / fps_delay)

        times = 1
        for i in range(total_frames):
            _x = original_x + velocity_x[min(times - 1, len(velocity_x) - 1)] * direction_x
            _y = original_y + velocity_y[min(times - 1, len(velocity_y) - 1)] * direction_y
            _width = original_width + velocity_width[min(times - 1, len(velocity_width) - 1)] * direction_width
            _height = original_height + velocity_height[min(times - 1, len(velocity_height) - 1)] * direction_height
            self.sequence_x.append(_x)
            self.sequence_y.append(_y)
            self.sequence_w.append(_width)
            self.sequence_h.append(_height)
            times += 1
        debug(f"Generated %d frames. in {time.time() - start_time} s" % times, COLORS.INFO, "GUI")

    def start(self):
        self.running = True
        self.force_stopped = False
        debug("Play HQAnimate", COLORS.INFO, "GUI")
        self.generate_frames()
        self.target.show()
        self.timer.start(1000 // self.fps)

    def withdraw(self, direction="center", duration=0.5, fps=120,
                 functions=None, parameters=None, ad_duration=None, func_delay=0):
        original_x = self.target.x()
        original_y = self.target.y()
        original_width = self.target.width()
        original_height = self.target.height()

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

        self.destination = QRect(x, y, width, height)
        self.timer.stop()
        if not parameters:
            parameters = []
        self.start_geom = self.target.geometry()
        self.duration = duration
        self.fps = fps
        self.functions = functions
        self.parameters = parameters
        self.ad_duration = ad_duration
        self.func_delay = func_delay
        self.frames = int(duration * fps)
        self.current_frame = 0
        self.sequence_x.clear()
        self.sequence_y.clear()
        self.sequence_w.clear()
        self.sequence_h.clear()
        self.start()

    def configure(self, new_destination: QRect, duration=0.5, fps=120,
                  functions=None, parameters=None, ad_duration=None, func_delay=0):
        self.timer.stop()
        if not parameters:
            parameters = []
        self.start_geom = self.target.geometry()
        self.destination = new_destination
        self.duration = duration
        self.fps = fps
        self.functions = functions
        self.parameters = parameters
        self.ad_duration = ad_duration
        self.func_delay = func_delay
        self.frames = int(duration * fps)
        self.current_frame = 0
        self.sequence_x.clear()
        self.sequence_y.clear()
        self.sequence_w.clear()
        self.sequence_h.clear()

    def restart(self, new_destination: QRect, duration=0.5, fps=120,
                functions=None, parameters=None, ad_duration=None, func_delay=0):
        self.timer.stop()
        if not parameters:
            parameters = []
        self.start_geom = self.target.geometry()
        self.destination = new_destination
        self.duration = duration
        self.fps = fps
        self.functions = functions
        self.parameters = parameters
        self.ad_duration = ad_duration
        self.func_delay = func_delay
        self.frames = int(duration * fps)
        self.current_frame = 0
        self.sequence_x.clear()
        self.sequence_y.clear()
        self.sequence_w.clear()
        self.sequence_h.clear()
        self.start()

    play = restart

    def update_frame(self):
        # debug(f"Ticking HQAnimate {self.current_frame} / {len(self.sequence_h)}", COLORS.INFO, "GUI")
        if self.current_frame >= self.frames:
            self.timer.stop()
            self.target.setGeometry(self.destination)

            def run_funcs():
                for func in self.functions:
                    if not self.force_stopped:
                        func()

            if self.functions:
                self.timer.singleShot(self.func_delay, run_funcs)
            self.running = False
            return

        if self.LOCK.get():
            self.stop()

        new_x = self.sequence_x[self.current_frame]
        new_y = self.sequence_y[self.current_frame]
        new_w = self.sequence_w[self.current_frame]
        new_h = self.sequence_h[self.current_frame]

        self.target.setGeometry(int(new_x), int(new_y), int(new_w), int(new_h))
        self.current_frame += 1

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()
        self.force_stopped = True
        self.running = False

    def isRunning(self):
        return self.running


class HQFade(QObject):
    def __init__(self, window, start_alpha, end_alpha, duration=0.5, fps=120, fade_in=False):
        super().__init__()
        self.window = window
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.duration = duration
        self.fps = fps

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.frames = int(duration * fps)
        self.step = round((abs(end_alpha - start_alpha)) / fps / duration * -1, 4)
        if fade_in:
            self.step = self.step * -1
        self.current_frame = 0
        self.running = False

    def start(self):
        self.running = True
        self.window.show()
        self.timer.start(1000 // self.fps)

    def restart(self, new_light, duration=0.5, fade_in=False):
        self.timer.stop()
        self.current_frame = 0
        self.end_alpha = new_light
        self.duration = duration
        self.start_alpha = self.window.windowOpacity()
        self.step = round((abs(self.end_alpha - self.start_alpha)) / self.fps / self.duration * -1, 4)
        if fade_in:
            self.step = self.step * -1
        self.start()

    def fade_in(self, duration=0.5):
        self.restart(1.0)
        self.step = self.step * -1
        self.timer.stop()
        self.current_frame = 0
        self.end_alpha = 1.0
        self.duration = duration
        self.start_alpha = self.window.windowOpacity()
        self.step = round((abs(self.end_alpha - self.start_alpha)) / self.fps / self.duration * -1, 4)
        self.step = self.step * -1
        self.start()

    def fade_out(self, duration=0.5):
        self.restart(1.0)
        self.step = self.step * -1
        self.timer.stop()
        self.current_frame = 0
        self.end_alpha = 0.0
        self.duration = duration
        self.start_alpha = self.window.windowOpacity()
        self.step = round((abs(self.end_alpha - self.start_alpha)) / self.fps / self.duration * -1, 4)
        self.start()

    def update_frame(self):
        if self.current_frame >= self.frames:
            self.timer.stop()
            self.window.setWindowOpacity(self.end_alpha)
            self.running = False
            return

        self.window.setWindowOpacity(round(self.start_alpha + self.current_frame * self.step, 4))
        self.current_frame += 1

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()
        self.running = False

    def isRunning(self):
        return self.running


class HQPrinter(QObject):
    def __init__(self, widget, string: str, duration=0.25, step=True, step_delay=0.75, FPS=30, funcs=None,
                 func_delay=0, pre_delay=0):
        super().__init__()
        self.widget = widget
        self.string = string
        self.duration = duration
        self.step = step
        self.step_delay = step_delay
        self.fps = FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.functions = funcs
        self.func_delay = func_delay
        self.pre_delay = pre_delay

        self.frames = int(duration * FPS)
        self.current_frame = 0
        self.text_frames = []
        self.running = False
        self.force_stopped = False

    def generate_frames(self):
        start_time = time.time()
        chars = []
        length = 0
        delay = 1 / self.fps
        if self.step:
            wait_time = self.step_delay / len(self.string) if len(self.string) > 0 else 0
            wait_step = round(wait_time / delay)
        else:
            wait_step = 0

        times = 0
        for i in self.string:
            if i in [" ", "\n", "\r", "\b", "	"]:
                chars.append([i] * round(self.duration / delay + round(wait_step * times)))

            elif i not in C_LIST + J_LIST + P_LIST + R_LIST:
                c_l = []
                path_l = ord(i)
                step_l = max(1.0, path_l / (self.duration / delay + round(wait_step * times)))
                if path_l <= self.duration / delay:
                    step_l = 1
                index = 32
                while True:
                    c_l.append(chr(round(index)))
                    index += step_l
                    if index >= path_l:
                        if i != c_l[-1]:
                            c_l.append(i)
                        break

                if len(c_l) < (self.duration / delay) + round(wait_step * times):
                    remains = ((self.duration / delay) + round(wait_step * times)) - len(c_l)
                    if int(remains) != remains:
                        remains = int(remains) + 1
                    else:
                        remains = int(remains)

                    for _chr in range(remains):
                        c_l.insert(0, chr(random.randint(32, 127)))
                if len(c_l) > ((self.duration / delay) + round(wait_step * times)):
                    while len(c_l) > ((self.duration / delay) + round(wait_step * times)):
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
                step_l = max(1.0, path_l / (self.duration / delay + round(wait_step * times)))
                if path_l <= self.duration / delay:
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
                if len(c_l) < ((self.duration / delay) + round(wait_step * times)):
                    remains = ((self.duration / delay) + round(wait_step * times)) - len(c_l)
                    if int(remains) != remains:
                        remains = int(remains) + 1
                    else:
                        remains = int(remains)

                    for _chr in range(remains):
                        c_l.insert(0, random.choice(LIST))
                if len(c_l) > ((self.duration / delay) + round(wait_step * times)):
                    while len(c_l) > ((self.duration / delay) + round(wait_step * times)):
                        c_l.pop(0)
                chars.append(c_l)

                if len(c_l) > length:
                    length = len(c_l)
            times += 1

        times = 0
        c_content = ""
        loc = 0
        while True:
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

            self.text_frames.append(str(c_content + content))
            times += 1
            if times == length:
                break
        debug(f"Generated %d text frames. in {time.time() - start_time} s" % times, COLORS.INFO, "GUI")

    def start(self):
        debug("Play HQPrinter", COLORS.INFO, "GUI")
        self.running = True
        self.force_stopped = False
        if len(self.text_frames) == 0:
            self.generate_frames()
        self.widget.show()
        if self.pre_delay > 0:
            self.timer.singleShot(self.pre_delay, lambda: self.timer.start(1000 // self.fps))
        else:
            self.timer.start(1000 // self.fps)

    def restart(self, string: str, duration=0.25, step=True, step_delay=0.75, FPS=30, funcs=None,
                func_delay=0, pre_delay=0):
        self.timer.stop()
        self.current_frame = 0
        self.text_frames = []
        self.string = string
        self.duration = duration
        self.step = step
        self.step_delay = step_delay
        self.fps = FPS
        self.functions = funcs
        self.func_delay = func_delay
        self.pre_delay = pre_delay
        self.start()

    print = restart

    def configure(self, string: str, duration=0.25, step=True, step_delay=0.75, FPS=30, funcs=None,
                  func_delay=0, pre_delay=0):
        self.timer.stop()
        self.current_frame = 0
        self.text_frames = []
        self.string = string
        self.duration = duration
        self.step = step
        self.step_delay = step_delay
        self.fps = FPS
        self.functions = funcs
        self.func_delay = func_delay
        self.pre_delay = pre_delay
        self.generate_frames()

    def update_frame(self):
        if self.current_frame >= len(self.text_frames):
            self.timer.stop()
            self.widget.setText(self.string)

            def run_funcs():
                for func in self.functions:
                    if not self.force_stopped:
                        func()

            if self.functions:
                self.timer.singleShot(self.func_delay, run_funcs)
            self.running = False
            return

        self.widget.setText(self.text_frames[self.current_frame])
        self.current_frame += 1

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()
        self.running = False
        self.force_stopped = True

    def isRunning(self):
        return self.running


class HQEndlessAnimation(QObject):
    def __init__(self, widget, image_sequence, fps, stop_condition=HBoolean(False), have_reset=False):
        super().__init__()
        self.widget = widget
        self.image_sequence = image_sequence
        self.reset_sequence = []
        self.stop_condition = stop_condition
        self.fps = fps

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.have_reset = have_reset
        self.resetting = False
        self.current_frame = 0

    def reset(self):
        if self.have_reset:
            self.reset_sequence = []

            if self.current_frame > len(self.image_sequence) / 2:
                times = self.current_frame
                gap = max(round((len(self.image_sequence) - self.current_frame) / self.fps), 1)
                while times < len(self.image_sequence):
                    icon = self.image_sequence[times]
                    self.reset_sequence.append(icon)
                    times += gap
            else:
                times = self.current_frame
                gap = max(round(self.current_frame / self.fps), 1)
                while times >= 0:
                    icon = self.image_sequence[times]
                    self.reset_sequence.append(icon)
                    times -= gap
            self.current_frame = 0
            self.resetting = True

    def start(self):
        debug("Play HQEndlessAnimation", COLORS.INFO, "GUI")
        self.widget.show()
        self.timer.start(1000 // self.fps)

    def restart(self, image_sequence, stop_condition=HBoolean(False)):
        self.timer.stop()
        self.current_frame = 0
        self.resetting = False
        self.image_sequence = image_sequence
        self.stop_condition = stop_condition
        self.start()

    def update_frame(self):
        # debug(f"Updating tick {self.current_frame}/{len(self.image_sequence)}", COLORS.INFO, "GUI")
        # debug(f"Widget info: Visible({self.widget.isVisible()}), size({self.widget.size()}, pos({self.widget.pos()})", COLORS.INFO, "GUI")
        if self.stop_condition.get():
            # debug(f"Pause play", COLORS.INFO, "GUI")
            self.widget.setPixmap(self.image_sequence[self.current_frame])
            return 0

        if self.resetting:
            if self.current_frame >= len(self.reset_sequence):
                self.resetting = False
                self.current_frame = 0
                return
            self.widget.setPixmap(self.reset_sequence[self.current_frame])
        else:
            if self.current_frame >= len(self.image_sequence):
                self.current_frame = 0
            self.widget.setPixmap(self.image_sequence[self.current_frame])
        self.current_frame += 1


class HQNormalAnimation(QObject):
    def __init__(self, widget, image_sequence, fps, stop_condition=HBoolean(False), have_reset=False):
        super().__init__()
        self.widget = widget
        self.image_sequence = image_sequence
        self.reset_sequence = []
        self.stop_condition = stop_condition
        self.fps = fps

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.have_reset = have_reset
        self.resetting = False
        self.current_frame = 0
        self.force_stopped = False
        self.running = False

    def reset(self):
        if self.have_reset:
            self.reset_sequence = []

            if self.current_frame > len(self.image_sequence) / 2:
                times = self.current_frame
                gap = max(round((len(self.image_sequence) - self.current_frame) / self.fps), 1)
                while times < len(self.image_sequence):
                    icon = self.image_sequence[times]
                    self.reset_sequence.append(icon)
                    times += gap
            else:
                times = self.current_frame
                gap = max(round(self.current_frame / self.fps), 1)
                while times >= 0:
                    icon = self.image_sequence[times]
                    self.reset_sequence.append(icon)
                    times -= gap
            self.current_frame = 0
            self.resetting = True

    def start(self):
        # debug("Play HQEndlessAnimation", COLORS.INFO, "GUI")
        self.force_stopped = False
        self.running = True
        self.widget.show()
        self.timer.start(1000 // self.fps)

    def restart(self, image_sequence, fps, stop_condition=HBoolean(False)):
        self.timer.stop()
        self.fps = fps
        self.current_frame = 0
        self.resetting = False
        self.image_sequence = image_sequence
        self.stop_condition = stop_condition
        self.start()

    play = restart

    def update_frame(self):
        # debug(f"Updating tick {self.current_frame}/{len(self.image_sequence)}", COLORS.INFO, "GUI")
        if self.stop_condition.get():
            # debug(f"Pause play", COLORS.INFO, "GUI")
            return 0

        if self.resetting:
            if self.current_frame >= len(self.reset_sequence):
                self.resetting = False
                self.current_frame = 0
                return
            self.widget.setPixmap(self.reset_sequence[self.current_frame])
        else:
            if self.current_frame >= len(self.image_sequence):
                self.timer.stop()
                self.widget.setPixmap(self.image_sequence[-1])
                self.running = False
                return
            self.widget.setPixmap(self.image_sequence[self.current_frame])
        self.current_frame += 1

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()
        self.force_stopped = True
        self.running = False

    def isRunning(self):
        return self.running


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


def withdraw(widget, direction="center", delay=0.5, fps=60, start_delay=0.0, advance_delay=None, is_windows=False,
             after_funtions=None):
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

        widget.setText(str(c_content + content))
        widget.repaint()
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
            widget.setText(content)
            break
        else:
            pass


def accurate_delay(delay):
    """ Function to provide accurate time delay in millisecond"""
    winmm = ctypes.windll.winmm
    winmm.timeBeginPeriod(1)
    time.sleep(delay / 1000)
    winmm.timeEndPeriod(1)


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
