import random
import cv2
import numpy as np
from PIL import Image

def box_area(box):
    return (box[2] - box[0]) * (box[3] - box[1])

def intersection_area(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    return max(0, x2 - x1) * max(0, y2 - y1)

def IoU(box1, box2):
    intersection = intersection_area(box1, box2)
    union = box_area(box1) + box_area(box2) - intersection + 1e-6
    if box_area(box1) > 0 and box_area(box2) > 0:
        ratio1 = intersection / box_area(box1)
        ratio2 = intersection / box_area(box2)
    else:
        ratio1, ratio2 = 0, 0
    return max(intersection / union, ratio1, ratio2)

def get_random_color():
    return tuple([random.randint(0, 255) for _ in range(3)])

def model_predict(model, image):
    # Run YOLO model on the padded image
    results = model.predict(image, conf=0.01)  # Note: Pass the original image (without padding) to the model
    boxes = results[0].boxes.xyxy.cpu().numpy()  # Bounding box coordinates (x1, y1, x2, y2)
    return boxes

def filter_boxes(boxes):
    # Filter out overlapping bounding boxes
    filtered_boxes = []
    for i, box1 in enumerate(boxes):
        is_valid_box = True
        for j, box2 in enumerate(boxes):
            if i != j and IoU(box1, box2) > 0.4 and box_area(box1) > box_area(box2):
                is_valid_box = False
                break
        if is_valid_box:
            filtered_boxes.append(box1)
    return filter_boxes

def yolo_and_coordinates(model,image):
    # Padding to ensure labels and boxes fit within the image
    padding=50
    coordinates=[]
    image=np.array(image)
    image_padded = cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    boxes=model_predict(model,image)
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
        coordinates.append(dict(label=label,x=(x1+x2)//2,y=(y1+y1)//2))
    return Image.fromarray(image_padded),coordinates