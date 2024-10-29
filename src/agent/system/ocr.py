from easyocr import Reader

reader=Reader(['en'],gpu=False)

def get_xyxy(input):
    x, y, xp, yp = input[0][0], input[0][1], input[2][0], input[2][1]
    x, y, xp, yp = int(x), int(y), int(xp), int(yp)
    return x, y, xp, yp

def ocr(image):
    results = reader.readtext(image, paragraph=False,text_threshold=0.8)
    bboxes = [get_xyxy(box[0]) for box in results]
    texts = [box[1] for box in results]  # Extract the OCR text
    return bboxes, texts