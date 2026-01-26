export interface WeatherData {
  icao: string;
  flight_category: string;
  led_index?: number;
  led_color?: [number, number, number];
  observed?: string;
  wind?: {
    degrees?: number;
    speed_kts?: number;
    gust_kts?: number;
  };
  visibility?: {
    miles?: string;
    meters?: string;
  };
  clouds?: Array<{
    code: string;
    base_feet_agl?: number;
  }>;
  temperature?: {
    celsius?: number;
    fahrenheit?: number;
  };
  dewpoint?: {
    celsius?: number;
    fahrenheit?: number;
  };
  barometer?: {
    hg?: number;
    hpa?: number;
  };
  raw_text?: string;
  station_name?: string;
}

export interface SystemStatus {
  active: boolean;
  last_update?: string;
  uptime_seconds: number;
}
