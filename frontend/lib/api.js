function getApiBase() {
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  }
  return 'https://datacenterdcf.onrender.com';
}
const API_BASE = getApiBase();

export async function getDefaults() {
  const res = await fetch(`${API_BASE}/api/defaults`);
  if (!res.ok) throw new Error('Failed to fetch defaults');
  return res.json();
}

export async function getMarketValues(location, facilityType, kwPerRack = 6.0) {
  const params = new URLSearchParams({ location, facility_type: facilityType, kw_per_rack: kwPerRack });
  const res = await fetch(`${API_BASE}/api/market-values?${params}`);
  if (!res.ok) throw new Error('Failed to fetch market values');
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

export async function downloadExcel(assumptions) {
  // Stateless download: POST the assumptions used for the run and stream back
  // the workbook built from exactly those inputs (no shared server state).
  const res = await fetch(`${API_BASE}/api/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assumptions),
  });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'DataCenter_DCF_Model.xlsx';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
