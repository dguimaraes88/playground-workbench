from videoCapture import VideoCapture # type: ignore

from handLandmarkDetector import HandLandmarkDetector # type: ignore 

import threading 
import time 


if __name__ == "__main__":
    print("APP INIT")
    
    obj = VideoCapture(0,True)
    t1 = threading.Thread(target=obj.initVideoCapture)
    t1.start()
    