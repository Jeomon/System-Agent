from src.agent.system.tools import click_tool,type_tool,scroll_tool,shortcut_tool,key_tool
from src.agent.system.utils import read_markdown_file,extract_agent_data
from src.message import HumanMessage,SystemMessage,AIMessage,ImageMessage
from langgraph.graph import StateGraph,START,END
from src.agent.system.state import AgentState
from src.agent.system.registry import Registry
from src.agent.system.desktop import Desktop
from src.inference import BaseInference
from src.agent import BaseAgent
from datetime import datetime
from termcolor import colored
from getpass import getuser
from pathlib import Path
import pyautogui
import platform
import json

pyautogui.FAILSAFE=False
pyautogui.PAUSE=2.5

tools=[
    click_tool,type_tool,
    scroll_tool,shortcut_tool,
    key_tool
]

class SystemAgent(BaseAgent):
    def __init__(self,instructions:list[str]=[],llm:BaseInference=None,use_vision:bool=False,max_iteration:int=10,verbose:bool=False,token_usage:bool=False) -> None:
        self.name='System Agent'
        self.description='The System Agent is an AI-powered automation tool designed to interact with the operating system. It simulates human actions, such as opening applications, clicking buttons, typing, scrolling, and performing other system-level tasks.'
        self.registry=Registry(tools)
        self.desktop=Desktop()
        self.instructions=self.format_instructions(instructions)
        self.system_prompt=read_markdown_file(f'./src/agent/system/prompt/system.md')
        self.human_prompt=read_markdown_file(f'./src/agent/system/prompt/human.md')
        self.ai_prompt=read_markdown_file(f'./src/agent/system/prompt/ai.md')
        self.graph=self.create_graph()
        self.max_iteration=max_iteration
        self.use_vision=use_vision
        self.token_usage=token_usage
        self.verbose=verbose
        self.iteration=0
        self.llm=llm

    def format_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    def reason(self,state:AgentState):
        ai_message=self.llm.invoke(state.get('messages'))
        agent_data=extract_agent_data(ai_message.content)
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'messages':[ai_message],'agent_data': agent_data,'route':route}

    def action(self,state:AgentState):
        agent_data=state.get('agent_data')
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        action_result=self.registry.execute(name=action_name,input=action_input,desktop=self.desktop)
        observation=action_result.content
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        state['messages'].pop() # Remove the last message (AI Message) for modification
        last_message=state['messages'][-1] #ImageMessage/HumanMessage
        if isinstance(last_message,ImageMessage) or isinstance(last_message,HumanMessage):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
        desktop_state=self.desktop.get_state(use_vision=self.use_vision)
        image_obj=desktop_state.screenshot
        ai_prompt=self.ai_prompt.format(thought=thought,action_name=action_name,action_input=json.dumps(action_input,indent=2),route=route)
        user_prompt=self.human_prompt.format(observation=observation,active_app=desktop_state.active_app,apps=desktop_state.apps_to_string(),interactive_elements=desktop_state.tree_state.elements_to_string())
        messages=[AIMessage(ai_prompt),ImageMessage(text=user_prompt,image_obj=image_obj) if self.use_vision else HumanMessage(user_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages,'prev_observation':observation}

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
            return state.get('route').lower()
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
        system_prompt=self.system_prompt.format(**{
            'instructions':self.instructions,
            'current_datetime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'actions_prompt':self.registry.actions_prompt(),
            'os':platform.system(),
            'home_dir':Path.home().as_posix(),
            'user':getuser()
        })
        desktop_state=self.desktop.get_state(use_vision=self.use_vision)
        image_obj=desktop_state.screenshot
        human_prompt=self.human_prompt.format(observation="No Action",active_app=desktop_state.active_app,apps=desktop_state.apps_to_string(),interactive_elements=desktop_state.tree_state.elements_to_string())
        messages=[SystemMessage(system_prompt)]+[HumanMessage(f'Task: {input}\n'),ImageMessage(text=human_prompt,image_obj=image_obj)] if self.use_vision else [HumanMessage(f'Task: {input}\n'),HumanMessage(human_prompt)]
        state={
            'input':input,
            'agent_data':{},
            'route':'',
            'output':'',
            'messages':messages
        }
        graph_response=self.graph.invoke(state)
        return graph_response.get('output')

    def stream(self,input:str):
        pass