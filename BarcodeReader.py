import cv2
from pyzbar import pyzbar
from scipy import ndimage
from threading import Thread, Lock
import numpy as np
import time
import imutils
import requests


class Barcode:
    """Получает фрейм возвращает строку"""

    def __init__(self, frame):
        self.frame = frame
        self._scale_percent = 60

    def __repr__(self):
        return 'Barcode'

    def _find_barcode(self):
        barcodes = pyzbar.decode(self.frame, symbols=[pyzbar.ZBarSymbol.CODE128])
        barcodeData = [barcode.data.decode('utf-8') for barcode in barcodes]
        return barcodeData

    def get_barcode(self):
        """Увелчивает фрейм с поворотом на 30 градусов"""
        if self._scale_percent <= 150:
            for i in range(4):
                width = int(self.frame.shape[1] * self._scale_percent / 100)
                height = int(self.frame.shape[0] * self._scale_percent / 100)
                dim = (width, height)
                cv2.resize(self.frame, dim, interpolation=cv2.INTER_CUBIC)
                if i == 0:
                    barcodeData = self._find_barcode()
                    if len(barcodeData) > 0:
                        yield barcodeData
                else:
                    self.frame = imutils.rotate(self.frame, 30)
                    barcodeData = self._find_barcode()
                    yield barcodeData

            self._scale_percent += 15

        else:
            self._scale_percent = 60


class FrameReader(Thread):
    def __init__(self):
        Thread.__init__(self)
        Thread.daemon = True
        self.last_frame = None
        self.mutex = Lock()
        self.timeout = 0.01
        self._shape = None

    def run(self):
        first = True
        while first:
            try:
                if not self.__capture.isOpened():
                    raise Exception
                ret = False
                while not ret:
                    ret = self.__capture.grab()
                    ret, image = self.__capture.retrieve()
                self._shape = image.shape
                first = False
            except:
                self.__connect()
                time.sleep(5)
        while True:
            self.__put_frame()
            time.sleep(self.timeout)

    def __connect(self):
        self.__capture = cv2.VideoCapture(self._url)
        self.__capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def set_capture(self, url):
        self._url = url
        self.__connect()

    def get_frame(self) -> np.ndarray:
        try:
            self.mutex.acquire()
            return self.last_frame
        finally:
            self.mutex.release()

    def __put_frame(self):
        try:
            ret = self.__capture.grab()
            ret, image = self.__capture.retrieve()
            self.last_frame = image
            if ret and self.__capture.isOpened():
                try:
                    self.mutex.acquire()
                    self.last_frame = image
                finally:
                    self.mutex.release()
            else:
                raise cv2.error
        except (cv2.error, AttributeError):
            self.last_frame = None
            self.__connect()
            time.sleep(5)

    @property
    def shape(self):
        return self._shape


if __name__ == '__main__':
    print('start project')
    cap = FrameReader()
    cap.set_capture(
        'rtsp://admin:splinex271813@192.168.0.73:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
    print('capture is done')
    cap.start()
    print('start capture')

    # cap = cv2.VideoCapture(
    #         'rtsp://admin:splinex271813@192.168.0.73:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')
    # cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    url = 'http://127.0.0.1:5000/barcode'
    while True:
        frame = cap.get_frame()
        if frame is not None:
            barcode = Barcode(frame)
            barcodeData = barcode.get_barcode()
            for barcode in list(barcodeData):
                if barcode:
                    # print((barcode))
                    object_ = {barcode[0]: 'barcode'}
                    requests.post(url, data=object_)
                    # requests.get(url, data={1:'one'})
                    # exit()

            time.sleep(0.01)
