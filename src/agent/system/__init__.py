from src.agent.system.tools import single_click_tool,double_click_tool,right_click_tool,type_tool,scroll_tool,shortcut_tool,key_tool
from src.agent.system.utils import read_markdown_file,extract_llm_response
from src.message import HumanMessage,SystemMessage,AIMessage,ImageMessage
from src.agent.system.ally_tree import ally_tree_and_coordinates
from src.agent.system.ocr import ocr_and_coordinates
from src.agent.system.yolo import yolo_and_coordinates
from langgraph.graph import StateGraph,START,END
from src.agent.system.state import AgentState
from src.inference import BaseInference
from src.agent import BaseAgent
from datetime import datetime
from termcolor import colored
from ultralytics import YOLO
import uiautomation as auto
from typing import Literal
from easyocr import Reader
from pathlib import Path
from json import dumps
from time import sleep
from io import BytesIO
from PIL import Image
import numpy as np
import cv2 as cv
import pyautogui
import platform

pyautogui.FAILSAFE=False
pyautogui.PAUSE=2.5

class SystemAgent(BaseAgent):
    def __init__(self,llm:BaseInference=None,verbose:bool=False,strategy:Literal['ocr','yolo','ally_tree',]='ally_tree',screenshot=False,max_iteration:int=10) -> None:
        self.name='System Agent'
        self.description=''
        tools=[single_click_tool,double_click_tool,right_click_tool,type_tool,scroll_tool,shortcut_tool,key_tool]
        self.tool_names=[tool.name for tool in tools]
        self.tools={tool.name:tool for tool in tools}
        self.strategy=strategy
        self.system_prompt=read_markdown_file(f'src/agent/system/prompt/{self.strategy}.md')
        self.graph=self.create_graph()
        self.max_iteration=max_iteration
        self.reader=Reader(['en'],gpu=False)
        self.yolo_model=YOLO(model='./models/best.pt')
        self.screenshot=screenshot
        self.verbose=verbose
        self.iteration=0
        self.llm=llm

    def find_element_by_role_and_name(self,state:AgentState,role:str,name:str):
        x,y=None,None
        for bbox in state.get('bboxes'):
            if bbox.get('role')==role and bbox.get('name')==name:
                x,y=bbox.get('x'),bbox.get('y')
                break
        if x is None or y is None:
            raise Exception('Role and Name is invalid')
        return x,y
    
    def find_element_by_label(self,state:AgentState,label:str):
        x,y=None,None
        for bbox in state.get('bboxes'):
            if bbox.get('label')==label:
                x,y=bbox.get('x'),bbox.get('y')
                break
        if x is None or y is None:
            raise Exception('Label is invalid')
        return x,y

    def reason(self,state:AgentState):
        # print(state.get('messages'))
        ai_message=self.llm.invoke(state.get('messages'))
        # print(ai_message.content)
        agent_data=extract_llm_response(ai_message.content)
        # print(dumps(agent_data,indent=2))
        if self.verbose:
            thought=agent_data.get('Thought')
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'messages':[ai_message],'agent_data': agent_data}

    def action(self,state:AgentState):
        agent_data=state.get('agent_data')
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        tool=self.tools[action_name]
        if self.strategy in['ocr','ally_tree']:
            try:
                if action_name=='Single Click Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    cordinate=self.find_element_by_role_and_name(state,role,name)
                    observation=tool(role=role,name=name,cordinate=cordinate)
                elif action_name=='Double Click Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    cordinate=self.find_element_by_role_and_name(state,role,name)
                    observation=tool(role=role,name=name,cordinate=cordinate)
                elif action_name=='Right Click Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    cordinate=self.find_element_by_role_and_name(state,role,name)
                    observation=tool(role=role,name=name,cordinate=cordinate)
                elif action_name=='Type Tool':
                    role=action_input.get('role')
                    name=action_input.get('name')
                    text=action_input.get('text')
                    observation=tool(role=role,name=name,text=text)
                elif action_name=='Scroll Tool':
                    direction=action_input.get('direction')
                    amount=action_input.get('amount')
                    observation=tool(direction,amount)
                elif action_name=='Shortcut Tool':
                    shortcut=action_input.get('shortcut')
                    observation=tool(shortcut)
                elif action_name=='Key Tool':
                    key=action_input.get('key')
                    observation=tool(key)
                elif action_name=='MoveTo Tool':
                    w,h=state.get('resolution')
                    x=float(action_input.get('x_percent'))*w
                    y=float(action_input.get('y_percent'))*h
                    observation=tool(int(x),int(y))
                else:
                    raise Exception('Tool not found.')
            except Exception as error:
                observation=error
        elif self.strategy=='yolo':
            try:
                if action_name=='Single Click Tool':
                    label_number=action_input.get('label_number')
                    cordinate=self.find_element_by_label(state,label_number)
                    observation=tool(label=label_number,cordinate=cordinate)
                elif action_name=='Double Click Tool':
                    label_number=action_input.get('label_number')
                    cordinate=self.find_element_by_label(state,label_number)
                    observation=tool(label=label_number,cordinate=cordinate)
                elif action_name=='Right Click Tool':
                    label_number=action_input.get('label_number')
                    cordinate=self.find_element_by_label(state,label_number)
                    observation=tool(label=label_number,cordinate=cordinate)
                elif action_name=='Type Tool':
                    label_number=action_input.get('label_number')
                    text=action_input.get('text')
                    observation=tool(label=label_number,text=text)
                elif action_name=='Scroll Tool':
                    direction=action_input.get('direction')
                    amount=action_input.get('amount')
                    observation=tool(direction,amount)
                elif action_name=='Shortcut Tool':
                    shortcut=action_input.get('shortcut')
                    observation=tool(shortcut)
                elif action_name=='Key Tool':
                    key=action_input.get('key')
                    observation=tool(key)
                else:
                    raise Exception('Tool not found.')
            except Exception as error:
                observation=error
        else:
            raise Exception('Strategy not found.')
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        root=auto.GetRootControl()
        state['messages'].pop() # Remove last message
        last_message=state.get('messages')[-1]
        sleep(10) #To prevent from hitting api limit
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            if self.iteration==1:
                content=f'Query:{state.get('input')}'
            else:
                content=f'<Observation>{state.get('previous_observation')}</Observation>'
            state['messages'][-1]=HumanMessage(content)
        ai_message=AIMessage(f'<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>')
        screenshot=pyautogui.screenshot()
        if self.screenshot:
            self.save_screenshot(screenshot)
        if self.strategy=='ally_tree':
            ally_tree,bboxes=ally_tree_and_coordinates(root)
            # print(ally_tree)
            image_bytes=self.screenshot_in_bytes(screenshot=screenshot)
            prompt=f'Ally Tree:\n{ally_tree}\n\nNow analyze the A11y Tree and Screenshot for gathering information and decide whether to act or answer based on the ally tree.'
            human_message=ImageMessage(text=f'<Observation>{observation}\n\n{prompt}</Observation>',image_bytes=image_bytes)
        elif self.strategy=='ocr':
            ally_tree,bboxes=ocr_and_coordinates(root,self.reader,self.llm,screenshot)
            # print(ally_tree)
            image_bytes=self.screenshot_in_bytes(screenshot=screenshot)
            prompt=f'Ally Tree:\n{ally_tree}\n\nNow analyze the A11y Tree and Screenshot for gathering information and decide whether to act or answer based on the ally tree.'
            human_message=ImageMessage(text=f'<Observation>{observation}\n\n{prompt}</Observation>',image_bytes=image_bytes)
        elif self.strategy=='yolo':
            label_screenshot,bboxes=yolo_and_coordinates(self.yolo_model,screenshot)
            image_bytes=self.screenshot_in_bytes(screenshot=label_screenshot)
            prompt=f'Now analyze the labeled screenshot for gathering information and decide whether to act or answer.'
            human_message=ImageMessage(text=f'<Observation>{observation}\n\n{prompt}</Observation>',image_bytes=image_bytes)
        else:
            raise Exception('Strategy not found.')
        messages=[ai_message,human_message]
        return {**state,'agent_data':agent_data,'messages':messages,'bboxes':bboxes,'previous_observation':observation}

    def screenshot_in_bytes(self,screenshot):
        screenshot=self.include_cursor(screenshot)
        io=BytesIO()
        screenshot.save(io,format='PNG')
        image_bytes=io.getvalue()
        return image_bytes
    
    def include_cursor(self,screenshot,dot_color=(0, 0, 255), dot_radius=5):
        screenshot = np.array(screenshot)
        cursor_x, cursor_y = pyautogui.position()
        cv.circle(screenshot, (cursor_x, cursor_y), dot_radius, dot_color, -1)
        return Image.fromarray(screenshot)
    
    def save_screenshot(self,screenshot):
        date_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        path = Path('./screenshots')
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        file_path = path.joinpath(f'screenshot_{date_time}.png').as_posix()
        screenshot.save(file_path, format='PNG')

    def final(self,state:AgentState):
        agent_data=state.get('agent_data')
        if self.iteration<self.max_iteration:
            final_answer=agent_data.get('Final Answer')
        else:
            final_answer='Maximum Iteration Reached'
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer}

    def controller(self,state:AgentState):
        if self.iteration<self.max_iteration:
            self.iteration+=1
            agent_data=state.get('agent_data')
            return agent_data.get('Route').lower()
        else:
            return 'final'    

    def create_graph(self):
        graph=StateGraph(AgentState)
        graph.add_node('reason',self.reason)
        graph.add_node('action',self.action)
        graph.add_node('final',self.final)

        graph.add_edge(START,'reason')
        graph.add_conditional_edges('reason',self.controller)
        graph.add_edge('action','reason')
        graph.add_edge('final',END)

        return graph.compile(debug=False)

    def invoke(self,input:str):
        root=auto.GetRootControl()
        screenshot=pyautogui.screenshot()
        if self.strategy=='ally_tree':
            if self.screenshot:
                self.save_screenshot(screenshot)
            ally_tree,bboxes=ally_tree_and_coordinates(root)
            image_bytes=self.screenshot_in_bytes(screenshot=screenshot)
            human_message=ImageMessage(image_bytes=image_bytes,text=f'User Query: {input}\n\nAlly Tree:\n{ally_tree}\nNow analyze the A11y Tree and Screenshot for gathering information and decide whether to act or answer based on the ally tree.')
        elif self.strategy=='ocr':
            if self.screenshot:
                self.save_screenshot(screenshot)
            ally_tree,bboxes=ocr_and_coordinates(root,self.reader,self.llm,screenshot)
            image_bytes=self.screenshot_in_bytes(screenshot=screenshot)
            human_message=ImageMessage(image_bytes=image_bytes,text=f'User Query: {input}\n\nAlly Tree:\n{ally_tree}\nNow analyze the A11y Tree and Screenshot for gathering information and decide whether to act or answer based on the ally tree.')
        elif self.strategy=='yolo':
            if self.screenshot:
                self.save_screenshot(label_screenshot)
            label_screenshot,bboxes=yolo_and_coordinates(self.yolo_model,screenshot)
            image_bytes=self.screenshot_in_bytes(screenshot=label_screenshot)
            human_message=ImageMessage(image_bytes=image_bytes,text=f'User Query: {input}\n\nNow analyze the labeled screenshot for gathering information and decide whether to act or answer.')
        else:
            raise Exception('Strategy not found.')
        parameters={
            'os':platform.platform(),
            'width':screenshot.width,
            'height':screenshot.height
        }
        system_message=SystemMessage(self.system_prompt.format(**parameters))
        state={
            'input':input,
            'output':'',
            'agent_data':{},
            'bboxes':bboxes,
            'resolution': (screenshot.width,screenshot.height),
            'messages':[system_message,human_message],
        }
        agent_response=self.graph.invoke(state)
        return agent_response['output']

    def stream(self,input:str):
        pass