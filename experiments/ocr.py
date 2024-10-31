import easyocr
import cv2
import matplotlib.pyplot as plt

ocr = easyocr.Reader(['en'], gpu=False)

# Load the image
image_path = 'screen.png'
image = cv2.imread(image_path)
h, w = image.shape[:2]  # Get the image dimensions (height, width)

def get_xyxy(input):
    x, y, xp, yp = input[0][0], input[0][1], input[2][0], input[2][1]
    x, y, xp, yp = int(x), int(y), int(xp), int(yp)
    return x, y, xp, yp

# OCR detection
results = ocr.readtext(image, paragraph=False,text_threshold=0.8)
ocr_boxes = [get_xyxy(box[0]) for box in results]
texts = [box[1] for box in results]  # Extract the OCR text

for box in ocr_boxes:
    x1, y1, x2, y2 = map(int, box)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Plot the image with the bounding boxes and text
plt.figure(figsize=(10, 10))
plt.imshow(image_rgb)
plt.axis('off')  # Turn off the axis labels
plt.show()