from uiautomation import Control,GetRootControl,ControlFromHandle
from multiprocessing import Pool, cpu_count

INTERACTIVE_CONTROL_TYPE_NAMES=[
    'ButtonControl','ListItemControl','MenuItemControl,DocumentControl',
    'EditControl','CheckBoxControl', 'RadioButtonControl','ComboBoxControl',
    'HyperlinkControl','SplitButtonControl','TabItemControl','MenuItemControl',
    'TreeItemControl','DataItemControl','HeaderItemControl','ImageControl',
    'TextBoxControl'
]

# Define the function to process a node
def process_node(node_handle):
    node = ControlFromHandle(node_handle)
    interactive_nodes = []

    def is_interactive(control:Control):
        # Define your logic for interactive controls
        return control.ControlTypeName in INTERACTIVE_CONTROL_TYPE_NAMES and control.IsEnabled

    def traverse(control:Control):
        if is_interactive(control):
            bounding_box = control.BoundingRectangle
            interactive_nodes.append({
                'name': control.Name,
                'control_type': control.ControlTypeName,
                'bounding_box': {
                    'left': bounding_box.left,
                    'top': bounding_box.top,
                    'right': bounding_box.right,
                    'bottom': bounding_box.bottom,
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
    print(node_handles)

    # Use multiprocessing pool
    with Pool(cpu_count()) as pool:
        results = pool.map(process_node, node_handles)

    # Combine results from all processes
    interactive_nodes = [node for result in results for node in result]
    return interactive_nodes

if __name__ == "__main__":
    interactive_elements = parallel_traversal()
    print(interactive_elements)
