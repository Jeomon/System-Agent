import re
import ast

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r',encoding='utf-8') as f:
        markdown_content = f.read()
    return markdown_content

def extract_llm_response(text):
    # Dictionary to store extracted values
    result = {}
    # Check if it's Option 1 (Action-based)
    if re.search(r"<Action-Name>", text):
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()
        # Extract Action-Name
        action_name_match = re.search(r"<Action-Name>(.*?)<\/Action-Name>", text, re.DOTALL)
        if action_name_match:
            result['Action Name'] = action_name_match.group(1).strip()
        # Extract and convert Action-Input to a dictionary
        action_input_match = re.search(r"<Action-Input>(.*?)<\/Action-Input>", text, re.DOTALL)
        if action_input_match:
            action_input_str = action_input_match.group(1).strip()
            try:
                # Convert string to dictionary safely using ast.literal_eval
                result['Action Input'] = ast.literal_eval(action_input_str.replace("{{","{").replace("}}","}"))
            except (ValueError, SyntaxError):
                # If there's an issue with conversion, store it as raw string
                result['Action Input'] = action_input_str
        # Extract Route (should always be 'Action' in Option 1)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
    # Check if it's Option 2 (Final Answer)
    elif re.search(r"<Final-Answer>", text):
        # Extract Thought
        thought_match = re.search(r"<Thought>(.*?)<\/Thought>", text, re.DOTALL)
        if thought_match:
            result['Thought'] = thought_match.group(1).strip()
        # Extract Final Answer
        final_answer_match = re.search(r"<Final-Answer>(.*?)<\/Final-Answer>", text, re.DOTALL)
        if final_answer_match:
            result['Final Answer'] = final_answer_match.group(1).strip()
        # Extract Route (should always be 'Final' in Option 2)
        route_match = re.search(r"<Route>(.*?)<\/Route>", text, re.DOTALL)
        if route_match:
            result['Route'] = route_match.group(1).strip()
    return result

def parse_ally_tree(tree_str):
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
    mapping = []
    for role, name in missing_elements:
        # If the name exists in OCR data, create the mapping
        if name in ocr_data:
            x,y=ocr_data[name][0],ocr_data[name][1]
            mapping.append(dict(role=role, name=name, x=x, y=y))
    return mapping