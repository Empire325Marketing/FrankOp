'use client';
import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/stats`)
      .then((res) => res.json())
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  return (
    <main className="p-4">
      <h1 className="text-xl font-bold mb-4">Trinity AI Dashboard</h1>
      {stats ? (
        <pre className="whitespace-pre-wrap">{JSON.stringify(stats, null, 2)}</pre>
      ) : (
        <p>Loading...</p>
      )}
    </main>
  );
}
