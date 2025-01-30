from src.inference.gemini import ChatGemini
from src.agent.system import SystemAgent
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv('GOOGLE_API_KEY')
llm=ChatGemini(model='gemini-2.0-flash-exp',api_key=api_key,temperature=0)

agent=SystemAgent(instructions=[],llm=llm,use_vision=True,verbose=True)
user_query=input('Enter your query: ')
agent_response=agent.invoke(user_query)
print(agent_response)