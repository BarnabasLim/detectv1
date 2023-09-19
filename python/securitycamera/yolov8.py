from ultralytics import YOLO
import cv2
import numpy as np
import logging

logger = logging.getLogger('security_camera')
class YoloDetector(object):

    def __init__(self):
        self.model = YOLO('./models/yolov8n.pt')
        self.classes=[0, 1,2,3,4,5,7,8,9,15,16,24]

    def detectPerson(self, frame):
        # rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = frame
        results = self.model.predict(source=rgb, classes=self.classes)
        detected_item=self.detect_count(results)
        result=results[0]
        im = result.plot()  # plot a BGR numpy array of predictions
        #print("Check im 5 shape: ",np.array(im).shape, np.array(im.max()))
        # im=np.array(im)/255
        print("frame",frame.shape,frame.max(), frame.min(), im.shape, im.max(), im.min() )
        cv2.imshow("OpenCV/Numpy normal HEREEEEE", np.array(im)/255)
        return (im, detected_item)

    def detect_count(self,results):
        detected_item={}
        class_id=results[0].boxes.cls.cpu().numpy().astype(int)
        names=results[0].names

        for i in class_id:
            if names[i] in detected_item:
                detected_item[names[i]]=detected_item[names[i]]+1
            else:
                detected_item[names[i]]=1
        print(detected_item)
        return detected_item
    

