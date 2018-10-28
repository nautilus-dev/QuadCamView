import cv2
import tkinter
import numpy as np
from getVideoFromCam import getVideoFromCam

class Stream:
    def __init__(self, source_id, col, row, width, height, black=False):
        self.source_id = source_id
        self.col = col
        self.row = row
        self.width = width
        self.height = height
        self.frame = None
        self.black = black

    def initvideo(self):
        if not self.black:
            self.vid = getVideoFromCam(self.source_id)

    def set_heigh_width(self, width, height):
        self.height = height
        self.width = width

    def set_black(self):
        self.black = True

    def getheight(self):
        return self.height

    def getwidth(self):
        return self.width

    def black_pic(self):
        return np.asarray(np.zeros([self.height, self.width, 3], dtype=np.uint8))

    def getframe(self):
        if self.black:
            return True, self.black_pic()
        return self.vid.get_frame(self.width, self.height)

    def setcanvas(self, window):
        self.canvas = tkinter.Canvas(window, width=self.width, height=self.height)
        self.canvas.grid(column=self.col, row=self.row)
