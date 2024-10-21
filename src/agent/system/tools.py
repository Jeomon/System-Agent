from src.tool import tool
from pydantic import BaseModel, Field
import pyautogui as pg

class SingleClick(BaseModel):
    pass

@tool('Single Click Tool',args_schema=SingleClick)
def single_click_tool(role:str,name:str,cordinate:tuple):
    x,y=cordinate
    pg.click(x=x,y=y,button='left',clicks=1)
    return f'Single clicked the item {role} {name}.'

class DoubleClick(BaseModel):
    pass

@tool('Double Click Tool',args_schema=DoubleClick)
def double_click_tool(role:str,name:str,cordinate:tuple):
    x,y=cordinate
    pg.click(x=x,y=y,button='left',clicks=2)
    return f'Double clicked the item {role} {name}.'

class RightClick(BaseModel):
    pass

@tool('Right Click Tool',args_schema=RightClick)
def right_click_tool(role:str,name:str,cordinate:tuple):
    x,y=cordinate
    pg.click(x=x,y=y,button='right')
    return f'Right clicked the item {role} {name}.'

class Type(BaseModel):
    pass

@tool('Type Tool',args_schema=Type)
def type_tool(role:str,name:str,text:str):
    pg.typewrite(text)
    return f'Typed {text} in {role} {name}.'

class Scroll(BaseModel):
    pass

@tool('Scroll Tool',args_schema=Scroll)
def scroll_tool(direction:str,amount:int):
    if direction=='up':
        pg.scroll(amount)
    else:
        pg.scroll(-amount)
    return f'Scrolled  {direction} by {amount}.'

class Shortcut(BaseModel):
    pass

@tool('Shortcut Tool',args_schema=Shortcut)
def shortcut_tool(shortcut:str):
    pg.hotkey(*shortcut.split('+'))
    return f'Shortcut {shortcut} triggered.'

class Key(BaseModel):
    pass

@tool('Key Tool',args_schema=Key)
def key_tool(key_name:str):
    pg.press(key_name)
    return f'Pressed {key_name}.'
