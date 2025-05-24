'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Login() {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleLogin() {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    });
    if (res.ok) {
      localStorage.setItem('pinarch_token', token);
      router.push('/dashboard');
    } else {
      setError('Invalid token');
    }
  }

  return (
    <main className="p-4 flex flex-col items-center">
      <h1 className="text-2xl font-bold mb-4">WELCOME PINARCH I'm JAMES</h1>
      <input
        type="password"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        className="border p-2 w-64"
        placeholder="Enter token"
      />
      <button
        onClick={handleLogin}
        className="mt-2 px-4 py-2 bg-green-600 text-white"
      >
        Login
      </button>
      {error && <p className="mt-2 text-red-600">{error}</p>}
    </main>
  );
}
