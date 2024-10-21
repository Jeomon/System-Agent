from src.agent.system.tools import single_click_tool,double_click_tool,right_click_tool,type_tool,scroll_tool,shortcut_tool,key_tool
from src.agent.system.utils import read_markdown_file,extract_llm_response,extract_observation
from src.message import HumanMessage,SystemMessage,AIMessage
from src.agent.system.ally_tree import ally_tree_and_coordinates
from langgraph.graph import StateGraph,START,END
from src.agent.system.state import AgentState
from src.inference import BaseInference
from src.agent import BaseAgent
from termcolor import colored
import uiautomation as auto
from json import dumps
from time import sleep

class SystemAgent(BaseAgent):
    def __init__(self,llm:BaseInference=None,verbose:bool=False,max_iteration:int=10) -> None:
        self.name='System Agent'
        self.description=''
        tools=[single_click_tool,double_click_tool,right_click_tool,type_tool,scroll_tool,shortcut_tool,key_tool]
        self.tool_names=[tool.name for tool in tools]
        self.tools={tool.name:tool for tool in tools}
        self.system_prompt=read_markdown_file('src/agent/system/prompt.md')
        self.graph=self.create_graph()
        self.max_iteration=max_iteration
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
            raise Exception('Bounding Box not found')
        return x,y

    def reason(self,state:AgentState):
        llm_response=self.llm.invoke(state.get('messages'))
        # print(llm_response.content)
        agent_data=extract_llm_response(llm_response.content)
        # print(dumps(agent_data,indent=2))
        if self.verbose:
            thought=agent_data.get('Thought')
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data}

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
        if action_name=='Single Click Tool':
            role=action_input.get('role')
            name=action_input.get('name')
            cordinate=self.find_element_by_role_and_name(state,role,name)
            observation=tool(role,name,cordinate)
        elif action_name=='Double Click Tool':
            role=action_input.get('role')
            name=action_input.get('name')
            cordinate=self.find_element_by_role_and_name(state,role,name)
            observation=tool(role,name,cordinate)
        elif action_name=='Right Click Tool':
            role=action_input.get('role')
            name=action_input.get('name')
            cordinate=self.find_element_by_role_and_name(state,role,name)
            observation=tool(role,name,cordinate)
        elif action_name=='Type Tool':
            role=action_input.get('role')
            name=action_input.get('name')
            text=action_input.get('text')
            observation=tool(role,name,text)
        elif action_name=='Scroll Tool':
            direction=action_input.get('direction')
            amount=action_input.get('amount')
            observation=tool(direction,amount)
        elif action_name=='Shortcut Tool':
            shortcut=action_input.get('shortcut')
            observation=tool(shortcut)
        elif action_name=='Key Tool':
            key_name=action_input.get('key_name')
            observation=tool(key_name)
        else:
            raise Exception('Tool not found.')
        
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        sleep(10) #To prevent from hitting api limit
        root=auto.GetRootControl()
        ally_tree,bboxes=ally_tree_and_coordinates(root)
        last_human_message=state.get('messages')[-2]
        if isinstance(last_human_message,HumanMessage):
            text=extract_observation(last_human_message.content).split('\n\n')[0]
            state['messages'][-2]=HumanMessage(text)
        state['messages'].pop() # Remove last message
        ai_prompt=f'<Thought>{thought}</Thought>\n<Action-Name>{action_name}</Action-Name>\n<Action-Input>{dumps(action_input,indent=2)}</Action-Input>\n<Route>{route}</Route>'
        user_prompt=f'<Observation>{observation}\n\nNow analyze the A11y Tree for gathering information and decide whether to act or answer.\nAlly tree:\n{ally_tree}</Observation>'
        messages=[AIMessage(ai_prompt),HumanMessage(user_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages,'bboxes':bboxes}

    def final(self,state:AgentState):
        agent_data=state.get('agent_data')
        final_answer=agent_data.get('Final Answer')
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer}

    def controller(self,state:AgentState):
        agent_data=state.get('agent_data')
        return agent_data.get('Route').lower()

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
        ally_tree,bboxes=ally_tree_and_coordinates(root)
        user_prompt=f'User Query: {input}\n\nNow analyze the A11y Tree for gathering information and decide whether to act or answer.\nAlly Tree:\n{ally_tree}'
        state={
            'input':input,
            'output':'',
            'agent_data':{},
            'bboxes':bboxes,
            'messages':[SystemMessage(self.system_prompt),HumanMessage(user_prompt)],
        }
        agent_response=self.graph.invoke(state)
        return agent_response['output']

    def stream(self,input:str):
        pass