import { useEffect, useState } from 'react';
import { Play, Square, RefreshCw, Plane, WifiOff, AlertTriangle, Sun } from 'lucide-react';
import { AirportCard } from './components/AirportCard';
import { WeatherModal } from './components/WeatherModal';
import { WeatherData, SystemStatus } from './types';

function App() {
  const [weather, setWeather] = useState<WeatherData[]>([]);
  const [status, setStatus] = useState<SystemStatus>({ active: false, uptime_seconds: 0, brightness: 255 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedAirport, setSelectedAirport] = useState<WeatherData | null>(null);

  const formatLastUpdate = (iso?: string) => {
    if (!iso) return null;
    const d = new Date(iso);
    if (isNaN(d.getTime())) return null;
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Status fetch failed", e);
    }
  };

  const fetchWeather = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/weather');
      if (!res.ok) throw new Error('Failed to fetch weather');
      const data = await res.json();
      setWeather(data);
    } catch (e) {
      setError('Failed to load weather data. Check API connection.');
    } finally {
      setLoading(false);
    }
  };

  const control = async (action: 'start' | 'stop' | 'refresh') => {
    try {
      const res = await fetch(`/api/control/${action}`, { method: 'POST' });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setError('');
      fetchStatus();
      if (action !== 'stop') fetchWeather();
    } catch (e) {
      console.error(e);
      setError(`Command "${action}" failed. The board may be offline.`);
    }
  };

  const updateBrightness = async (val: number) => {
    // Optimistic update
    setStatus(prev => ({ ...prev, brightness: val }));
    try {
      await fetch('/api/control/brightness', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brightness: val })
      });
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchWeather();
    const interval = setInterval(() => {
      fetchStatus();
      // Don't auto-fetch weather too often, the backend handles the loop.
      // But we can poll for updates occasionally.
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen pb-12">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Plane className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Aviation Weather</h1>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span className={`w-2 h-2 rounded-full ${status.active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                {status.active ? 'System Active' : 'System Stopped'}
                {status.last_update && formatLastUpdate(status.last_update) && (
                  <span>&middot; Updated {formatLastUpdate(status.last_update)}</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            {!status.active ? (
              <button onClick={() => control('start')} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors">
                <Play size={18} /> Start
              </button>
            ) : (
              <button onClick={() => control('stop')} className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors">
                <Square size={18} /> Stop
              </button>
            )}
            <button onClick={() => control('refresh')} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors disabled:opacity-50">
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} /> Refresh
            </button>
          </div>

          <div className="flex items-center gap-3 border-l border-slate-700 pl-4 ml-2">
            <Sun size={18} className="text-slate-400" />
            <input
              type="range"
              min="10"
              max="255"
              value={status.brightness}
              onChange={(e) => updateBrightness(parseInt(e.target.value))}
              className="w-24 accent-blue-500 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-xs text-slate-300 w-8 text-right" data-testid="brightness-value">
              {status.brightness}
            </span>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">

        {error && (
          <div className="bg-red-900/50 border border-red-700 text-red-200 p-4 rounded-xl mb-6 flex items-center gap-3">
            <AlertTriangle /> {error}
          </div>
        )}

        {weather.length === 0 && !loading && !error && (
          <div className="text-center py-20 text-slate-500">
            <WifiOff size={48} className="mx-auto mb-4 opacity-50" />
            <p>No weather data available. Start the board or refresh.</p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {weather.map(data => (
            <AirportCard
              key={data.icao}
              data={data}
              onClick={setSelectedAirport}
            />
          ))}
        </div>
      </main>

      <WeatherModal
        data={selectedAirport}
        onClose={() => setSelectedAirport(null)}
      />
    </div>
  )
}

export default App
