import random
import cv2
import numpy as np
from PIL import Image

def box_area(box):
    return (box[2] - box[0]) * (box[3] - box[1])

def get_random_color():
    return tuple([random.randint(0, 255) for _ in range(3)])

def model_predict(model, image):
    # Run YOLO model on the image
    results = model.predict(image, conf=0.01)  # Note: Pass the original image (without padding) to the model
    boxes = results[0].boxes.xyxy.cpu().numpy()  # Bounding box coordinates (x1, y1, x2, y2)
    return boxes

def is_overlapping(box1, box2):
    x1_box1, y1_box1, x2_box1, y2_box1 = box1
    x1_box2, y1_box2, x2_box2, y2_box2 = box2

    # Check if there is no overlap
    if x1_box1 > x2_box2 or x1_box2 > x2_box1:
        return False
    if y1_box1 > y2_box2 or y1_box2 > y2_box1:
        return False

    return True

def filter_boxes(boxes):
    # Filter out overlapping bounding boxes
    filtered_boxes = []
    for i, box1 in enumerate(boxes):
        is_valid_box = True
        for j, box2 in enumerate(boxes):
            if i != j and is_overlapping(box1, box2) and box_area(box1) > box_area(box2):
                is_valid_box = False
                break
        if is_valid_box:
            filtered_boxes.append(box1)
    return filtered_boxes

def yolo_and_coordinates(model, image):
    # Padding to ensure labels and boxes fit within the image
    padding = 50
    coordinates = []
    image = np.array(image)
    
    # Add white padding to the image
    image_padded = cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    
    # Get bounding boxes from YOLO model
    boxes = model_predict(model, image)
    
    # Filter out overlapping boxes
    boxes = filter_boxes(boxes)
    
    # Draw bounding boxes and labels
    for idx, box in enumerate(boxes):
        # Generate a random color for the bounding box and label
        color = get_random_color()
        
        # Convert the box coordinates to integers and adjust for padding
        x1, y1, x2, y2 = map(int, box)
        x1, y1, x2, y2 = x1 + padding, y1 + padding, x2 + padding, y2 + padding  # Adjust coordinates for padding
        
        # Draw the bounding box
        cv2.rectangle(image_padded, (x1, y1), (x2, y2), color, 2)
        
        # Create a label with the same color as the bounding box background
        label = f"{idx + 1}"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        label_w, label_h = label_size
        
        # Draw the label box filled with the same color as the bounding box
        cv2.rectangle(image_padded, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
        
        # Put the label text with contrasting color
        cv2.putText(image_padded, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Store coordinates of the center of the bounding box
        coordinates.append(dict(label=label, x=(x1 + x2) // 2, y=(y1 + y2) // 2))
    
    return Image.fromarray(image_padded), coordinates
