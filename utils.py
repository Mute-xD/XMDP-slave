import yaml
import RPi.GPIO as GPIO


class Config:
    def __init__(self, file):
        super().__init__()
        with open(file) as f:
            self._dict = yaml.load(f, Loader=yaml.FullLoader)

    def __getattr__(self, name):
        return self._dict[name]

    def getDict(self):
        return self._dict

    def __getstate__(self):
        return self._dict

    def __setstate__(self, state):
        self._dict = state


class Servo:
    def __init__(self, port):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(port, GPIO.OUT)
        self.pwm = GPIO.PWM(port, 50)
        self.pwm.start(0)

    def set(self, angle):
        self.pwm.ChangeDutyCycle(self.calDutyRatio(angle))

    @staticmethod
    def calDutyRatio(angle):
        if not 0. <= angle <= 180.:
            raise RuntimeError('what the fuck?')
        return 2.5 + angle / 18.
