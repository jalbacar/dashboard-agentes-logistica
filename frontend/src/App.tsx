// frontend/src/App.tsx
// Versión interactiva que se comunica con el backend de Crew AI.

import React, { useState } from 'react';

// --- Estilos (movidos aquí para simplicidad) ---
const AppStyles = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    :root {
      --bg-color: #f4f7fa;
      --card-bg: #ffffff;
      --text-color: #333;
      --primary-color: #007bff;
      --border-color: #e0e0e0;
      --shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    body { margin: 0; font-family: 'Roboto', sans-serif; background-color: var(--bg-color); color: var(--text-color); }
    .App { display: flex; flex-direction: column; min-height: 100vh; }
    .app-header { background-color: var(--card-bg); padding: 1rem 2rem; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; box-shadow: var(--shadow); }
    .app-header h1 { margin: 0; font-size: 1.5rem; font-weight: 500; }
    main { padding: 2rem; }
    .control-panel { background-color: var(--card-bg); padding: 1.5rem; border-radius: 8px; box-shadow: var(--shadow); }
    button { background-color: var(--primary-color); color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 5px; cursor: pointer; font-size: 1rem; transition: background-color 0.2s; }
    button:hover { background-color: #0056b3; }
    button:disabled { background-color: #a0a0a0; cursor: not-allowed; }
    .results { margin-top: 2rem; background-color: var(--card-bg); padding: 1.5rem; border-radius: 8px; box-shadow: var(--shadow); }
    pre { background-color: #2d2d2d; color: #f8f8f2; padding: 1rem; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
  `}</style>
);

// --- Componente Principal de la App ---
function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimizeRoutes = async () => {
    setIsLoading(true);
    setResults(null);
    setError(null);

    const requestData = {
      deliveries: [
        { id: "d1", orderId: "o1", weight: 10 },
        { id: "d2", orderId: "o2", weight: 25 },
        { id: "d3", orderId: "o3", weight: 15 },
        { id: "d4", orderId: "o4", weight: 5 }
      ],
      fleet: [
        { id: "v1", capacity: 35 },
        { id: "v2", capacity: 20 }
      ]
    };

    try {
      // La URL ahora es relativa gracias al proxy en package.json
      const response = await fetch('/api/optimize-routes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`Error en la petición: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <AppStyles />
      <header className="app-header">
        <h1>Dashboard de Agentes de Logística</h1>
      </header>
      <main>
        <div className="control-panel">
          <h2>Panel de Control</h2>
          <p>Pulsa el botón para enviar una petición de optimización a los agentes de IA.</p>
          <button onClick={handleOptimizeRoutes} disabled={isLoading}>
            {isLoading ? 'Optimizando...' : 'Optimizar Rutas'}
          </button>
        </div>

        {results && (
          <div className="results">
            <h2>Resultados de la Optimización</h2>
            <pre>{JSON.stringify(results, null, 2)}</pre>
          </div>
        )}

        {error && (
          <div className="results">
            <h2>Error</h2>
            <pre>{error}</pre>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
