from src.agent.system.utils import parse_ally_tree,find_missing_elements,create_mapping_from_missing_elements
from src.agent.system.ally_tree import ally_tree_and_coordinates
from src.agent.system.utils import read_markdown_file
from src.message import SystemMessage,ImageMessage
from easyocr import Reader
from io import BytesIO
import pyautogui as pg
from PIL import Image
import numpy as np
import cv2 as cv

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


def screenshot_in_bytes(screenshot):
    io=BytesIO()
    screenshot.save(io,format='PNG')
    image_bytes=io.getvalue()
    return image_bytes

def ocr(reader:Reader,image):
    image = np.array(image)
    results = reader.readtext(image, paragraph=False,text_threshold=0.8)
    ocr_data = {box[1]:get_cxcy(box[0]) for box in results}
    texts = [box[1] for box in results]  # Extract the OCR text
    return ocr_data, texts


def ocr_and_coordinates(root,reader,llm,screenshot):
    prompt=read_markdown_file('./src/agent/system/prompt/update_ally_tree_ocr.md')
    original_ally_tree,bboxes=ally_tree_and_coordinates(root)
    ocr_data,texts=ocr(reader,screenshot)
    image_bytes=screenshot_in_bytes(screenshot)
    updated_ally_tree=llm.invoke([
        SystemMessage(prompt),      
        ImageMessage(image_bytes=image_bytes,text=f'OCR Text\n{texts}\nAlly Tree:\n{original_ally_tree}\n Now give me the updated ally tree')
    ]).content
    orignal=parse_ally_tree(original_ally_tree)
    updated=parse_ally_tree(updated_ally_tree)
    missing_elements=find_missing_elements(orignal,updated)
    more_bboxes=create_mapping_from_missing_elements(missing_elements,ocr_data)
    return updated_ally_tree,[*bboxes,*more_bboxes]
