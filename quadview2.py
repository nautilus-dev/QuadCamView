import tkinter
from tkinter import Grid, Label, LEFT, CENTER, StringVar
import cv2
import PIL.Image, PIL.ImageTk
import time
import math
import numpy as np
import sys
from Stream import Stream
from CountsPerSec import CountsPerSec

# adapated 20181026 from: https://solarianprogrammer.com/2018/04/21/python-opencv-show-video-tkinter-window/


class App:
    def __init__(self, window, window_title, num_streams):
        self._numcols = 2
        self._numrows = 2
        self._minSpacing = 20
        self._lowerspace = 80
        self._min_stream_width = 320
        self._min_stream_height = 240

        self._maxstreams = num_streams if num_streams < 4 else 4
        self._cams = []
        self.__check_all_avaliable_cameras()

        self.window = window
        self.window.title(window_title)
        self.window.attributes('-fullscreen', True)
        self.window.configure(background="black")

        self._stream_width = self._min_stream_width
        self._stream_height = self._min_stream_height

        Grid.rowconfigure(self.window, 0, weight=1)
        Grid.columnconfigure(self.window, 0, weight=1)

        # first we need a grid of two rows and one columns
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.header_frame = tkinter.Frame(window)
        self.video_frame = tkinter.Frame(window)
        self.button_frame = tkinter.Frame(window)
        self.video_frame.columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        self.header_frame.grid(row=0, column=0, sticky='nswe')
        self.video_frame.grid(row=1, column=0, sticky='nswe')
        self.button_frame.grid(row=2, column=0, sticky='nswe')

        cams = str('Anzeige der Kameras: ' + ''.join(str(self._cams)))
        self.header = Label(self.header_frame, text=cams, justify=LEFT)
        self.header.grid(row=0, column=0, sticky='nswe')


        # Grid.rowconfigure(self.video_frame, 0, weight=1)
        # Grid.columnconfigure(self.video_frame, 0, weight=1)
        # Grid.rowconfigure(self.button_frame, 1, weight=1)
        # Grid.columnconfigure(self.button_frame, 0, weight=1)

        self.video_area = tkinter.Frame(self.video_frame)
        self.video_area.grid(column=self._numcols, row=self._numrows, sticky='nswe')

        self.calculate_size()

        self.streams = []

        for x in range(0, self._maxstreams):
            black = False
            if x not in self._cams:
                black = True
            stream = Stream(source_id=x, col=x % self._numcols, row=math.floor(x / self._numcols),
                            # width=self._stream_width, height=self._stream_height, black=black)
                            width=self._stream_width, height=self._stream_height, black=black)
            stream.initvideo()
            # Grid.columnconfigure(self.video_area, x % self._numcols, weight=1)
            # Grid.rowconfigure(self.video_area, math.floor(x / self._numcols), weight=1)
            self.video_area.grid_columnconfigure(x % self._numcols, weight=1)
            self.video_area.grid_rowconfigure(math.floor(x / self._numcols), weight=1)
            stream.setcanvas(self.video_area)
            self.streams.append(stream)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tkinter.Button(self.button_frame, text="Screenshot", width=50, command=self.snapshot)
        Grid.rowconfigure(self.button_frame, 0, weight=1)
        self.btn_snapshot.grid(row=0, column=0, sticky='nswe')

        self.btn_exit = tkinter.Button(self.button_frame, text="Exit", width=50, command=self.quit)
        Grid.rowconfigure(self.button_frame, 0, weight=1)
        self.btn_exit.grid(row=0, column=1, sticky='nswe')

        self.cps = CountsPerSec().start()

        self.delay = 5
        self.stopped = False
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.update()
        self.window.mainloop()

    def calculate_size(self):
        """
        The maximum size in x is depending on the amount of columns (for two columns we have three spacings)
        The maximum size in y is depending on the amount of rows + the button
        """
        x_total_space = self.window.winfo_screenwidth()
        y_total_space = self.window.winfo_screenheight()

        x_video_space = x_total_space - self._minSpacing
        y_video_space = y_total_space - self._minSpacing - self._lowerspace

        x_dim = math.floor((x_video_space / self._numcols) - self._minSpacing)
        y_dim = math.floor((y_video_space / self._numrows) - self._minSpacing)

        self._stream_width = x_dim if x_dim > self._min_stream_width else self._min_stream_width
        self._stream_height = y_dim if y_dim > self._min_stream_height else self._min_stream_height

        print("Set the playback size to: " + str(self._stream_width) + "x" + str(self._stream_height))

    def accessible_device(self, source):
        cap = cv2.VideoCapture(source)
        if cap is None or not cap.isOpened():
            return False
        cap.release()
        return True

    def __check_all_avaliable_cameras(self):
        for x in range(0, 10):
            isCam = self.accessible_device(x)
            if isCam:
                self._cams.append(x)

    def snapshot(self):
        for stream in self.streams:
            ret, frame = stream.getframe()
            if ret:
                cv2.imwrite("Screen-" + time.strftime("%d-%m-%Y-%H-%M-%S") + 'cam' + str(stream.source_id) +".jpg",
                            cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def update(self):
        for stream in self.streams:
            ret, frame = stream.getframe()
            if ret:
                frame = self.putIterationsPerSec(frame, self.cps.countsPerSec())
                stream.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                stream.canvas.create_image(0, 0, image=stream.photo, anchor=tkinter.NW)
        self.window.after(self.delay, self.update)
        self.cps.increment()

    def putIterationsPerSec(self, frame, iterations_per_sec):
        """
        Add iterations per second text to lower-left corner of a frame.
        """

        cv2.putText(frame, "{:.0f} iterations/sec".format(iterations_per_sec),
                    (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0))
        return frame

    def quit(self):
        sys.exit(0)


# Create a window and pass it to the Application object
App(tkinter.Tk(), "QuadCameraView", num_streams=4)
