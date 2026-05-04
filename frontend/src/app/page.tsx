// frontend/src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [time, setTime] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      // Use env variable or fallback to dynamic hostname
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL || `http://${window.location.hostname}:8000/api/status`;
      const res = await fetch(apiUrl);
      if (!res.ok) throw new Error('Failed to fetch');
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    
    const clockInterval = setInterval(() => setTime(new Date()), 1000);
    
    return () => {
      clearInterval(interval);
      clearInterval(clockInterval);
    };
  }, []);

  if (error) return <div className="min-h-screen bg-black p-8 text-red-500 flex items-center justify-center">Error: {error}</div>;
  if (!data) {
    return (
      <div className="min-h-screen bg-black p-8 text-gray-400 flex flex-col items-center justify-center font-sans">
        <svg className="w-8 h-8 animate-spin text-green-500 mb-4" xmlns="http://www.w3.org/0000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <div className="animate-pulse tracking-widest text-sm uppercase text-gray-500 font-semibold">Loading network status...</div>
      </div>
    );
  }

  const isps = Object.entries(data.isps);
  const nodes = data.mesh.nodes;
  const ispsUp = isps.filter(([_, isp]: any) => isp.status === 'ONLINE').length;
  
  const allSystemsUp = ispsUp === isps.length && nodes.every((n: any) => n.online);

  const timeStr = time.toLocaleTimeString('en-GB', { hour12: false });

  const MAX_PLAN_MBPS = process.env.NEXT_PUBLIC_MAX_PLAN_MBPS ? parseFloat(process.env.NEXT_PUBLIC_MAX_PLAN_MBPS) : 500; // Add your actual ISP plan limit to env file

  const parseSpeed = (speedStr: string) => {
    const parts = speedStr.split(' ');
    if (parts.length === 2) return { val: parts[0], unit: parts[1] };
    return { val: '0', unit: 'kbps' };
  };

  const getMetricWidth = (valStr: string, unit: string, isLatency: boolean = false) => {
    const val = parseFloat(valStr);
    if (isNaN(val)) return '0%';
    if (isLatency) {
      return `${Math.min(100, Math.max(5, (val / 200) * 100))}%`; // Assume 200ms is "max" bar length
    }
    if (unit.toLowerCase().includes('mbps')) {
      return `${Math.min(100, Math.max(2, (val / MAX_PLAN_MBPS) * 100))}%`;
    }
    return `${Math.min(100, Math.max(2, (val / 1000 / MAX_PLAN_MBPS) * 100))}%`;
  };

  const formatNodeInfo = (rawName: string, isFirst: boolean) => {
    const parts = rawName.split(' - ');
    const title = parts[0];
    let subtitle = '';
    if (parts.length > 1) {
      subtitle = parts[1];
      if (subtitle.includes('2F')) subtitle = '2ND FLOOR' + (isFirst ? ' • PRIMARY' : '');
      else if (subtitle.includes('1F')) subtitle = '1ST FLOOR';
    } else {
      subtitle = isFirst ? 'PRIMARY NODE' : 'EXTENSION NODE';
    }
    return { title, subtitle: subtitle.toUpperCase() };
  };

  return (
    <main className="min-h-screen bg-black text-gray-200 p-4 md:p-10 font-sans selection:bg-gray-800 selection:text-white">
      <div className="max-w-5xl mx-auto">
        
        {/* HEADER */}
        <header className="flex justify-between items-end mb-12">
          <div>
            <div className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest mb-1">
              {process.env.NEXT_PUBLIC_NETWORK_NAME || 'Home Network'}
            </div>
            <h1 className="text-3xl font-semibold text-white tracking-tight">Network Status</h1>
          </div>
          <div className="text-right">
            <div className="text-xl text-gray-300 font-medium mb-1 tracking-wide">
              {timeStr}
            </div>
            <div className="flex items-center justify-end text-sm text-gray-400">
              <span className={`w-1.5 h-1.5 rounded-full mr-2 ${allSystemsUp ? 'bg-green-500' : 'bg-red-500'}`}></span>
              {allSystemsUp ? 'All systems up' : 'System issues detected'}
            </div>
          </div>
        </header>

        {/* INTERNET CONNECTIONS */}
        <section className="mb-10">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-4 gap-4 md:gap-0">
            <h2 className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Internet Connections</h2>
            
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6 bg-[#161616] px-4 py-2 rounded-lg border border-[#222]">
              <div className="text-[10px] text-gray-500 uppercase tracking-widest">Live Usage</div>
              <div className="flex items-baseline gap-1">
                <span className="text-green-500 text-[10px] mr-1">↓</span>
                <span className="text-lg font-medium text-white">
                  {isps.reduce((acc: number, [_, isp]: [string, any]) => acc + parseFloat(parseSpeed(isp.rx).val || '0'), 0).toFixed(1)}
                </span>
                <span className="text-[11px] text-gray-500 font-mono">/ {MAX_PLAN_MBPS} Mbps</span>
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-blue-500 text-[10px] mr-1">↑</span>
                <span className="text-lg font-medium text-white">
                  {isps.reduce((acc: number, [_, isp]: [string, any]) => acc + parseFloat(parseSpeed(isp.tx).val || '0'), 0).toFixed(1)}
                </span>
                <span className="text-[11px] text-gray-500 font-mono">/ {MAX_PLAN_MBPS} Mbps</span>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            {isps.map(([name, isp]: [string, any]) => {
              const rx = parseSpeed(isp.rx);
              const tx = parseSpeed(isp.tx);
              const isOnline = isp.status === 'ONLINE';
              // Force uppercase for all ISP names (e.g. CONVERGE, PLDT, GLOBE)
              const displayName = name.toUpperCase();
              
              return (
                <div key={name} className="bg-[#161616] p-6 rounded-[20px] shadow-lg border border-[#222]">
                  <div className="flex justify-between items-center mb-10">
                    <h3 className="text-[22px] font-medium text-white">{displayName}</h3>
                    
                    <div className="bg-white px-3 py-1 rounded-full flex items-center shadow-sm">
                      <span className={`w-1.5 h-1.5 rounded-full mr-2 ${isOnline ? 'bg-[#10B981]' : 'bg-red-500'}`}></span>
                      <span className={`text-[11px] font-bold uppercase tracking-wide ${isOnline ? 'text-emerald-700' : 'text-red-700'}`}>
                        {isOnline ? 'Online' : 'Offline'}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    {/* Latency */}
                    <div>
                      <div className="text-[11px] text-gray-500 tracking-widest mb-1 uppercase">Latency</div>
                      <div className="flex items-baseline mb-3">
                        <span className="text-xl font-medium text-white mr-1.5">{isp.latencyMs}</span>
                        <span className="text-sm text-gray-500">ms</span>
                      </div>
                      <div className="h-[3px] w-full bg-[#2a2a2a] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-yellow-500 rounded-full transition-all duration-500" 
                          style={{ width: getMetricWidth(isp.latencyMs, 'ms', true) }}
                        ></div>
                      </div>
                    </div>
                    {/* Download */}
                    <div>
                      <div className="text-[11px] text-gray-500 tracking-widest mb-1 uppercase flex items-center gap-1">
                        <span className="text-[10px]">↓</span> Down
                      </div>
                      <div className="flex items-baseline mb-3">
                        <span className="text-xl font-medium text-white mr-1.5">{rx.val}</span>
                        <span className="text-sm text-gray-500">{rx.unit}</span>
                      </div>
                      <div className="h-[3px] w-full bg-[#2a2a2a] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-green-500 rounded-full transition-all duration-500" 
                          style={{ width: getMetricWidth(rx.val, rx.unit) }}
                        ></div>
                      </div>
                    </div>
                    {/* Upload */}
                    <div>
                      <div className="text-[11px] text-gray-500 tracking-widest mb-1 uppercase flex items-center gap-1">
                        <span className="text-[10px]">↑</span> Up
                      </div>
                      <div className="flex items-baseline mb-3">
                        <span className="text-xl font-medium text-white mr-1.5">{tx.val}</span>
                        <span className="text-sm text-gray-500">{tx.unit}</span>
                      </div>
                      <div className="h-[3px] w-full bg-[#2a2a2a] rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-blue-500 rounded-full transition-all duration-500" 
                          style={{ width: getMetricWidth(tx.val, tx.unit) }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* MESH NETWORK */}
        <section className="mb-8">
          <div className="flex justify-between items-end mb-4">
            <h2 className="text-[11px] font-semibold text-gray-500 uppercase tracking-widest">Mesh Network</h2>
          </div>

          <div className="bg-[#161616] rounded-[20px] shadow-lg border border-[#222] flex flex-col md:flex-row overflow-hidden">
            {nodes.map((node: any, idx: number) => {
              const rx = parseSpeed(node.rx);
              const tx = parseSpeed(node.tx);
              const { title, subtitle } = formatNodeInfo(node.name, idx === 0);

              return (
                <div 
                  key={node.name} 
                  className="flex-1 p-6 border-b md:border-b-0 md:border-r border-[#262626] last:border-0 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <h3 className="text-[17px] font-medium text-white">{title}</h3>
                      <div className={`w-1.5 h-1.5 rounded-full ${node.online ? 'bg-[#10B981]' : 'bg-red-500'}`}></div>
                    </div>
                    
                    <div className="text-[11px] font-medium text-gray-500 tracking-widest mb-1">
                      {subtitle}
                    </div>
                    
                    <div className="text-[14px] text-gray-400 mb-8 mt-2">
                      <span className="text-white font-medium mr-1">{node.clients === '---' ? 0 : node.clients}</span> clients
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex items-center text-sm">
                      <span className="text-gray-500 text-[10px] mr-1.5">↓</span>
                      <span className="text-gray-300 font-medium mr-1">{rx.val}</span>
                      <span className="text-gray-500">{rx.unit}</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <span className="text-gray-500 text-[10px] mr-1.5">↑</span>
                      <span className="text-gray-300 font-medium mr-1">{tx.val}</span>
                      <span className="text-gray-500">{tx.unit}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* FOOTER */}
        <footer className="flex justify-between items-center text-[13px] text-gray-500 pt-2 px-2 pb-6">
          <div>
            <span className="text-gray-400">
              Developed by Nathan Rener M.
            </span>
          </div>
          <div className="flex items-center tracking-wide">
            <div className="relative w-3 h-3 mr-2">
              <svg className="w-full h-full animate-spin text-[#1ABC9C]" xmlns="http://www.w3.org/0000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            Refreshes every 5s
          </div>
        </footer>

      </div>
    </main>
  );
}
