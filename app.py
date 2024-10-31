from src.inference.gemini import ChatGemini
from src.inference.mistral import ChatMistral
from src.inference.groq import ChatGroq
from src.agent.system import SystemAgent
from dotenv import load_dotenv
import os

load_dotenv()

# api_key=os.getenv('GROQ_API_KEY')
# llm=ChatGroq(model='llama-3.1-70b-versatile',api_key=api_key,temperature=0)

api_key=os.getenv('GOOGLE_API_KEY')
llm=ChatGemini(model='gemini-1.5-flash',api_key=api_key,temperature=0)

# api_key=os.getenv('MISTRAL_API_KEY')
# llm=ChatMistral(model='open-codestral-mamba',api_key=api_key,temperature=0)

agent=SystemAgent(llm=llm,verbose=True,strategy='screenshot')
user_query=input('Enter your query: ')
agent_response=agent.invoke(user_query)
print(agent_response)