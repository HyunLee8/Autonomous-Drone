import { ElevenLabsClient } from '@elevenlabs/elevenlabs-js';
export async function POST(request: Request) {
  const { text } = await request.json();
  const elevenlabs = new ElevenLabsClient({
    apiKey: process.env.ELEVENLABS_API_KEY
  });
  const audio = await elevenlabs.textToSpeech.convert('uyVNoMrnUku1dZyVEXwD', {
    text: text,
    modelId: 'eleven_multilingual_v2',
    outputFormat: 'mp3_44100_128',
  });
  const chunks: Uint8Array[] = [];
  const reader = audio.getReader();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  const audioBuffer = Buffer.concat(chunks);
  return new Response(audioBuffer, {
    headers: {
      'Content-Type': 'audio/mpeg',
      'Content-Length': audioBuffer.length.toString(),
    },
  });
}