from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlDir
from pyforms.controls   import ControlPlayer
from pyforms.controls   import ControlButton
from pyforms.controls   import ControlCheckBoxList

import cv2
import os
from time import gmtime, strftime

class QuadView(BaseWidget):

    def __init__(self, *args, **kwargs):
        super().__init__('4-Cam')

        self.set_margin(10)

        # Definition of the forms fields
        self._player1 = ControlPlayer('Player1')
        self._player2 = ControlPlayer('Player2')
        self._player3 = ControlPlayer('Player3')
        self._player4 = ControlPlayer('Player4')
        self._runbutton  = ControlButton('Stop')
        self._screenshot = ControlButton('Screenshot')
        self._outputfile = ControlDir('Screenshots Ausgabe Ordner')
        self._cams       = ControlCheckBoxList('Kameras')

        # Define the event that will be called when the run button is processed
        self._runbutton.value       = self.__stopEvent
        self._screenshot.value      = self._saveImages

        self.__check_all_avaliable_cameras()

        self.formset = [{
            '0-Kameras': [('_runbutton'), ('_player1', '_player2'), ('_player3', '_player4')],
            '1-Einstellungen': [('_outputfile'), ('_cams')]
        }]

        self._player1.value = self.__assign_capture(0)
        self._player2.value = self.__assign_capture(1)
        self._player3.value = self.__assign_capture(2)
        self._player4.value = self.__assign_capture(3)

        self._outputfile.value = os.getcwd()

        self.__runEvent()

    def __assign_capture(self, player_id):
        checked_cam_ids = self._cams.checked_indexes
        if checked_cam_ids.__len__() > player_id:
            return cv2.VideoCapture(checked_cam_ids[player_id])
        return cv2.VideoCapture()



    def __runEvent(self):
        """
        After setting the best parameters run the full algorithm
        """
        self._player1.update_frame()
        self._player1.play()
        self._player2.update_frame()
        self._player2.play()
        self._player3.update_frame()
        self._player3.play()
        self._player4.update_frame()
        self._player4.play()
        pass

    def __stopEvent(self):
        self._player1.stop()
        self._player2.stop()
        self._player3.stop()
        self._player4.stop()

    def _saveImages(self):
        """
        Saves the Images of all cams to a file
        :return:
        """
        currentTime = str(strftime("%Y-%m-%d_%H:%M:%S", gmtime()))
        cv2.imwrite(os.path.join(self._outputfile.value, currentTime + '_cam_1.png'), self._player1.value['frame'])
        cv2.imwrite(os.path.join(self._outputfile.value, currentTime + '_cam_2.png'), self._player2.value['frame'])
        cv2.imwrite(os.path.join(self._outputfile.value, currentTime + '_cam_3.png'), self._player3.value['frame'])
        cv2.imwrite(os.path.join(self._outputfile.value, currentTime + '_cam_4.png'), self._player4.value['frame'])
        print("Written screenshots to disk")
        pass

    def accessible_device(self, source):
        cap = cv2.VideoCapture(source)
        if cap is None or not cap.isOpened():
            return False
        cap.release()
        return True

    def __check_all_avaliable_cameras(self):
        for x in range (0, 10):
            isCam = self.accessible_device(x)
            if isCam:
                self._cams += ('Kamera ' + str(x), True)


if __name__ == '__main__':

    from pyforms import start_app
    start_app(QuadView)
