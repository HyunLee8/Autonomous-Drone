from openai import OpenAI
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def transcribe_audio(audio_file):
    try:        
=        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_path = temp_file.name
        
        audio_file.save(temp_path)
        temp_file.close()
        
        file_size = os.path.getsize(temp_path)
        
        if file_size < 5000: 
            os.unlink(temp_path)
            return None
        with open(temp_path, 'rb') as audio:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",
                language="en",  # Force English to prevent foreign language hallucinations
            )
        os.unlink(temp_path)
        transcription = response.text.strip()
        hallucination_keywords = [
            'thank',
            'watching',
            'subscribe',
            'like',
            '감사합니다',  # Korean: thank you
            '시청',        # Korean: watching
            'gracias',    # Spanish: thank you
            'merci',      # French: thank you
            'danke',      # German: thank you
            '谢谢',       # Chinese: thank you
            'ありがとう',  # Japanese: thank you
            '♪',
            '[music]',
            '[applause]',
            'subtitles',
            '...',
        ]
        
        transcription_lower = transcription.lower()
        for keyword in hallucination_keywords:
            if keyword in transcription or keyword in transcription_lower:
                return None
        if len(transcription) < 3:
            return None
        
        if not any(c.isalnum() for c in transcription):
            return None
        
        ascii_count = sum(1 for c in transcription if ord(c) < 128)
        if len(transcription) > 5 and ascii_count / len(transcription) < 0.5:
            return None
        return transcription
        
    except Exception as e:
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass
        return None