
'use client'

import TextType from '@/components/TextType';
import Link from 'next/link';
import { useState } from 'react';

export default function Home() {
  const [isTakingOff, setIsTakingOff] = useState(false);
  const [showProcess, setShowProcess] = useState(false);

  const handleTakeoff = () => {
    setIsTakingOff(true);
    setTimeout(() => setShowProcess(true), 1000);
  }

  return (
    <div className="flex flex-col min-h-screen items-center justify-center font-sans dark:bg-black">
      <Link href="resources" className="fixed top-5 font-bold">Resources</Link>
      <h1 className="fixed top-5 right-5 text-6xl">GAZER</h1>
      <h2 className="fixed bottom-5 right-5 text-sm">Developed by Isaac Lee and Aryan Thind</h2>
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
      <div className="z-10 text-center relative">
        <div className={`transition-opacity duration-1000 ${isTakingOff ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
          <div className="flex flex-col items-center justify-center gap-8">
            <h2 className="text-5xl">Click below to <span className="font-bold">Activate</span></h2>
            <button onClick={handleTakeoff} className="py-5 px-10 border border-black bg-black text-white z-10 duration-500 hover:bg-white hover:text-black">Initiate Takeoff</button>
          </div>
        </div>
        {showProcess && (
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center gap-8">
            <h2 className="text-5xl">
              <TextType
                text={["Taking off..."]}
                typingSpeed={100}
                pauseDuration={1500}
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