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

  return (
    <main className="min-h-screen bg-gray-900 text-gray-100 p-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2">Network Status</h1>
          <p className="text-gray-400">Last updated: {new Date(data.timestamp).toLocaleTimeString()}</p>
        </header>

        <section className="mb-10">
          <h2 className="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">Internet Connections</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.isps).map(([name, isp]: [string, any]) => (
              <div key={name} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h3 className="text-xl font-medium uppercase mb-2">{name}</h3>
                <p className={`font-bold ${isp.up ? 'text-green-500' : 'text-red-500'}`}>
                  {isp.up ? 'ONLINE' : 'OFFLINE'}
                </p>
                <div className="mt-4 text-sm text-gray-400 space-y-1">
                  <p>Latency: {isp.latencyMs} ms</p>
                  <p>↓ {isp.rx} | ↑ {isp.tx}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">Mesh Network (Deco)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.mesh.nodes.map((node: any) => (
              <div key={node.name} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h3 className="text-lg font-medium mb-2">{node.name}</h3>
                <p className={`font-bold ${node.online ? 'text-green-500' : 'text-red-500'}`}>
                  {node.online ? 'ONLINE' : 'OFFLINE'}
                </p>
                <div className="mt-4 text-sm text-gray-400 space-y-1">
                  <p>Clients: {node.clients}</p>
                  <p>↓ {node.rx} | ↑ {node.tx}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
