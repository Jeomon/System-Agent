from src.agent.system.desktop.views import DesktopState,App
from pygetwindow import getActiveWindow,getAllWindows
from src.agent.system.tree import Tree,TreeElementNode
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image
from os import getcwd
import pyautogui

class Desktop:
    def __init__(self):
        self.desktop_state=None
    def get_state(self,use_vision:bool=False):
        tree=Tree(self)
        active_window=getActiveWindow()
        active_app=active_window.title
        windows=self.get_windows_in_z_order()
        apps=[App(name=window.title,depth=depth,is_maximized=window.isMaximized,is_minimized=window.isMinimized) for depth,window in enumerate(windows)]
        screenshot,tree_state=tree.get_state(use_vision=use_vision)
        self.desktop_state=DesktopState(active_app=active_app,apps=apps,screenshot=screenshot,tree_state=tree_state)
        return self.desktop_state
    
    def get_element_by_index(self,index:int)->TreeElementNode:
        selector_map=self.desktop_state.tree_state.selector_map
        if index not in selector_map:
            raise ValueError(f'Invalid index {index}')
        return selector_map.get(index)
    
    def get_windows_in_z_order(self):
        # Get all open windows with titles
        windows = getAllWindows()
        # Sort windows based on their Z-order (front to back)
        # We'll use the "isActive" property to get the most front window
        sorted_windows = sorted([ window for window in windows if window.title.strip()], key=lambda w: w.isActive, reverse=True)
        return sorted_windows
    
    def get_screenshot(self)->BytesIO:
        screenshot=pyautogui.screenshot()
        screenshot_bytes=self.screenshot_in_bytes(screenshot)
        return BytesIO(screenshot_bytes)
    
    def screenshot_in_bytes(self,screenshot:Image)->bytes:
        io=BytesIO()
        screenshot.save(io,format='PNG')
        bytes=io.getvalue()
        return bytes
    
    def save_screenshot(self,screenshot:Image):
        date_time=datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        folder_path=Path(getcwd()).joinpath('./screenshots')
        folder_path.mkdir(parents=True,exist_ok=True)
        path=folder_path.joinpath(f'screenshot_{date_time}.png')
        screenshot.save(path.as_posix(),format='PNG')