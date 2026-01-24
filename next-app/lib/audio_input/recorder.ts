export async function RecordAudio() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  const chunks: Blob[] = [];
 
 
  // Setup silence detection
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();
  const microphone = audioContext.createMediaStreamSource(stream);
  analyser.fftSize = 256;
  microphone.connect(analyser);
  const dataArray = new Uint8Array(analyser.frequencyBinCount);
 
 
  let silenceStart: number | null = null;
  const SILENCE_THRESHOLD = 30;
  const SILENCE_DURATION = 3000;
 
 
  const checkSilence = () => {
    analyser.getByteFrequencyData(dataArray);
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
 
 
    if (average < SILENCE_THRESHOLD) {
      if (!silenceStart) silenceStart = Date.now();
      else if (Date.now() - silenceStart > SILENCE_DURATION) {
        mediaRecorder.stop();
        return;
      }
    } else {
      silenceStart = null;
    }
 
 
    if (mediaRecorder.state === 'recording') {
      requestAnimationFrame(checkSilence);
    }
  };
 
 
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
 
 
  return new Promise((resolve, reject) => {
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(chunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', audioBlob);
 
 
      try {
        const response = await fetch('http://localhost:5000/api/process', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        stream.getTracks().forEach(track => track.stop());
        audioContext.close();
        resolve(data);
      } catch (error) {
        reject(error);
      }
    };
 
 
    mediaRecorder.start();
    checkSilence();
  });
 }
 