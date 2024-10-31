import uiautomation as auto
import re

# List of common interactive control types (can be extended)
interactive_types = [
    'ButtonControl', 'EditControl', 'ComboBoxControl', 
    'CheckBoxControl', 'CheckBoxControl', 'RadioButtonControl', 
    'ListControl', 'SliderControl', 'TabControl', 'HyperlinkControl', 'ListItemControl'
]

# Function to check if the name is valid (contains only printable ASCII characters)
def is_valid_name(name):
    return bool(re.match(r'^[\x20-\x7E]*$', name))

def is_visible(bounding_rectangle, visible_area):
    """
    Check if any part of the bounding rectangle is within the visible area.
    """
    return not (bounding_rectangle.right <= visible_area.left or
                bounding_rectangle.left >= visible_area.right or
                bounding_rectangle.bottom <= visible_area.top or
                bounding_rectangle.top >= visible_area.bottom)

def build_a11y_tree(node: auto.PaneControl, app_name: str, level=0, tree_dict: dict = None, cordinates: dict = None):
    if tree_dict is None:
        tree_dict = {}
    if cordinates is None:
        cordinates = {}

    # Identify the application by checking the window title
    if node.ControlTypeName == 'WindowControl':
        app_name = node.Name  # Update the app_name when entering a new window
        bounding_rectangle = node.BoundingRectangle
        
        # Check if the window is visible on the screen
        if bounding_rectangle and is_visible(bounding_rectangle, auto.GetRootControl().BoundingRectangle):
            visible_window = True
        else:
            visible_window = False
    else:
        visible_window = True  # For elements inside a visible window

    indent = "  " * level

    if app_name and visible_window:
        # Initialize a tree string for the application if it doesn't exist
        if app_name not in tree_dict:
            tree_dict[app_name] = ""

        # Check if the control is interactive and has a valid name, and if it's visible
        if is_valid_name(node.Name) and node.Name:
            bounding_rectangle = node.BoundingRectangle
            if bounding_rectangle and not bounding_rectangle.isempty() and is_visible(bounding_rectangle, node.BoundingRectangle):
                x_center = bounding_rectangle.xcenter()
                y_center = bounding_rectangle.ycenter()

                # Add to coordinates dictionary
                cordinates[(app_name, node.ControlTypeName, node.Name)] = (x_center, y_center)
                
                # Add the tree representation of the interactive element
                tree_dict[app_name] += f"{indent}Role: {node.ControlTypeName}, Name: {node.Name}\n"

    # Recursively process children
    for child in node.GetChildren():
        build_a11y_tree(child, app_name, level + 1, tree_dict, cordinates)

    return tree_dict, cordinates


def ally_tree_and_coordinates(root):
    tree_representation,cordinates = build_a11y_tree(root, app_name="Desktop")
    tree_string=''
    mapping=[]

    for app, tree in tree_representation.items():
        tree_string+=f"\nApplication: {app}\n{tree}\n"
    
    for key, coord in cordinates.items():
        _, role, name = key
        x,y=coord
        mapping.append(dict(role=role, name=name, x=x, y=y))

    return tree_string, mapping