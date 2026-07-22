import React, { useEffect, useState } from 'react';
import RoomDashboard from './components/RoomDashboard';

export interface Device {
  id: string;
  name: string;
  type: string;
  state: boolean;
  value: number;
}

export type RoomState = Record<string, Device[]>;

function App() {
  const [rooms, setRooms] = useState<RoomState>({});
  const [wsStatus, setWsStatus] = useState<string>('Connecting...');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => setWsStatus('Connected');
    ws.onclose = () => setWsStatus('Disconnected');
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'INIT_STATE' || message.type === 'STATE_UPDATE') {
        setRooms(message.data);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Smart Home Hub</h1>
          <p className="text-slate-400 text-sm">Offline Voice Processing Active</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${wsStatus === 'Connected' ? 'bg-green-500' : 'bg-red-500' } animate-pulse`} />
          <span className="text-sm font-medium">{wsStatus}</span>
        </div>
      </header>

      <div className="space-y-8">
        {Object.entries(rooms).map(([roomName, devices]) => (
          <RoomDashboard key={roomName} roomName={roomName} devices={devices} />
        ))}
      </div>
    </div>
  );
}

export default App;