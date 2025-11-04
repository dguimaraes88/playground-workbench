import cv2
from udpFrameSender import UDPFrameSender # type: ignore

class VideoCapture:
    def __init__(self, cameraDeviceID, showCamera):
        print("VIDEO CAPTURE INITED")
        self.deviceCamID = cameraDeviceID
        self.debugCamera = showCamera

        self.udpObj = UDPFrameSender("localhost", 8383)
        
    def initVideoCapture(self):
        self.cap = cv2.VideoCapture(self.deviceCamID, cv2.CAP_DSHOW)
        
        try:
            while self.cap.isOpened():
                rect, frame = self.cap.read()
                
                if not rect:
                    break

                self.udpObj.encodeImage(frame)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #QUERO ENVIAR A FRAME POR UDP AQUI PARA UM SERVIDOR 
                if self.debugCamera:
                    cv2.imshow('CAMERA', frame_rgb)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
                    break
            self.cap.release()
            cv2.destroyAllWindows()                    
                
        except:
            print("FAILEDDDDD VIDEO NOT CAPTURED")

  
        
    