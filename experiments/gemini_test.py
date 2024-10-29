from src.inference.gemini import ChatGemini
from src.message import HumanMessage,ImageMessage,SystemMessage
from easyocr import Reader
from dotenv import load_dotenv
from experiments.ally_tree import ally_tree_and_coordinates
import os
import cv2
import uiautomation as auto
import json
import re
import ast

load_dotenv()

def get_cxcy(input):
    x1, y1, x2, y2 = input[0][0], input[0][1], input[2][0], input[2][1]
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    # Calculate the center coordinates
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    
    return cx, cy

ocr = Reader(['en'], gpu=False)
image = cv2.imread('screen.png')
results = ocr.readtext(image, paragraph=False)
ocr_boxes = {box[1]:get_cxcy(box[0]) for box in results}
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
NOTE: There should nothing else other than the accessibility tree in plain text.
'''
ally_tree,cordinates=ally_tree_and_coordinates(auto.GetRootControl())
response=llm.invoke([
    SystemMessage(system_prompt),
    ImageMessage(image_path='screen.png',text=f'OCR Text\n{texts}\nAlly Tree:\n{ally_tree}\n Now give me the updated ally tree'),
])

system_prompt='''
You are provided with the following:
1. **An updated accessibility tree** that contains the elements from the OCR data, structured properly.
2. **OCR data**, which includes text-to-coordinate mappings for elements in the screenshot.

Your task is to:
- **Create a mapping** between the role and name of each element (from the OCR data) in the accessibility tree and its associated coordinates (from the OCR data).
- Use the **accessibility tree** as a reference to identify the elements and roles.
- Focus only on mapping the **OCR content** to the coordinates. You do **not** need to create the full mapping for all elements in the accessibility tree, as an older version of the tree with mapped coordinates already exists. 

Your job is to:
- Compare the OCR data with the elements in the accessibility tree.
- For each matching OCR element, create a mapping between its **role**, **name**, and **coordinates** from the OCR data.

Respond in the following format:

```python
{
    ("role of the element in OCR data from the accessibility tree", "name of the element in OCR data from the accessibility tree"): coordinates from the OCR mapping,
    ......
}
```

Make sure to generate mappings only for the elements present in the OCR data and focus solely on updating the existing mapping with these new coordinates.
'''
response=llm.invoke([
    SystemMessage(system_prompt),
    HumanMessage(f'Ally Tree:\n{response.content}\nOCR:{ocr_boxes}\n.Now create the mapping for the ocr so that. I can combine with the mapping for the accessibility tree.'),
])

def extract_dict(text: str):
    pattern = r"```python(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        extracted_code = match.group(1).strip()  # Extract and strip any extra spaces
        try:
            # Convert the extracted string into a dictionary safely
            return ast.literal_eval(extracted_code)
        except (SyntaxError, ValueError):
            print("Error converting string to dictionary.")
            return None
    else:
        return None


def extract_dict_from_text(text: str):
    # Regex to match everything inside ```python and ```
    pattern = r"```python(.*?)```"
    
    # Use re.DOTALL to match across newlines
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        # Extract the dictionary content between the backticks
        dict_content = match.group(1).strip()
        
        try:
            # Safely convert the string to a dictionary using ast.literal_eval
            extracted_dict = ast.literal_eval(dict_content)
            return extracted_dict
        except (SyntaxError, ValueError) as e:
            print(f"Error converting to dictionary: {e}")
            return None
    else:
        print("No match found.")
        return None
    
print(extract_dict_from_text(response.content))