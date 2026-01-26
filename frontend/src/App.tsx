import { useEffect, useState } from 'react';
import { Play, Square, RefreshCw, Plane, WifiOff, AlertTriangle } from 'lucide-react';
import { AirportCard } from './components/AirportCard';
import { WeatherModal } from './components/WeatherModal';
import { WeatherData, SystemStatus } from './types';

function App() {
  const [weather, setWeather] = useState<WeatherData[]>([]);
  const [status, setStatus] = useState<SystemStatus>({ active: false, uptime_seconds: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedAirport, setSelectedAirport] = useState<WeatherData | null>(null);

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
        await fetch(`/api/control/${action}`, { method: 'POST' });
        fetchStatus();
        if (action !== 'stop') fetchWeather();
    } catch(e) {
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
