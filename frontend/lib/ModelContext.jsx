'use client';
import { createContext, useContext, useState, useEffect } from 'react';

const ModelContext = createContext(null);

export function ModelProvider({ children }) {
  const [result, setResult]         = useState(null);
  const [assumptions, setAssumptions] = useState(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);

  useEffect(() => {
    try {
      const r = localStorage.getItem('dcf-result');
      const a = localStorage.getItem('dcf-assumptions');
      if (r) setResult(JSON.parse(r));
      if (a) setAssumptions(JSON.parse(a));
    } catch {}
  }, []);

  const updateResult = (data, asmps) => {
    setResult(data);
    setAssumptions(asmps);
    try {
      localStorage.setItem('dcf-result', JSON.stringify(data));
      localStorage.setItem('dcf-assumptions', JSON.stringify(asmps));
    } catch {}
  };

  const clearResult = () => {
    setResult(null);
    setAssumptions(null);
    localStorage.removeItem('dcf-result');
    localStorage.removeItem('dcf-assumptions');
  };

  return (
    <ModelContext.Provider value={{ result, assumptions, loading, setLoading, error, setError, updateResult, clearResult }}>
      {children}
    </ModelContext.Provider>
  );
}

export function useModel() {
  const ctx = useContext(ModelContext);
  if (!ctx) throw new Error('useModel must be used within ModelProvider');
  return ctx;
}
