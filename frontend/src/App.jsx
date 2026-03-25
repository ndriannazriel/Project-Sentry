import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Project Sentinel - Security Intelligence Dashboard
          </h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-12 px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Input Layer</h2>
            <p className="text-gray-600">Raw visibility & event ingestion</p>
            <p className="text-sm mt-2">
              <a href="http://localhost:8001/health" className="text-blue-600 hover:underline">
                Status →
              </a>
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Enrichment Layer</h2>
            <p className="text-gray-600">CTI & threat analysis</p>
            <p className="text-sm mt-2">
              <a href="http://localhost:8002/health" className="text-blue-600 hover:underline">
                Status →
              </a>
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Intelligence Layer</h2>
            <p className="text-gray-600">Risk scoring & AI advisory</p>
            <p className="text-sm mt-2">
              <a href="http://localhost:8003/health" className="text-blue-600 hover:underline">
                Status →
              </a>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
