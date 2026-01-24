import TextType from '@/components/TextType';
import Link from 'next/link';

export default function Resources() {
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
        <div>
          <h1 className="gray-500 text-xs">Design</h1>
          <a className="text-3xl" href="https://motion.dev/">Framer Motion</a>
        </div>
        <div>
          <h1 className="gray-500 text-xs">Controls</h1>
          <a className="text-3xl" href="https://djitellopy.readthedocs.io/en/latest/">DJI Tellopy Docs</a>
        </div>
        <div>
          <h1 className="gray-500 text-xs">Natural Language</h1>
          <a className="text-3xl" href="https://platform.openai.com/docs/overview">Open AI API key</a>
        </div>
        <div>
          <h1 className="gray-500 text-xs">Segmentation & Detection</h1>
          <a className="text-3xl" href="https://docs.ultralytics.com/">Ultralytics YOLO</a>
        </div>
        <div>
          <h1 className="gray-500 text-xs">Audio output</h1>
          <a className="text-3xl" href="https://elevenlabs.io/docs/overview/intro">11ElevenLabs Docs</a>
        </div>
        <div>
          <h1 className="gray-500 text-xs">For vibing</h1>
          <a className="text-3xl" href="https://open.spotify.com/user/249lw9zwlh70b2wak8phnb9k9?si=2777a88c30a342ab">{"Spotify and Celcius"}</a>
        </div>
      </div>
    </div>
  )
}