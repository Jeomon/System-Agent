from dataclasses import dataclass,field

@dataclass
class TreeState:
    nodes:list['TreeElementNode']=field(default_factory=[])
    selector_map:dict[int,'TreeElementNode']=field(default_factory={})

@dataclass
class DesktopState:
    screenshot:bytes
    tree_state:TreeState

@dataclass
class BoundingBox:
    left:int
    top:int
    right:int
    bottom:int

@dataclass
class CenterCord:
    x:int
    y:int

@dataclass
class TreeElementNode:
    name:str
    control_type:str
    bounding_box:BoundingBox
    center:CenterCord

    def __repr__(self):
        return f'TreeElementNode(name={self.name},control_type={self.control_type},bounding_box={self.bounding_box},center={self.center})'