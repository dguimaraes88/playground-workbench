class UDPFrameSender:
    def __init__(self):
        print("UDP SENDER INIT")
        self.serverIP = "localhost"
        self.serverPort = 8585
        
    def sendData(self):
        print("Data sent!")