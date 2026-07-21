import React from 'react';

interface ProgressRingProps {
  score: number;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({ score }) => {
  const radius = 60;
  const stroke = 10;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getColor = (pct: number) => {
    if (pct >= 85) return 'stroke-emerald-500';
    if (pct >= 50) return 'stroke-amber-500';
    return 'stroke-rose-500';
  };

  return (
    <div className="relative flex items-center justify-center">
      <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
        <circle
          className="stroke-slate-700"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          className={`transition-all duration-1000 ease-out ${getColor(score)}`}
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset }}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
      </svg>
      <span className="absolute text-2xl font-bold text-white">{score}%</span>
    </div>
  );
};