'use client'
import TextType from '@/components/TextType';
import Link from 'next/link';
import { useState } from 'react';
import { SpeakWithElevenLabs } from '@/lib/speech/elevenlabs';

export default function Home() {
  const [isActive, setIsActive] = useState(false);
  const [takeoff, setTakeoff] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');

  const handleClick = async () => {
    setIsActive(true);
    setTimeout(() => setTakeoff(true), 1000);

    try {
      fetch('http://127.0.0.1:5000/api/takeoff', { method: 'POST' });
      fetch('http://127.0.0.1:5000/api/start-tracking', { method: 'POST' });
      setCurrentMessage('Preparing for takeoff...')
      await SpeakWithElevenLabs('Preparing for takeoff...');
    } catch (err) {
      console.error('Error during speech synthesis:', err);
    }
  }

  const killSwitch = async () => {
    window.location.reload();
    fetch('http://127.0.0.1:5000/api/stop-tracking', { method: 'POST' });
    fetch('http://127.0.0.1:5000/api/land', { method: 'POST' })
  }

  return (
    <div className="flex flex-col min-h-screen items-center justify-center font-sans dark:bg-black">
      <div className="fixed flex gap-20 text-center top-5">
        <Link href="resources" className="font-bold">Resources</Link>
        <Link href="demos" className="font-bold">Demos</Link>
        <Link href="live-feed" className="font-bold">Live Feed</Link>
        <button onClick={killSwitch} className="font-bold cursor-pointer">Kill Switch</button>
      </div>
      <h1 className="fixed top-5 right-5 text-6xl">GAZER</h1>
      <h2 className="fixed bottom-5 right-5 text-l">Developed by Isaac Lee and Aryan Thind</h2>
      <h2 className="fixed top-5 left-5 text-xl">2026 Hoya Hacks at</h2>
      <div className="fixed top-13 left-5 font-bold text-xl">
        <TextType
          text={["Washington D.C", "Georgetown University"]}
          typingSpeed={100}
          pauseDuration={1500}
          showCursor={true}
          cursorCharacter="|"
        />
      </div>
      <div className="z-10 relative">
        <div className={`transition-opacity duration-1000 ${isActive ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
          <div className="flex flex-col items-center justify-center gap-8">
            <h2 className="text-5xl">Initiate Takeoff</h2>
            <button onClick={handleClick} className="py-5 px-10 border border-black bg-black text-white z-10 duration-500 hover:bg-white hover:text-black">Launch Gazer</button>
          </div>
        </div>
        {takeoff && (
          <h2 className="min-w-max text-3xl absolute top-1/2 left-1/2 -translate-x-1/2 animate-fade-in">
            <TextType
              key={currentMessage}
              text={[currentMessage]}
              typingSpeed={100}
              pauseDuration={1500}
              showCursor={true}
              cursorCharacter="|"
            />
          </h2>
        )}
      </div>
    </div>
  );
}