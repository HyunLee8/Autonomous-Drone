from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def transcribe_audio(audio_file):
    try:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, audio_file.read(), audio_file.content_type),
            response_format="text",
        )
        print("Transcription response:", response)
        return response
    except Exception as e:
        print("Error during transcription:", e)
        return None