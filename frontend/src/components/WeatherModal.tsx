import { X } from 'lucide-react';
import { WeatherData } from '../types';

interface Props {
  data: WeatherData | null;
  onClose: () => void;
}

export function WeatherModal({ data, onClose }: Props) {
  if (!data) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="bg-slate-900 w-full max-w-lg rounded-2xl border border-slate-700 shadow-2xl overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        <div className="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-800">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-3">
              {data.icao}
              <span className="text-sm font-normal text-slate-400 bg-slate-900 px-2 py-1 rounded">
                LED #{data.led_index}
              </span>
            </h2>
            <p className="text-slate-400">{data.station_name}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-700 rounded-full transition-colors">
            <X />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          
          <div className="flex items-center gap-4">
             <div className="flex-1 bg-slate-800 p-4 rounded-xl text-center">
                <div className="text-slate-400 text-sm mb-1">Flight Category</div>
                <div className="text-2xl font-bold">{data.flight_category}</div>
             </div>
             <div className="flex-1 bg-slate-800 p-4 rounded-xl text-center">
                <div className="text-slate-400 text-sm mb-1">Observed</div>
                <div className="text-lg font-mono">{data.observed?.split('T')[1]?.replace('Z','')}Z</div>
             </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-slate-500 font-bold uppercase text-xs tracking-wider">Metar Details</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-slate-400 block text-sm">Wind</span>
                <span className="text-lg">
                    {data.wind?.degrees ?? '---'}° at {data.wind?.speed_kts ?? 0}kt
                    {data.wind?.gust_kts ? ` (G${data.wind.gust_kts})` : ''}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block text-sm">Visibility</span>
                <span className="text-lg">{data.visibility?.miles} sm</span>
              </div>
               <div>
                <span className="text-slate-400 block text-sm">Temperature</span>
                <span className="text-lg">{data.temperature?.celsius}°C (DP {data.dewpoint?.celsius}°)</span>
              </div>
              <div>
                <span className="text-slate-400 block text-sm">Pressure</span>
                <span className="text-lg">{data.barometer?.hg} inHg</span>
              </div>
            </div>

            <div>
                 <span className="text-slate-400 block text-sm mb-1">Clouds</span>
                 <div className="flex flex-wrap gap-2">
                    {data.clouds?.length ? data.clouds.map((c, i) => (
                        <span key={i} className="bg-slate-700 px-2 py-1 rounded text-sm">
                            {c.code}{c.base_feet_agl ? ` @ ${c.base_feet_agl}ft` : ''}
                        </span>
                    )) : <span className="text-slate-500">None reported</span>}
                 </div>
            </div>
          </div>

          <div className="bg-black/30 p-4 rounded-lg font-mono text-sm text-slate-300 break-words border border-slate-800">
            {data.raw_text}
          </div>
        </div>
      </div>
    </div>
  );
}
