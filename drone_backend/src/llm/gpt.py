from openai import OpenAI
import json
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
    data = json.loads(response.choices[0].message.content)
    return data

if __name__ == "__main__":
    app.run(debug=True, port=5000)