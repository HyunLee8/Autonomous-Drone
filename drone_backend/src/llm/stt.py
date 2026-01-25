from openai import OpenAI
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

def transcribe_audio(audio_file):
    """
    Transcribe audio file using OpenAI's Whisper API
    
    Args:
        audio_file: FileStorage object from Flask request
        
    Returns:
        str: Transcribed text or None if error/silence
    """
    try:
        print(f"Transcribing audio file: {audio_file.filename}")
        
        # Save the uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_path = temp_file.name
        
        # Write the uploaded file content to temp file
        audio_file.save(temp_path)
        temp_file.close()
        
        file_size = os.path.getsize(temp_path)
        print(f"Saved to temp file: {temp_path}")
        print(f"File size: {file_size} bytes")
        
        # If file is too small, it's likely just noise
        if file_size < 5000:  # Less than 5KB is probably silence
            print("⚠️ File too small - likely silence")
            os.unlink(temp_path)
            return None
        
        # Open the temp file and send to OpenAI with language hint
        with open(temp_path, 'rb') as audio:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",
                language="en",  # Force English to prevent foreign language hallucinations
            )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        transcription = response.text.strip()
        
        # Comprehensive hallucination filter (all languages)
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
        
        # Check if it contains ANY hallucination keyword
        for keyword in hallucination_keywords:
            if keyword in transcription or keyword in transcription_lower:
                print(f"⚠️ Detected hallucination keyword '{keyword}' in: '{transcription}'")
                return None
        
        # If transcription is too short (likely noise)
        if len(transcription) < 3:
            print(f"⚠️ Transcription too short: '{transcription}'")
            return None
        
        # If transcription is just punctuation or whitespace
        if not any(c.isalnum() for c in transcription):
            print(f"⚠️ No alphanumeric characters: '{transcription}'")
            return None
        
        # Check if it's mostly non-English characters (unexpected for your use case)
        ascii_count = sum(1 for c in transcription if ord(c) < 128)
        if len(transcription) > 5 and ascii_count / len(transcription) < 0.5:
            print(f"⚠️ Mostly non-English characters: '{transcription}'")
            return None
        
        print(f"✅ Transcription successful: '{transcription}'")
        return transcription
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.unlink(temp_path)
        except:
            pass
        return None