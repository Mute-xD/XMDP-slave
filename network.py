import socket
import time

import bluetooth

NET_STAT_OK = '100'
NET_STAT_CONTINUE = '200'


class Network:
    """

    """

    def __init__(self, config):
        self.config = config
        self.port = config.PORT
        self.cmdPackSize = config.CMDPACKSIZE

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect = None
        self.type = None

    def dataRecv(self, dataSize):
        buff = b''
        while dataSize:
            temp = self.connect.recv(dataSize)
            if not temp:
                print('DATA RECV ERROR')
                return None
            buff += temp
            dataSize -= len(temp)
        return buff

    def dataSend(self, byteData):
        self.connect.send(byteData)

    def cmdRecv(self):
        return self.connect.recv(self.cmdPackSize).decode('utf-8')

    def cmdSend(self, cmd):
        self.connect.send(str(cmd).ljust(self.cmdPackSize).encode('utf-8'))

    def packRecv(self):
        return self.connect.recv(self.cmdPackSize)

    def packSend(self, pack):
        self.connect.send(pack)

    def getIp(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip


class NetworkServer(Network):
    def __init__(self, config):
        super(NetworkServer, self).__init__(config)
        self.tryBind()
        self.sock.listen(5)
        self.type = 'SRV'

    def tryBind(self):
        try:
            self.sock.bind(('0.0.0.0', self.port))
        except OSError:
            print('Bind Failed! Retry in 5s')
            time.sleep(5)
            self.tryBind()

    def tryConnect(self):
        print('Connecting...')
        try:
            self.connect, addr = self.sock.accept()
            print('Connected to: ', addr)
        except KeyboardInterrupt:
            self.sock.close()
        except RuntimeError:
            self.reset()

    def reset(self):
        print('Retry')
        self.connect.close()


class NetworkClient(Network):
    def __init__(self, config):
        super(NetworkClient, self).__init__(config)
        self.ip = config.PIIP
        self.type = 'CLI'

    def tryConnect(self):
        print('Connecting to Server...')
        try:
            self.sock.connect((self.ip, self.port))
            self.connect = self.sock
        except KeyboardInterrupt:
            self.sock.close()
        except ConnectionRefusedError:
            self.reset()

    def reset(self):
        print('Retry')
        self.tryConnect()


class BluetoothControl:
    def __init__(self):
        self.port = 1
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.type = None
        self.connect = None
        self.cmdPackSize = 672

    def dataRecv(self, dataSize):
        buff = b''
        while dataSize:
            temp = self.connect.recv(dataSize)
            if not temp:
                print('DATA RECV ERROR')
                return None
            buff += temp
            dataSize -= len(temp)
        return buff

    def dataSend(self, byteData):
        self.connect.send(byteData)

    def cmdRecv(self):
        return self.connect.recv(self.cmdPackSize).decode('utf-8')

    def cmdSend(self, cmd):
        self.connect.send(str(cmd).ljust(self.cmdPackSize).encode('utf-8'))

    def packRecv(self):
        return self.connect.recv(self.cmdPackSize)

    def packSend(self, pack):
        self.connect.send(pack)


class BluetoothControlServer(BluetoothControl):
    def __init__(self):
        super(BluetoothControlServer, self).__init__()
        self.sock.bind(('', 0))
        self.sock.listen(1)

    def tryConnect(self):
        print('BT Connecting...')
        try:
            self.connect, addr = self.sock.accept()
            print('Connected to: ', addr)
        except KeyboardInterrupt:
            self.sock.close()
        except RuntimeError:
            self.reset()

    def reset(self):
        print('Retry')
        self.connect.close()
        self.sock.close()
        self.tryConnect()


class BluetoothControlClient(BluetoothControl):
    def __init__(self):
        super(BluetoothControlClient, self).__init__()
        self.targetMAC = '9C:30:5B:DC:6E:50'

    def tryConnect(self):
        print('BT Connecting to Server...')
        try:
            self.sock.connect((self.targetMAC, self.port))
            self.connect = self.sock
            print('Connected!')
        except KeyboardInterrupt:
            self.sock.close()
        except ConnectionRefusedError:
            self.reset()
        except TimeoutError:
            self.reset()

    def reset(self):
        print('Retry')
        self.connect.close()
        self.sock.close()
        self.tryConnect()


if __name__ == '__main__':
    import utils

    config_ = utils.Config('./config.yaml')
    nc = NetworkClient(config_)
    nc.tryConnect()
    while True:
        nc.cmdSend('wow')
        print(nc.cmdRecv())
