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

    def get_interactive_nodes(self,node:Control)->list[TreeElementNode]:
        interactive_nodes=[]
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

        def tree_traversal(node:Control):
            # Avoid including the minimized windows interactive elements
            if node.ControlTypeName=='WindowControl' and node.IsMinimize():
                return None
            # Avoid including the disabled interactive elements
            if not node.IsEnabled:
                return None
            # Including the elements that are not interactive
            if node.ControlTypeName in INTERACTIVE_CONTROL_TYPE_NAMES:
                box=node.BoundingRectangle
                bounding_box=BoundingBox(**{
                    'left':box.left,
                    'top':box.top,
                    'right':box.right,
                    'bottom':box.bottom
                })
                center=CenterCord(**{
                    'x':box.xcenter(),
                    'y':box.ycenter()
                })
                interactive_nodes.append(TreeElementNode(**{
                    'name':node.Name.strip(),
                    'control_type':node.ControlTypeName,
                    'bounding_box':bounding_box,
                    "center":center,
                    "handle":node
                }))
                # return None
            for child in node.GetChildren():
                tree_traversal(child)
        tree_traversal(node)
        return interactive_nodes

    def get_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def mark_screen(self,nodes:list[TreeElementNode],save_screenshot:bool=False)->bytes:
        screenshot_bytes=self.desktop.get_screenshot()
        screenshot=Image.open(screenshot_bytes)
        draw=ImageDraw.Draw(screenshot)
        font_size=12
        try:
            font=ImageFont.truetype('arial.ttf',font_size)
        except:
            font=ImageFont.load_default()
        for label,node in enumerate(nodes):
            box=node.bounding_box
            color=self.get_random_color()

            # Draw bounding box around the element in the screenshot
            draw.rectangle((box.left,box.top,box.right,box.bottom),outline=color,width=2)
            
            # Get the size of the label
            label_width=draw.textlength(str(label),font=font,font_size=font_size)
            label_height=font_size

            # Position the label above the bounding box and towards the right
            label_x1 = box.right - label_width  # Align the right side of the label with the right edge of the box
            label_y1 = box.top - label_height - 4  # Place the label just above the top of the bounding box, with some padding

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
            self.desktop.save_screenshot(screenshot)
        return self.desktop.screenshot_in_bytes(screenshot)

    def build_selector_map(self, nodes: list[TreeElementNode]) -> dict[int, TreeElementNode]:
        return {index:node for index,node in enumerate(nodes)}