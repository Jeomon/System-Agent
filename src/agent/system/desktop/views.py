from src.agent.system.tree.views import TreeState
from dataclasses import dataclass

@dataclass
class App:
    name:str
    depth:int
    is_maximized:bool
    is_minimized:bool

@dataclass
class DesktopState:
    active_app:str
    apps:list[App]
    screenshot:bytes|None
    tree_state:TreeState

    def apps_to_string(self):
        return '\n'.join([f'{i+1} - App Name: {app.name} - Depth: {app.depth} -  Is Minimized: {app.is_minimized} - Is Maximized: {app.is_maximized}' for (i,app) in enumerate(self.apps)])