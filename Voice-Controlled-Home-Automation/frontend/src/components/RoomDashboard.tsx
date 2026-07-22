import React from 'react';
import type { Device } from '../App';
import DeviceCard from './DeviceCard';

interface Props {
  roomName: string;
  devices: Device[];
}

const RoomDashboard: React.FC<Props> = ({ roomName, devices }) => {
  // Format room name (e.g., "living_room" -> "Living Room")
  const formattedName = roomName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());

  return (
    <div className="bg-slate-800 rounded-xl p-6 shadow-lg border border-slate-700">
      <h2 className="text-xl font-semibold mb-4 text-indigo-400">{formattedName}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {devices.map(device => (
          <DeviceCard key={device.id} device={device} />
        ))}
      </div>
    </div>
  );
};

export default RoomDashboard;