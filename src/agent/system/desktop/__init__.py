from src.agent.system.desktop.views import DesktopState,App
from pygetwindow import getActiveWindow,getAllWindows
from src.agent.system.tree import Tree,TreeElementNode
from io import BytesIO
from PIL import Image
import pyautogui

class Desktop:
    def __init__(self):
        self.desktop_state=None
    def get_state(self,use_vision:bool=False):
        tree=Tree(self)
        active_window=getActiveWindow()
        active_app=active_window.title
        windows=getAllWindows()
        apps=[App(name=window.title,is_maximized=window.isMaximized,is_minimized=window.isMinimized) for window in windows]
        screenshot,tree_state=tree.get_state(use_vision=use_vision)
        self.desktop_state=DesktopState(active_app=active_app,apps=apps,screenshot=screenshot,tree_state=tree_state)
        return self.desktop_state
    
    def get_element_by_index(self,index:int)->TreeElementNode:
        selector_map=self.desktop_state.tree_state.selector_map
        if index not in selector_map:
            raise ValueError(f'Invalid index {index}')
        return selector_map.get(index)
    
    def get_screenshot(self)->BytesIO:
        screenshot=pyautogui.screenshot()
        screenshot_bytes=self.screenshot_in_bytes(screenshot)
        return BytesIO(screenshot_bytes)
    
    def screenshot_in_bytes(self,screenshot:Image)->bytes:
        io=BytesIO()
        screenshot.save(io,format='PNG')
        bytes=io.getvalue()
        return bytes