const PROD_URL = 'https://datacenterdcf.onrender.com';
const API_BASE = (process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL.length > 0)
  ? process.env.NEXT_PUBLIC_API_URL
  : PROD_URL;

export async function getDefaults() {
  const res = await fetch(`${API_BASE}/api/defaults`);
  if (!res.ok) throw new Error('Failed to fetch defaults');
  return res.json();
}

export async function runModel(assumptions) {
  let res;
  try {
    res = await fetch(`${API_BASE}/api/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(assumptions),
    });
  } catch (e) {
    throw new Error(`Network error calling ${API_BASE}/api/run — ${e.message}`);
  }
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err);
  }
  return res.json();
}

export function getDownloadUrl() {
  return `${API_BASE}/api/download`;
}
