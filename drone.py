import cv2
import struct
import numpy as np
import network
import utils
import RPi.GPIO as gpio
import threading
import time


pinCode11 = 11
pinCode12 = 12
NET_STAT_OK = '100'
NET_STAT_CONTINUE = '200'
NET_STAT_ERROR = '400'


class DroneControl:
    def __init__(self):
        self.ctlAngle = 0.
        self.ctlPower = 0.
        self.config = utils.Config('./config.yaml')
        self.network = network.NetworkServer(self.config)
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)
        gpio.setup(11, gpio.OUT)
        gpio.setup(12, gpio.OUT)
        self.jpegPara = (cv2.IMWRITE_JPEG_QUALITY, 25)

        self.sync = PhotoSync()

    def communication(self):
        try:
            com_cmd_recv = self.network.cmdRecv()
            self.network.cmdSend(com_cmd_recv)
            com_pack_recv = self.network.packRecv()
            self.ctlPower, self.ctlAngle = struct.unpack('ff', com_pack_recv)
            self.network.cmdSend(NET_STAT_OK)
            photo_req = self.network.cmdRecv().rstrip()
            if photo_req != NET_STAT_CONTINUE:
                # self.network.cmdSend(NET_STAT_ERROR)
                print('Waiting for user action')
            photo = self.sync.photo
            if photo is None:
                photo = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            # photo = cv2.resize(photo, (640, 480))
            photo_encode = cv2.imencode('.jpg', photo, self.jpegPara)[1]
            photo_encode = np.array(photo_encode)
            photo_data, photo_size = photo_encode.tobytes(), len(photo_encode)
            self.network.cmdSend(photo_size)
            photo_OK = self.network.cmdRecv().rstrip()
            if photo_OK != NET_STAT_OK:
                # self.network.cmdSend(NET_STAT_ERROR)
                print('Waiting for user action')

            self.network.dataSend(photo_data)
        except ConnectionResetError:
            self.network.reset()
            self.go()

    def solve(self):
        if self.ctlPower == 1:
            gpio.output(pinCode11, gpio.HIGH)
            gpio.output(pinCode12, gpio.LOW)
            print('10')
        elif self.ctlPower == -1:
            gpio.output(pinCode11, gpio.LOW)
            gpio.output(pinCode12, gpio.HIGH)
            print('01')
        else:
            gpio.output(pinCode12, gpio.LOW)
            gpio.output(pinCode11, gpio.LOW)

        if self.ctlAngle == 1:
            pass

    def go(self):
        self.network.tryConnect()
        self.sync.go()
        while True:
            self.communication()
            self.solve()


class PhotoSync:
    def __init__(self):
        self.photo = np.random.randint(0, 255, (480, 640, 3))
        self.config = utils.Config('./config.yaml')
        self.frame_rate = 1000 // self.config.FRAME

        self.capture = cv2.VideoCapture(0)

        self.capture.set(cv2.CAP_PROP_FPS, 24)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    def go(self):
        t = threading.Thread(target=self.update_photo_thread)
        t.start()

    def update_photo_thread(self):
        while True:
            cur_time = int(time.time()*1000)

            self.photo = self.capture.read()[1]

            time_in_loop = int(time.time()*1000) - cur_time
            if time_in_loop < self.frame_rate:
                time.sleep((self.frame_rate - time_in_loop) / 1000)


if __name__ == '__main__':
    drone = DroneControl()
    drone.go()
