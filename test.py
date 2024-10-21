import uiautomation as auto
import re

# List of common interactive control types (can be extended)
interactive_types = [
    'ButtonControl', 'EditControl', 'ComboBoxControl', 
    'CheckBoxControl', 'RadioButtonControl', 'ListControl',
    'SliderControl', 'TabControl', 'HyperlinkControl', 'ListItemControl'
]

# Function to check if the name is valid (contains only printable ASCII characters)
def is_valid_name(name):
    return bool(re.match(r'^[\x20-\x7E]*$', name))

def build_a11y_tree(node: auto.PaneControl, app_name: str, level=0, tree_dict: dict = None,cordinates: dict = None):
    if tree_dict is None:
        tree_dict = {}

    if cordinates is None:
        cordinates = {}

    # Identify the application by checking the window title
    if node.ControlTypeName == 'WindowControl':
        app_name = node.Name  # Update the app_name when entering a new window

    indent = "  " * level

    if app_name:
        # Initialize a tree string for the application if it doesn't exist
        if app_name not in tree_dict:
            tree_dict[app_name] = ""

        # Check if the control is interactive and has a valid name
        if node.ControlTypeName in interactive_types and is_valid_name(node.Name) and node.Name:
            bounding_rectangle = node.BoundingRectangle
            if bounding_rectangle and not bounding_rectangle.isempty():
                x_center = bounding_rectangle.xcenter()
                y_center = bounding_rectangle.ycenter()

                # Add to coordinates dictionary
                cordinates[(app_name, node.ControlTypeName, node.Name)] = (x_center, y_center)
        tree_dict[app_name] += f"{indent}Role: {node.ControlTypeName}, Name: {node.Name}\n"

    # Recursively process children
    for child in node.GetChildren():
        build_a11y_tree(child, app_name, level + 1, tree_dict,cordinates)

    return tree_dict,cordinates


root = auto.GetRootControl()

def ally_tree_and_coordinates(root):
    tree_representation,cordinates = build_a11y_tree(root, app_name="Desktop")
    tree_string=''
    mapping={}

    for app, tree in tree_representation.items():
        tree_string+=f"\nApplication: {app}\n{tree}\n"
    
    for key, coord in cordinates.items():
        app_name, role, name = key
        mapping[(role, name)] = coord

    return tree_string, mapping

ally,cord=ally_tree_and_coordinates(root)
print(ally,cord)
