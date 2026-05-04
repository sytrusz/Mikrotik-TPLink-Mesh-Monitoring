// frontend/src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/status');
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
    return () => clearInterval(interval);
  }, []);

  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;
  if (!data) return <div className="p-8">Loading...</div>;

  const getStatusBgColor = (status: string) => {
    switch (status) {
      case 'ONLINE': return 'bg-green-600';
      case 'NO INTERNET': return 'bg-yellow-600';
      case 'OFFLINE': return 'bg-red-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <main className="min-h-screen bg-gray-950 text-gray-100 p-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2 tracking-tight">Network Status</h1>
          <p className="text-gray-500 text-sm">Last updated: {new Date(data.timestamp).toLocaleTimeString()}</p>
        </header>

        <section className="mb-12">
          <h2 className="text-xl font-semibold mb-6 text-gray-400 uppercase tracking-widest border-b border-gray-800 pb-2">Internet Connections</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(data.isps).map(([name, isp]: [string, any]) => (
              <div key={name} className="bg-gray-900 p-6 rounded-2xl border border-gray-800 shadow-xl transition-all hover:border-gray-700">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold uppercase tracking-tight">{name}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold text-white shadow-sm ${getStatusBgColor(isp.status)}`}>
                    {isp.status}
                  </span>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">Latency</span>
                    <span className="font-mono">{isp.latencyMs} ms</span>
                  </div>
                  <div className="flex justify-between items-center text-sm border-t border-gray-800 pt-3">
                    <span className="text-gray-500">Download</span>
                    <span className="text-green-400 font-medium">↓ {isp.rx}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">Upload</span>
                    <span className="text-blue-400 font-medium">↑ {isp.tx}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-6 text-gray-400 uppercase tracking-widest border-b border-gray-800 pb-2">Mesh Network</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {data.mesh.nodes.map((node: any) => (
              <div key={node.name} className="bg-gray-900 p-6 rounded-2xl border border-gray-800 shadow-xl transition-all hover:border-gray-700">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-bold">{node.name}</h3>
                  <div className={`w-3 h-3 rounded-full ${node.online ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' : 'bg-red-500'}`} />
                </div>
                <div className="space-y-2 text-sm">
                  <p className="text-gray-500">Clients: <span className="text-gray-200">{node.clients}</span></p>
                  <div className="flex gap-4 text-xs text-gray-500">
                    <span>↓ {node.rx}</span>
                    <span>↑ {node.tx}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
        
        <footer className="mt-16 text-center text-gray-600 text-xs">
          <p>Automatic refresh every 5 seconds</p>
        </footer>
      </div>
    </main>
  );
}
