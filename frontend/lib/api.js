const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getDefaults() {
  const res = await fetch(`${API_BASE}/api/defaults`);
  if (!res.ok) throw new Error('Failed to fetch defaults');
  return res.json();
}

export async function runModel(assumptions) {
  const res = await fetch(`${API_BASE}/api/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assumptions),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  return res.json();
}

export function getDownloadUrl() {
  return `${API_BASE}/api/download`;
}
