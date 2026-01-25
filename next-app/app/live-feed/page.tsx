/* eslint-disable @next/next/no-img-element */
'use client';

import TextType from '@/components/TextType';
import DroneData from '@/components/DroneData';
import Link from 'next/link';

export default function LiveFeedPage() {
  return (
    <div className="flex flex-col min-h-screen items-center justify-center font-sans dark:bg-black">
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
      <Link href="/" className="fixed top-5 font-bold">Back</Link>
      <div className="flex flex-col gap-10 z-10">
          <div className="flex">
            <img
              src="http://127.0.0.1:5000/api/video-tracking"
              alt="Drone video feed"
              className="border-4 border-white rounded-4xl"
              width={480}
              height={360}
            />
            <div className="fixed left-5">
              <DroneData />
            </div>
          </div>
      </div>
    </div>
  );
}