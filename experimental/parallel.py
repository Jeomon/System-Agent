import argparse
from uiautomation import Control, GetRootControl, ControlFromHandle,ControlsAreSame, ControlFromPoint
from multiprocessing import Pool, cpu_count
import json

INTERACTIVE_CONTROL_TYPE_NAMES = [
    'ButtonControl', 'ListItemControl', 'MenuItemControl', 'DocumentControl',
    'EditControl', 'CheckBoxControl', 'RadioButtonControl', 'ComboBoxControl',
    'HyperlinkControl', 'SplitButtonControl', 'TabItemControl', 'MenuItemControl',
    'TreeItemControl', 'DataItemControl', 'HeaderItemControl', 'ImageControl',
    'TextBoxControl'
]

# Define the function to process a node
def process_node(node_handle):
    node = ControlFromHandle(node_handle)
    interactive_nodes = []

    def is_element_covered(element:Control):
        bounding_box = element.BoundingRectangle
        if not bounding_box:
            return False  # If there's no bounding box, assume it's not covered
        # Calculate the center point of the element
        center_x = bounding_box.xcenter()
        center_y = bounding_box.ycenter()
        # Find the top-most element at the center point
        try:
            top_element = ControlFromPoint(center_x, center_y)
        except Exception as e:
            print(f"Error fetching element from point: {e}")
            return False
        # If no top element is found, assume the element is not covered
        if top_element is None:
            return False
        # Check if the top element is inside the current element
        is_inside = ControlsAreSame(element, top_element)
        # If the top element is the same as the given element, it's not covered
        if is_inside:
            return False
        return True

    def is_interactive(control: Control):
        # Define your logic for interactive controls
        return control.ControlTypeName in INTERACTIVE_CONTROL_TYPE_NAMES and control.IsEnabled

    def traverse(control: Control):
        if is_interactive(control):
            bounding_box = control.BoundingRectangle
            interactive_nodes.append({
                "name": control.Name,
                "control_type": control.ControlTypeName,
                "bounding_box": {
                    "left": bounding_box.left,
                    "top": bounding_box.top,
                    "right": bounding_box.right,
                    "bottom": bounding_box.bottom,
                },
                'center': {
                    'x': bounding_box.xcenter(),
                    'y': bounding_box.ycenter(),
                },
            })
        for child in control.GetChildren():
            traverse(child)

    traverse(node)
    return interactive_nodes

# Main function for parallel traversal
def parallel_traversal():
    root = GetRootControl()
    children = root.GetChildren()

    # Get the handles of the child nodes
    node_handles = [child.NativeWindowHandle for child in children if child.NativeWindowHandle]

    # Use multiprocessing pool
    with Pool(cpu_count()) as pool:
        results = pool.map(process_node, node_handles)

    # Combine results from all processes
    interactive_nodes = [node for result in results for node in result]
    return interactive_nodes

# Set up the command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="UI Automation Interactive Elements Scraper")
    parser.add_argument(
        '--output', 
        type=str, 
        required=True, 
        help="Path to save the output JSON file"
    )
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Get interactive elements
    interactive_elements = parallel_traversal()

    # Write the interactive elements to the file provided by the user
    with open(args.output, 'w') as file:
        json.dump(interactive_elements, file, indent=4)
