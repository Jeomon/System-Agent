from src.tool import tool
from pydantic import BaseModel, Field
import pyautogui as pg

class SingleClick(BaseModel):
    pass

@tool('Single Click Tool',args_schema=SingleClick)
def single_click_tool(label:str='',role:str='',name:str='',cordinate:tuple=()):
    x,y=cordinate
    pg.click(x=x,y=y,button='left',clicks=1)
    if role and name:
        return f'Single clicked the item {role} {name}.'
    else:
        return f'Single clicked the label {label}.'


class DoubleClick(BaseModel):
    pass

@tool('Double Click Tool',args_schema=DoubleClick)
def double_click_tool(label:str='',role:str='',name:str='',cordinate:tuple=()):
    x,y=cordinate
    pg.click(x=x,y=y,button='left',clicks=2)
    if role and name:
        return f'Double clicked the item {role} {name}.'
    else:
        return f'Double clicked the label {label}.'

class RightClick(BaseModel):
    pass

@tool('Right Click Tool',args_schema=RightClick)
def right_click_tool(label:str='',role:str='',name:str='',cordinate:tuple=()):
    x,y=cordinate
    pg.click(x=x,y=y,button='right')
    if role and name:
        return f'Right clicked the item {role} {name}.'
    else:
        return f'Right clicked the label {label}.'

class Type(BaseModel):
    pass

@tool('Type Tool',args_schema=Type)
def type_tool(label:str='',role:str='',name:str='',text:str=''):
    pg.typewrite(text)
    if role and name:
        return f'Typed {text} in {role} {name}.'
    else:
        return f'Typed {text} in {label}.'
    
class Scroll(BaseModel):
    pass

@tool('Scroll Tool',args_schema=Scroll)
def scroll_tool(direction:str='',amount:int=0):
    if direction=='up':
        pg.scroll(amount)
    else:
        pg.scroll(-amount)
    return f'Scrolled  {direction} by {amount}.'

class Shortcut(BaseModel):
    pass

@tool('Shortcut Tool',args_schema=Shortcut)
def shortcut_tool(shortcut:str=''):
    pg.hotkey(*shortcut.split('+'))
    return f'Shortcut {shortcut} triggered.'

class Key(BaseModel):
    pass

@tool('Key Tool',args_schema=Key)
def key_tool(key:str=''):
    pg.press(key)
    return f'Pressed {key}.'

class Move(BaseModel):
    pass

@tool('Move Tool',args_schema=Move)
def move_tool(x,y):
    pg.moveTo(x=x,y=y,duration=1)
    return f'Cursor moved to the specified location.'
