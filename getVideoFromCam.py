from threading import Thread
import cv2
import time


class getVideoFromCam:
    """
    Class that holds a VideoStream Object in a thread and is able to read from it.
    """

    def __init__(self, video_source=0, pb_width=640, pb_height=480):
        self.cam = cv2.VideoCapture(video_source)
        self.stopped = False
        self.pb_width = pb_width
        self.pb_height = pb_height

        initialized = False

        while not initialized:
            set_x = self.cam.set(3, 640)
            set_y = self.cam.set(4, 640)
            print(str(set_x) + str(set_y))
            if set_x and set_y:
                initialized = True

        self.ok, self.frame = self.cam.read()

        #self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.pb_width)
        #self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.pb_height)
        self.ip_width = self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.ip_height = self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print("Cam stream dimensions are: " + str(self.ip_width) + "x" + str(self.ip_width))

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.ok:
                self.stop()
            else:
                self.ok, self.frame = self.cam.read()

    def get_frame(self, pb_width, pb_height):
        ret = False
        if self.cam.isOpened():
            ret, frame = self.cam.read()
            r = pb_width / float(self.ip_width)
            dim = (pb_width, int(self.ip_height * r))
            frame_resized = cv2.resize(frame, dim)
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return ret, None

    def stop(self):
        self.stopped = True

    def __del__(self):
        if self.cam.isOpened():
            self.cam.release()
