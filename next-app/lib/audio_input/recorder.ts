export async function RecordAudio(): Promise<unknown> {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    
    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });
    
    const chunks: Blob[] = [];

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const microphone = audioContext.createMediaStreamSource(stream);
    analyser.fftSize = 512;
    microphone.connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    let silenceStart: number | null = null;
    const SILENCE_THRESHOLD = 40;
    const SILENCE_DURATION = 2000;
    const MAX_RECORDING_TIME = 10000;
    const recordingStartTime = Date.now();

    const checkAudio = () => {
      if (mediaRecorder.state !== 'recording') return;

      analyser.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      const elapsedTime = Date.now() - recordingStartTime;

      if (elapsedTime > MAX_RECORDING_TIME) {
        console.log('Max recording time reached');
        mediaRecorder.stop();
        return;
      }

      if (average < SILENCE_THRESHOLD) {
        if (!silenceStart) {
          silenceStart = Date.now();
        } else if (Date.now() - silenceStart > SILENCE_DURATION) {
          console.log('Silence detected, stopping');
          mediaRecorder.stop();
          return;
        }
      } else {
        silenceStart = null;
      }

      requestAnimationFrame(checkAudio);
    };

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };

    return new Promise((resolve) => {
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        
        stream.getTracks().forEach(track => track.stop());
        audioContext.close();

        if (audioBlob.size < 5000) {
          console.log('Audio too small, skipping');
          resolve({ 
            success: false, 
            error: 'Audio too short',
            transcription: ''
          });
          return;
        }

        const formData = new FormData();
        const audioFile = new File([audioBlob], 'audio.webm', { type: 'audio/webm' });
        formData.append('audio', audioFile);

        console.log('Sending audio, size:', audioBlob.size);

        try {
          const response = await fetch('http://127.0.0.1:5000/api/llm', {
            method: 'POST',
            body: formData
          });
          const data = await response.json();
          resolve(data);
        } catch (error) {
          console.error('Fetch error:', error);
          resolve({ 
            success: false, 
            error: (error as Error).message,
            transcription: ''
          });
        }
      };

      mediaRecorder.onerror = () => {
        stream.getTracks().forEach(track => track.stop());
        audioContext.close();
        resolve({ 
          success: false, 
          error: 'Recording error',
          transcription: ''
        });
      };

      console.log('Recording started');
      mediaRecorder.start();
      checkAudio();
    });
  } catch (error) {
    console.error('Microphone access error:', error);
    return {
      success: false,
      error: 'Microphone access denied',
      transcription: ''
    };
  }
}