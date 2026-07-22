import React from 'react';
import type { Device } from '../App';

interface Props {
  device: Device;
}

const DeviceCard: React.FC<Props> = ({ device }) => {
  return (
    <div className={`p-4 rounded-lg border transition-all duration-300 ${device.state ? 'bg-indigo-900/50 border-indigo-500' : 'bg-slate-700/50 border-slate-600'}`}>
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-medium text-lg">{device.name}</h3>
        <div className={`px-2 py-1 text-xs rounded-full font-bold ${device.state ? 'bg-indigo-500 text-white' : 'bg-slate-600 text-slate-300'}`}>
          {device.state ? 'ON' : 'OFF'}
        </div>
      </div>
      
      <p className="text-sm text-slate-400 capitalize">{device.type}</p>
      
      {device.type === 'light' && device.state && (
        <div className="mt-4">
          <label className="text-xs text-slate-400">Brightness: {device.value}%</label>
          <input type="range" disabled value={device.value} className="w-full h-2 bg-slate-600 rounded-lg appearance-none cursor-not-allowed mt-1" />
        </div>
      )}
    </div>
  );
};

export default DeviceCard;