'use client';

import { useState, useEffect } from 'react';

export default function DroneStatus() {
  const [droneData, setDroneData] = useState<{
    forward: boolean;
    backward: boolean;
    left: boolean;
    right: boolean;
    up: boolean;
    down: boolean;
    center: boolean;
  } | null>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/logged-data');
        const data = await response.json();
        setDroneData(data);
      } catch (error) {
        console.error('Error fetching drone status:', error);
      }
    }, 100);

    return () => clearInterval(interval);
  }, []);

  if (!droneData) return <div>Loading Feed ...</div>;

  return (
    <div className="flex flex-col gap-5">
      <h1 className="font-bold">Drone Console</h1>
      <p>Forward: {droneData.forward ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
      <p>Backward: {droneData.backward ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
      <p>Left: {droneData.left ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
      <p>Right: {droneData.right ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
      <p>Up: {droneData.up ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
      <p>Down: {droneData.down ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
      <p>Center: {droneData.center ? <span className="text-green-500">True</span> : <span className="text-red-500">False</span>}</p>
    </div>
  );
}