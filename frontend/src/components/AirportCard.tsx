import { WeatherData } from '../types';
import { Wind, Cloud, Eye, Thermometer } from 'lucide-react';

interface Props {
  data: WeatherData;
  onClick: (data: WeatherData) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  VFR: 'bg-green-500',
  MVFR: 'bg-blue-500',
  IFR: 'bg-red-500',
  LIFR: 'bg-pink-500',
  Unknown: 'bg-gray-500',
};

const CATEGORY_TEXT_COLORS: Record<string, string> = {
  VFR: 'text-green-400',
  MVFR: 'text-blue-400',
  IFR: 'text-red-400',
  LIFR: 'text-pink-400',
  Unknown: 'text-gray-400',
};

export function AirportCard({ data, onClick }: Props) {
  const badgeColor = CATEGORY_COLORS[data.flight_category] || CATEGORY_COLORS['Unknown'];
  const textColor = CATEGORY_TEXT_COLORS[data.flight_category] || CATEGORY_TEXT_COLORS['Unknown'];

  return (
    <div 
      onClick={() => onClick(data)}
      className="bg-slate-800 rounded-xl p-4 shadow-lg hover:bg-slate-750 transition-colors cursor-pointer border border-slate-700 hover:border-slate-600"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-xl font-bold text-white">{data.icao}</h3>
          <p className="text-xs text-slate-400 truncate max-w-[150px]">{data.station_name}</p>
        </div>
        <span className={`${badgeColor} ${textColor} bg-opacity-20 text-xs font-bold px-2 py-1 rounded-full border border-opacity-20 border-white`}>
          {data.flight_category}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm text-slate-300">
        <div className="flex items-center gap-1">
          <Wind size={14} className="text-slate-500" />
          <span>{data.wind?.speed_kts ?? 0} kt</span>
        </div>
        <div className="flex items-center gap-1">
          <Eye size={14} className="text-slate-500" />
          <span>{data.visibility?.miles ?? '-'} sm</span>
        </div>
        <div className="flex items-center gap-1">
          <Cloud size={14} className="text-slate-500" />
          <span>{data.clouds?.[0]?.code ?? 'CLR'}</span>
        </div>
        <div className="flex items-center gap-1">
          <Thermometer size={14} className="text-slate-500" />
          <span>{data.temperature?.celsius ?? '-'}°C</span>
        </div>
      </div>
    </div>
  );
}
