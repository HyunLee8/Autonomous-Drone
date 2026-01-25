'use client'
import TextType from '@/components/TextType';
import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import { SpeakWithElevenLabs } from '@/lib/speech/elevenlabs';
import { RecordAudio } from '@/lib/audio_input/recorder';

interface LLMResponse {
  success: boolean;
  response?: string;
  error?: string;
  transcription?: string;
  actions?: unknown[];
}

export default function Home() {
  const [isActive, setIsActive] = useState(false);
  const [takeoff, setTakeoff] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('Say "initiate flight" to begin...');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isHoldingButton, setIsHoldingButton] = useState(false);
  const [lastHeard, setLastHeard] = useState('');
  const recordingAbortController = useRef<AbortController | null>(null);

  const speakMessage = async (message: string) => {
    setCurrentMessage(message);
    setIsSpeaking(true);
    try {
      await SpeakWithElevenLabs(message);
    } catch (err) {
      console.error('Speech error:', err);
    } finally {
      setIsSpeaking(false);
    }
  };

  const startRecording = async () => {
    if (isListening || isProcessing || isSpeaking) return;

    setIsListening(true);
    console.log('Recording started...');

    try {
      const data = await RecordAudio() as LLMResponse;
      
      setIsListening(false);
      
      if (data.success && data.transcription && data.transcription.trim()) {
        setLastHeard(data.transcription);
        console.log('Heard:', data.transcription);
        
        const transcription = data.transcription.toLowerCase();
        
        // Check for wake phrase
        if (!isActive && (
          transcription.includes('initiate flight') || 
          transcription.includes('initiate fly') ||
          transcription.includes('initialize flight')
        )) {
          console.log('Wake phrase detected');
          await handleTakeoff();
        } 
        // Process commands after takeoff
        else if (isActive && data.response) {
          setIsProcessing(true);
          await speakMessage(data.response);
          setIsProcessing(false);
        }
      }
    } catch (err) {
      console.error('Voice error:', err);
      setIsListening(false);
      setIsProcessing(false);
    }
  };

  const handleTakeoff = async () => {
    setIsActive(true);
    setTimeout(() => setTakeoff(true), 1000);

    try {
      fetch('http://127.0.0.1:5000/api/takeoff', { method: 'POST' });
      setTimeout(() => {
        fetch('http://127.0.0.1:5000/api/start-tracking', { method: 'POST' });
      }, 100);
      
      await speakMessage('Preparing for takeoff...');
      await speakMessage('Takeoff complete. Ready for voice commands.');
    } catch (err) {
      console.error('Takeoff error:', err);
      await speakMessage('Error during takeoff sequence.');
    }
  };

  const killSwitch = async () => {
    try {
      await speakMessage('Emergency landing initiated. Shutting down.');
    } catch (err) {
      console.error('Shutdown error:', err);
    }
    
    fetch('http://127.0.0.1:5000/api/stop-tracking', { method: 'POST' });
    fetch('http://127.0.0.1:5000/api/land', { method: 'POST' });
    
    setTimeout(() => window.location.reload(), 2000);
  };

  // Handle button press/release
  const handleMouseDown = () => {
    setIsHoldingButton(true);
    startRecording();
  };

  const handleMouseUp = () => {
    setIsHoldingButton(false);
  };

  // Keyboard support (Space bar)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.repeat && !isHoldingButton) {
        e.preventDefault();
        setIsHoldingButton(true);
        startRecording();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault();
        setIsHoldingButton(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isHoldingButton, isListening, isProcessing, isSpeaking]);

  return (
    <div className="flex flex-col min-h-screen items-center justify-center font-sans dark:bg-black">
      <div className="fixed flex gap-20 text-center top-5">
        <Link href="resources" className="font-bold">Resources</Link>
        <Link href="demos" className="font-bold">Demos</Link>
        <Link href="live-feed" className="font-bold">Live Feed</Link>
        <button onClick={killSwitch} className="font-bold cursor-pointer">Land Drone</button>
      </div>
      <button onClick={killSwitch} className="fixed bottom-5 left-5 font-bold text-l">Fail Safe</button>
      <h1 className="fixed top-5 right-5 text-6xl">GAZER</h1>
      <h2 className="fixed bottom-5 right-5 text-l">Developed by Isaac Lee and Aryan Thind</h2>
      <h2 className="fixed top-5 left-5 text-xl">2026 Hoya Hacks at</h2>
      <div className="fixed top-13 left-5 font-bold text-xl">
        <TextType
          text="Washington D.C"
          typingSpeed={100}
          showCursor={true}
          cursorCharacter="|"
        />
      </div>

      {/* Voice status indicator */}
      <div className="fixed bottom-20 right-5 flex flex-col items-end gap-2">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${
            isListening ? 'bg-red-500 animate-pulse' : 
            isSpeaking ? 'bg-blue-500 animate-pulse' : 
            isProcessing ? 'bg-yellow-500 animate-pulse' :
            'bg-green-500'
          }`}></div>
          <span className="text-sm font-bold">
            {isListening ? 'Listening...' : 
             isSpeaking ? 'Speaking...' : 
             isProcessing ? 'Processing...' :
             'Ready'}
          </span>
        </div>
        {lastHeard && (
          <div className="text-xs text-gray-400 max-w-xs text-right">
            Heard: &quot;{lastHeard}&quot;
          </div>
        )}
      </div>

      {/* Push to Talk Button */}
      <button
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchStart={handleMouseDown}
        onTouchEnd={handleMouseUp}
        disabled={isProcessing || isSpeaking}
        className={`fixed bottom-10 left-1/2 -translate-x-1/2 w-24 h-24 rounded-full font-bold text-white transition-all ${
          isHoldingButton 
            ? 'bg-red-600 scale-110 shadow-2xl' 
            : 'bg-red-500 hover:bg-red-600 shadow-lg'
        } ${
          isProcessing || isSpeaking ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        }`}
      >
        {isListening ? 'HOLD' : 'HOLD'}
      </button>
      
      {/* Instructions */}
      <div className="fixed bottom-36 left-1/2 -translate-x-1/2 text-center">
        <p className="text-sm text-gray-400">Hold button or press SPACE to talk</p>
      </div>
      
      <div className="z-10 relative w-full max-w-2xl px-4">
        <div className={`transition-opacity duration-1000 ${isActive ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
          <div className="flex flex-col items-center justify-center gap-8">
            <h2 className="text-5xl text-center">Voice Command Ready</h2>
            <p className="text-2xl text-center opacity-70">Say &quot;Initiate Flight&quot; to begin</p>
          </div>
        </div>
        
        {takeoff && (
          <div className="flex flex-col items-center gap-8">
            <h2 className="min-w-max text-3xl text-center">
              <TextType
                key={currentMessage}
                text={currentMessage}
                typingSpeed={100}
                showCursor={true}
                cursorCharacter="|"
              />
            </h2>
          </div>
        )}
      </div>
    </div>
  );
}