import socket
import numpy as np

class UDPFrameSender:
    def __init__(self,serverIP,serverPORT):
        print("UDP SENDER INIT")
        self.serverIP = serverIP
        self.serverPort = serverPORT
        self.clientSocket = None

        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print("Impossible to connect socket...")

    def encodeImage(self, dataToEncode):
        data = dataToEncode.tobytes()
        BUFFSIZE = len(data)
        MAX_SAFE_UDP_SIZE = 60000
        #if BUFFSIZE > MAX_SAFE_UDP_SIZE:
            #print("Frame too large...")     
        self.sendEncodedImage(data)

    def sendEncodedImage(self, encodedData):        
        try:
            self.clientSocket.sendto(encodedData, (self.serverIP, self.serverPort))
        except: 
            print("Impossible to send data...")       

    def closeSocketConnection(self):
        self.clientSocket.close()
        print("Connection Closed")


