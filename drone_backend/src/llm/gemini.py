from google import genai
import json
import os
from .systems_prompt import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

# Initialize the client with API key
client = genai.Client(api_key=os.getenv('GEMINI_KEY'))

def get_agent_response(user_req):
    """
    Generate a response from the Gemini model based on user request.
    
    Args:
        user_req (str): The user's request/query
        
    Returns:
        dict: JSON response containing the agent's response and actions
    """
    try:
        # Combine system prompt and user request
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {user_req}"
        
        # Generate content with JSON response format
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type='application/json',
            )
        )
        
        # Parse and return the JSON response
        data = json.loads(response.text)
        print(f"✅ LLM Response: {data}")
        return data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
        return {
            "response": "I encountered an error parsing the response.",
            "actions": []
        }
    except Exception as e:
        print(f"❌ Error in get_agent_response: {e}")
        import traceback
        traceback.print_exc()
        return {
            "response": "I encountered an error processing your request.",
            "actions": []
        }