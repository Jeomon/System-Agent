from src.agent.system.tools.views import Click,Type,Scroll,Shortcut,Key
from src.agent.system.desktop import Desktop
from typing import Literal
from src.tool import Tool
import pyautogui as pg

@Tool('Click Tool',params=Click)
def click_tool(index:int,button:Literal['left','right','middle']='left',clicks:int=1,desktop:Desktop=None):
    '''Clicks on the element at the specified index.'''
    element=desktop.get_element_by_index(index)
    center_cord=element.center
    pg.click(x=center_cord.x,y=center_cord.y,button=button,clicks=clicks)
    num_clicks={1:'Single',2:'Double',3:'Triple'}
    return f'{num_clicks.get(clicks)} {button} clicked on the element at index {index}.'

@Tool('Type Tool',params=Type)
def type_tool(index:int,text:str,desktop:Desktop=None):
    '''Types the specified text on the element at the specified index.'''
    element=desktop.get_element_by_index(index)
    center_cord=element.center
    pg.click(x=center_cord.x,y=center_cord.y,button='left',clicks=1)
    pg.typewrite(text,interval=0.1)
    return f'Typed {text} on the element at index {index}.'

@Tool('Scroll Tool',params=Scroll)
def scroll_tool(direction:Literal['up','down']='',amount:int=0,desktop:Desktop=None):
    '''Scrolls the screen up or down by the specified amount.'''
    if direction=='up':
        pg.scroll(amount)
    else:
        pg.scroll(-amount)
    return f'Scrolled  {direction} by {amount}.'

@Tool('Shortcut Tool',params=Shortcut)
def shortcut_tool(shortcut:list[str],desktop:Desktop=None):
    '''Presses a combination of keys in the shortcut to perform that action.'''
    pg.hotkey(*shortcut)
    return f'Pressed {'+'.join(shortcut)}.'

@Tool('Key Tool',params=Key)
def key_tool(key:str='',desktop:Desktop=None):
    '''Presses the specified key.'''
    pg.press(key)
    return f'Pressed the key {key}.'
