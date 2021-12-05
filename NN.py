import cv2
import numpy as np
import time
import os
import sys

class neuralnetwork():
    def __init__(self):
        self.CONFIDENCE = 0.001
        self.SCORE_THRESHOLD = 0.001
        self.IOU_THRESHOLD = 0.001

        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        path = os.path.join(base_path, './nn')

        # the neural network configuration
        self.config_path = os.path.join(path, "yolov4.cfg")
        # the YOLO net weights file
        self.weights_path = os.path.join(path, "yolov4.weights")

        # load the YOLO network
        self.net = cv2.dnn.readNetFromDarknet(self.config_path, self.weights_path)

    def ProcessImage(self, name):
        path_name = name
        # path_name = sys.argv[1]

        stream = open(path_name, 'rb')
        bytes = bytearray(stream.read())
        array = np.asarray(bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)

        #image = cv2.imread(path_name)
        #print(path_name)
        file_name = os.path.basename(path_name)
        filename, ext = file_name.split(".")

        h, w = image.shape[:2]
        # create 4D blob
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (699, 699), swapRB=True, crop=False)

        # sets the blob as the input of the network
        self.net.setInput(blob)

        # get all the layer names
        ln = self.net.getLayerNames()
        ln = [ln[i - 1] for i in self.net.getUnconnectedOutLayers()]
        # feed forward (inference) and get the network output
        # measure how much it took in seconds
        start = time.perf_counter()
        layer_outputs = self.net.forward(ln)
        time_took = time.perf_counter() - start
        #print(f"Time took: {time_took:.2f}s")

        boxes, confidences, class_ids = [], [], []

        # loop over each of the layer outputs
        for output in layer_outputs:
            # loop over each of the object detections
            for detection in output:
                # extract the class id (label) and confidence (as a probability) of
                # the current object detection
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                # discard weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > self.CONFIDENCE:
                    # scale the bounding box coordinates back relative to the
                    # size of the image, keeping in mind that YOLO actually
                    # returns the center (x, y)-coordinates of the bounding
                    # box followed by the boxes' width and height
                    box = detection[:4] * np.array([w, h, w, h])
                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.SCORE_THRESHOLD, self.IOU_THRESHOLD)
        return len(idxs) > 0
