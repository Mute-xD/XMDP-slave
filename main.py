# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

import RPi.GPIO as gpio
import time
import cv2
import numpy as np


capture = cv2.VideoCapture(0)


def blinker(pinCode, times, delay):
    for _ in range(times):
        gpio.output(pinCode, gpio.HIGH)
        time.sleep(delay)
        gpio.output(pinCode, gpio.LOW)
        time.sleep(delay)


def videoCap():
    while True:
        _, frame = capture.read()
        frame = cv2.flip(frame, 1)
        cv2.imwrite('./testing.jpg', frame)



if __name__ == '__main__':

    videoCap()
