from ultralytics import YOLO
import cv2
import config

class ObjectDetector:
    def __init__(self):
        print(f"Loading YOLO model: {config.YOLO_MODEL_PATH}")
        # Initialize YOLOv8 model
        self.model = YOLO(config.YOLO_MODEL_PATH)
        self.latest_detections = []
        
    def process_frame(self, frame):
        """
        Runs YOLO inference on a single frame.
        Returns the annotated frame and list of detected classes.
        """
        # Run inference
        results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
        
        detections = []
        
        # Parse results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                detections.append(class_name)
        
        self.latest_detections = detections
        
        # Get annotated image
        annotated_frame = results[0].plot()
        return annotated_frame, detections
    
    def get_latest_detections(self):
        return self.latest_detections
