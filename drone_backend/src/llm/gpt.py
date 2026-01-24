import os
from .systems_prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def get_agent_response(user_req):
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_req}
        ]
        response_format={"type": "json"}
    )