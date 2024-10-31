from easyocr import Reader

def get_xyxy(input):
    x, y, xp, yp = input[0][0], input[0][1], input[2][0], input[2][1]
    x, y, xp, yp = int(x), int(y), int(xp), int(yp)
    return (x, y, xp, yp)

def get_cxcy(input):
    x1, y1, x2, y2 = input[0][0], input[0][1], input[2][0], input[2][1]
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return (cx, cy)

def ocr(reader:Reader,image):
    results = reader.readtext(image, paragraph=False,text_threshold=0.8)
    ocr_data = {box[1]:get_cxcy(box[0]) for box in results}
    texts = [box[1] for box in results]  # Extract the OCR text
    return ocr_data, texts

