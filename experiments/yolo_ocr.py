from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import easyocr

# Load the YOLO model
model = YOLO('./models/best.pt') 

ocr = easyocr.Reader(['en'], gpu=False)

# Load the image
image_path = '1.png'
image = cv2.imread(image_path)
h, w = image.shape[:2]  # Get the image dimensions (height, width)

def get_xyxy(input):
    x, y, xp, yp = input[0][0], input[0][1], input[2][0], input[2][1]
    x, y, xp, yp = int(x), int(y), int(xp), int(yp)
    return x, y, xp, yp

# OCR detection
results = ocr.readtext(image, paragraph=False, text_threshold=0.8)
ocr_boxes = [get_xyxy(box[0]) for box in results]
texts = [box[1] for box in results]  # Extract the OCR text

# Run YOLO model on the image
results = model.predict(image, conf=0.01)
boxes = results[0].boxes.xyxy.cpu().numpy()  # Bounding box coordinates (x1, y1, x2, y2)
conf = results[0].boxes.conf.cpu().numpy()  # Confidence scores

# Define the area and IoU functions
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

# Filter out overlapping bounding boxes
filtered_boxes = []
if ocr_boxes:
    filtered_boxes.extend(ocr_boxes)

for i, box1 in enumerate(boxes):
    is_valid_box = True
    for j, box2 in enumerate(boxes):
        if i != j and IoU(box1, box2) > 0.4 and box_area(box1) > box_area(box2):
            is_valid_box = False
            break
    if is_valid_box:
        # Add to filtered_boxes if no significant overlap with OCR boxes
        if ocr_boxes:
            if not any(IoU(box1, box3) > 0.9 for k, box3 in enumerate(ocr_boxes)):
                filtered_boxes.append(box1)
            else:
                filtered_boxes.append(box1)

# Draw the filtered bounding boxes on the image
for box in filtered_boxes:
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green box for the filtered box

# Add the OCR text next to each bounding box
for (box, text) in zip(ocr_boxes, texts):
    x1, y1, x2, y2 = box
    cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)  # Blue text above the box

# Convert BGR to RGB for matplotlib display
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Plot the image with the bounding boxes and text
plt.figure(figsize=(10, 10))
plt.imshow(image_rgb)
plt.axis('off')  # Turn off the axis labels
plt.show()

print(filtered_boxes,texts)