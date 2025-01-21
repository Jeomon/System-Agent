from pydantic import BaseModel,Field
from typing import Literal

class SharedBaseModel(BaseModel):
    class Config:
        extra='allow'

class Click(SharedBaseModel):
    index:int=Field(...,description="The index of the element to click on.",examples=[0])
    button:Literal['left','right','middle']=Field(description='The button to click on the element.',default='left',examples=['left'])
    clicks:int=Field(description="The number of times to click on the element.",default=2,examples=[1])

class Type(SharedBaseModel):
    index:int=Field(...,description="The index of the element to type on.",examples=[0])
    text:str=Field(...,description="The text to type on the element.",examples=['hello world'])

class Scroll(SharedBaseModel):
    direction:Literal['up','down']=Field(...,description="The direction of the scroll.",examples=['down'])
    amount:int=Field(...,description="The amount of the scroll.",examples=[100])

class Shortcut(SharedBaseModel):
    shortcut:list[str]=Field(...,description="The shortcut to execute by pressing the keys.",examples=[['ctrl','a'],['alt','f4']])

class Key(SharedBaseModel):
    key:str=Field(...,description="The key to press.",examples=['enter'])