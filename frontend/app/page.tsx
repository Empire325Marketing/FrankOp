'use client';

import { useState } from 'react';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');

  async function sendPrompt() {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, model: 'openai' }),
    });
    const data = await res.json();
    setResponse(data.response || data.error);
  }

  return (
    <main className="p-4">
      <h1 className="text-xl font-bold mb-4">Trinity AI Dashboard</h1>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full border p-2"
        rows={4}
      />
      <button onClick={sendPrompt} className="mt-2 px-4 py-2 bg-blue-500 text-white">
        Send
      </button>
      <pre className="mt-4 whitespace-pre-wrap">{response}</pre>
    </main>
  );
}
