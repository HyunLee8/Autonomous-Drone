from openai import OpenAI
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def transcribe_audio(audio_file):

    try:
        print(f"Transcribing audio file: {audio_file.filename}")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_path = temp_file.name
        
        audio_file.save(temp_path)
        temp_file.close()
        
        file_size = os.path.getsize(temp_path)
        print(f"Saved to temp file: {temp_path}")
        print(f"File size: {file_size} bytes")
        
        if file_size < 5000: 
            os.unlink(temp_path)
            return None
        
        with open(temp_path, 'rb') as audio:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",
                language="en", 
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
                print(f"Detected hallucination keyword '{keyword}' in: '{transcription}'")
                return None
        
        if len(transcription) < 3:
            print(f"Transcription too short: '{transcription}'")
            return None
        
        if not any(c.isalnum() for c in transcription):
            print(f"No alphanumeric characters: '{transcription}'")
            return None
        
        ascii_count = sum(1 for c in transcription if ord(c) < 128)
        if len(transcription) > 5 and ascii_count / len(transcription) < 0.5:
            print(f"⚠️ Mostly non-English characters: '{transcription}'")
            return None
        
        print(f"Transcription successful: '{transcription}'")
        return transcription
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass
        return None