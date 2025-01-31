from src.agent.system.tree.views import TreeElementNode,BoundingBox,CenterCord,TreeState
from uiautomation import GetRootControl,Control,ControlFromPoint,ControlsAreSame
from src.agent.system.tree.config import INTERACTIVE_CONTROL_TYPE_NAMES
from PIL import Image,ImageDraw,ImageFont
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from src.agent.system.desktop import Desktop

class Tree:
    def __init__(self,desktop:'Desktop'):
        self.desktop=desktop

    def get_state(self,use_vision:bool=False)->tuple[bytes,TreeState]:
        root=GetRootControl()
        nodes=self.get_interactive_nodes(node=root)
        if use_vision:
            screenshot=self.mark_screen(nodes=nodes,save_screenshot=True)
        else:
            screenshot=None
        selector_map=self.build_selector_map(nodes=nodes)
        return (screenshot,TreeState(nodes=nodes,selector_map=selector_map))

    def get_interactive_nodes(self, node: Control) -> list[TreeElementNode]:
        interactive_nodes = []

        def is_element_covered(node: Control):
            bounding_box = node.BoundingRectangle
            if not bounding_box:
                return False  # If there's no bounding box, assume it's not covered
            # Calculate the center point of the element
            center_x = bounding_box.xcenter()
            center_y = bounding_box.ycenter()
            # Find the top-most element at the center point
            try:
                top_node = ControlFromPoint(center_x, center_y)
            except Exception as e:
                print(f"Error fetching element from point: {e}")
                return False
            if top_node is None:
                return False
            if ControlsAreSame(node, top_node):  # If same, it's not covered
                return False
            return True
        
        def is_window_minimized(node: Control):
            return node.ControlTypeName == 'WindowControl' and node.IsMinimize()

        def is_element_interactive(node: Control):
            return node.ControlTypeName in INTERACTIVE_CONTROL_TYPE_NAMES

        def tree_traversal(node: Control):
            if is_window_minimized(node):
                return None
            if not node.IsEnabled:
                return None
            # if is_element_covered(node):
            #     return None
            # Check if it has interactive children
            interactive_childrens = []
            for child in node.GetChildren():
                if is_element_interactive(child):
                    interactive_childrens.append(child)

            if is_element_interactive(node) and interactive_childrens:
                # If both the parent and children are interactive, only include the children
                for child in interactive_childrens:
                    tree_traversal(child)
            else:
                # If no interactive children, include this node
                if is_element_interactive(node):
                    box = node.BoundingRectangle
                    bounding_box = BoundingBox(
                        left=box.left, top=box.top, right=box.right, bottom=box.bottom
                    )
                    center = CenterCord(x=box.xcenter(), y=box.ycenter())
                    interactive_nodes.append(TreeElementNode(
                        name=node.Name.strip(),
                        control_type=node.ControlTypeName,
                        bounding_box=bounding_box,
                        center=center,
                        handle=node
                    ))
                # Recursively check all children
                for child in node.GetChildren():
                    tree_traversal(child)

        tree_traversal(node)
        return interactive_nodes

    def get_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def mark_screen(self,nodes:list[TreeElementNode],save_screenshot:bool=False)->bytes:
        screenshot_bytes=self.desktop.get_screenshot()
        screenshot=Image.open(screenshot_bytes).convert('RGB')
        # Include padding to the screenshot
        padding=20
        width=screenshot.width+(2*padding)
        height=screenshot.height+(2*padding)
        padded_screenshot=Image.new("RGB", (width, height), color=(255, 255, 255))
        padded_screenshot.paste(screenshot, (padding,padding))
        # Create a layout above the screenshot to place bounding boxes.
        draw=ImageDraw.Draw(padded_screenshot)
        font_size=12
        try:
            font=ImageFont.truetype('arial.ttf',font_size)
        except:
            font=ImageFont.load_default()
        for label,node in enumerate(nodes):
            box=node.bounding_box
            color=self.get_random_color()
            # Adjust bounding box to fit padded image
            adjusted_box = (
                box.left + padding, box.top + padding,  # Adjust top-left corner
                box.right + padding, box.bottom + padding  # Adjust bottom-right corner
            )
            # Draw bounding box around the element in the screenshot
            draw.rectangle(adjusted_box,outline=color,width=2)
            
            # Get the size of the label
            label_width=draw.textlength(str(label),font=font,font_size=font_size)
            label_height=font_size
            left,top,right,bottom=adjusted_box
            # Position the label above the bounding box and towards the right
            label_x1 = right - label_width  # Align the right side of the label with the right edge of the box
            label_y1 = top - label_height - 4  # Place the label just above the top of the bounding box, with some padding

            # Draw the label background rectangle
            label_x2 = label_x1 + label_width
            label_y2 = label_y1 + label_height + 4  # Add some padding

            # Draw the label background rectangle
            draw.rectangle([(label_x1, label_y1), (label_x2, label_y2)], fill=color)

            # Draw the label text
            text_x = label_x1 + 2  # Padding for text inside the rectangle
            text_y = label_y1 + 2
            draw.text((text_x, text_y), str(label), fill=(255, 255, 255), font=font)

        if save_screenshot:
            self.desktop.save_screenshot(padded_screenshot)
        return self.desktop.screenshot_in_bytes(padded_screenshot)

    def build_selector_map(self, nodes: list[TreeElementNode]) -> dict[int, TreeElementNode]:
        return {index:node for index,node in enumerate(nodes)}