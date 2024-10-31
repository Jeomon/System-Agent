from src.inference.gemini import ChatGemini
from src.message import HumanMessage,ImageMessage,SystemMessage
from experiments.ally_tree import ally_tree_and_coordinates
from easyocr import Reader
from dotenv import load_dotenv
import uiautomation as auto
import os
import re

load_dotenv()

def get_cxcy(input):
    x1, y1, x2, y2 = input[0][0], input[0][1], input[2][0], input[2][1]
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    # Calculate the center coordinates
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    
    return cx, cy

ocr = Reader(['en'], gpu=True)
image_path = 'screen.png'
results = ocr.readtext(image_path, paragraph=False)
ocr_data = {box[1]:get_cxcy(box[0]) for box in results}
texts = [box[1] for box in results]

api_key=os.getenv('GOOGLE_API_KEY')
llm=ChatGemini(model='gemini-1.5-flash',api_key=api_key,temperature=0)
system_prompt='''
You are provided with:
1. **A screenshot** of a user interface.
2. **An accessibility tree** corresponding to that screenshot, structured hierarchically, with elements arranged in a window-wise or desktop-based order.
3. **OCR scan results** from the screenshot that contain text elements missing in the accessibility tree.

Your task is to **update the accessibility tree** by:
- Understanding the elements visible in the screenshot.
- Identifying the text elements from the OCR results that are missing in the accessibility tree.
- Accurately integrating these missing text elements into their appropriate locations within the accessibility tree based on the screenshot's visual structure. Ensure the hierarchical structure of the accessibility tree is preserved, and the new textual elements are correctly placed within the appropriate parent-child relationships.

Make sure the updated accessibility tree reflects all visual elements from the screenshot, ensuring that the tree is comprehensive and complete.
NOTE: There should nothing else other than the accessibility tree in plain text. Also don't include unwanted elements in the tree from the OCR data only what is most appropriate based on the screenshot.
'''
ally_tree,cordinates=ally_tree_and_coordinates(auto.GetRootControl())
updated_ally_tree=llm.invoke([
    SystemMessage(system_prompt),
    ImageMessage(image_path='screen.png',text=f'OCR Text\n{texts}\nAlly Tree:\n{ally_tree}\n Now give me the updated ally tree'),
]).content

import re

def parse_alley_tree(tree_str):
    tree_elements = []
    # Split the string by lines
    lines = tree_str.strip().split('\n')
    for line in lines:
        # Extract role and name from the line (assuming format like: "Role: ButtonControl, Name: Close")
        match = re.search(r"Role:\s*(\w+Control),\s*Name:\s*(.+)", line.strip())
        if match:
            role = match.group(1).strip()
            name = match.group(2).strip()
            tree_elements.append({
                'role': role,
                'name': name
            })
    return tree_elements

def find_missing_elements(original_tree, updated_tree):
    original_set = {(el['role'], el['name']) for el in original_tree}
    updated_set = {(el['role'], el['name']) for el in updated_tree}
    # Find elements that are in the updated tree but not in the original tree
    missing_elements = updated_set - original_set
    return missing_elements


def create_mapping_from_missing_elements(missing_elements, ocr_data):
    mapping = {}
    
    for role, name in missing_elements:
        # If the name exists in OCR data, create the mapping
        if name in ocr_data:
            mapping[(role, name)] = ocr_data[name]
    return mapping


original=parse_alley_tree(ally_tree)
updated=parse_alley_tree(updated_ally_tree)
missing_elements = find_missing_elements(original, updated)
mapping = create_mapping_from_missing_elements(missing_elements, ocr_data)
print(mapping)