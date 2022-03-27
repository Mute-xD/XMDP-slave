import random
import time
import numpy as np
import RPi.GPIO as GPIO
import network

bt = network.BluetoothControlServer()
bt.tryConnect()
ip = bt.getIp()

bt.cmdSend(ip)
print(bt.cmdRecv())
bt.cmdSend(0)
