from src.inference.groq import AudioGroq,ChatGroq
from src.inference.gemini import ChatGemini
from src.agent.system import SystemAgent
from dotenv import load_dotenv
from src.speech import Speech
import os

load_dotenv()
google_api_key=os.getenv('GOOGLE_API_KEY')
groq_api_key=os.getenv('GROQ_API_KEY')

# LLMs used
llm=ChatGemini(model='gemini-2.0-flash-exp',api_key=google_api_key,temperature=0)
speech_llm=AudioGroq(model='whisper-large-v3',mode='translations',api_key=groq_api_key,temperature=0)

# Initialize Web Agent
agent=SystemAgent(llm=llm,use_vision=True,verbose=True)

mode=input('Enter the mode of input (text/voice): ')
if mode=='text':
    user_query=input('Enter your query: ')
elif mode=='voice':
    speech=Speech(llm=speech_llm)
    user_query=speech.invoke()
    print(f'Enter your query: {user_query.content}')
else:
    raise Exception('Invalid mode of input. Please enter either text or voice.')
agent_response=agent.invoke(user_query)
print(agent_response)