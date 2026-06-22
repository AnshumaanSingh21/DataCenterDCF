'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useModel } from '@/lib/ModelContext';
import { getDefaults, runModel } from '@/lib/api';
import { Card } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { CheckCircle, AlertCircle } from 'lucide-react';

function Field({ label, name, value, onChange, type = 'number', unit, step = 'any', min, max }) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-semibold text-[#1A1F36]">{label}</label>
      <div className="flex items-center gap-2">
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          step={step}
          min={min}
          max={max}
          className="w-full px-3 py-2 text-sm rounded-lg border border-[#E2E8F0] bg-white text-[#1A1F36] placeholder:text-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#0077C8]/30 focus:border-[#0077C8]/50 transition-all duration-200"
        />
        {unit && <span className="text-xs text-[#9CA3AF] whitespace-nowrap">{unit}</span>}
      </div>
    </div>
  );
}

function SelectField({ label, name, value, onChange, options }) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-semibold text-[#1A1F36]">{label}</label>
      <select
        name={name}
        value={value}
        onChange={onChange}
        className="w-full px-3 py-2 text-sm rounded-lg border border-[#E2E8F0] bg-white text-[#1A1F36] focus:outline-none focus:ring-2 focus:ring-[#0077C8]/30 focus:border-[#0077C8]/50 transition-all duration-200"
      >
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

function SectionHeader({ children }) {
  return (
    <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-4 mt-2">
      {children}
    </div>
  );
}

const LOCATIONS = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai'];
const FACILITY_TYPES = [
  { value: 'retail_colo', label: 'Retail Colo' },
  { value: 'wholesale',   label: 'Wholesale' },
  { value: 'ai_hpc',      label: 'AI / HPC' },
  { value: 'hyperscale',  label: 'Hyperscale' },
];

export default function AssumptionsPage() {
  const { updateResult, setLoading, setError, loading, error } = useModel();
  const router = useRouter();
  const [form, setForm]     = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    getDefaults()
      .then(d => setForm(d))
      .catch(() => setForm({
        total_racks: 1000, location: 'Mumbai', facility_type: 'retail_colo',
        start_year: 2026, projection_years: 10, pue: 1.6,
        debt_pct: 0.50, moratorium_years: 2, interest_rate: 0.10,
        rack_mrc_crore: 0.005, util_tariff: 8.0, power_markup: 1.5, kw_per_rack: 4.5,
      }));
  }, []);

  const onChange = e => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: isNaN(Number(value)) ? value : Number(value) }));
    setSuccess(false);
  };

  const onSubmit = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const data = await runModel(form);
      updateResult(data, form);
      setSuccess(true);
      setTimeout(() => router.push('/dashboard'), 800);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!form) {
    return <div className="flex items-center justify-center py-24 text-sm text-[#9CA3AF]">Loading defaults...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#1A1F36]">Model Assumptions</h1>
        <p className="text-sm text-[#6B7280] mt-0.5">Adjust parameters and run the model to regenerate all outputs and the Excel file.</p>
      </div>

      <Card>
        <SectionHeader>Project Parameters</SectionHeader>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Total Racks" name="total_racks" value={form.total_racks} onChange={onChange} step={100} min={100} />
          <SelectField label="Location" name="location" value={form.location} onChange={onChange}
            options={LOCATIONS.map(l => ({ value: l, label: l }))} />
          <SelectField label="Facility Type" name="facility_type" value={form.facility_type} onChange={onChange}
            options={FACILITY_TYPES} />
          <Field label="Start Year" name="start_year" value={form.start_year} onChange={onChange} step={1} min={2024} />
          <Field label="Projection Years" name="projection_years" value={form.projection_years} onChange={onChange} step={1} min={5} max={20} unit="years" />
        </div>
      </Card>

      <Card>
        <SectionHeader>Technical Parameters</SectionHeader>
        <div className="grid grid-cols-2 gap-4">
          <Field label="PUE" name="pue" value={form.pue} onChange={onChange} step={0.1} min={1.0} max={3.0} unit="ratio" />
          <Field label="IT Load per Rack" name="kw_per_rack" value={form.kw_per_rack} onChange={onChange} step={0.5} min={1} unit="kW/rack" />
        </div>
      </Card>

      <Card>
        <SectionHeader>Revenue Parameters</SectionHeader>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Rack MRC (Year 1)" name="rack_mrc_crore" value={form.rack_mrc_crore} onChange={onChange} step={0.0001} unit="Cr/rack/mo" />
          <Field label="Grid Tariff" name="util_tariff" value={form.util_tariff} onChange={onChange} step={0.5} unit="Rs/kWh" />
          <Field label="Power Markup" name="power_markup" value={form.power_markup} onChange={onChange} step={0.1} unit="Rs/kWh" />
        </div>
      </Card>

      <Card>
        <SectionHeader>Financing Parameters</SectionHeader>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Debt / Total CapEx" name="debt_pct" value={form.debt_pct} onChange={onChange} step={0.05} min={0} max={1} unit="decimal (0.5 = 50%)" />
          <Field label="Interest Rate" name="interest_rate" value={form.interest_rate} onChange={onChange} step={0.005} min={0} max={0.30} unit="decimal (0.10 = 10%)" />
          <Field label="Moratorium" name="moratorium_years" value={form.moratorium_years} onChange={onChange} step={1} min={0} max={5} unit="years" />
        </div>
      </Card>

      {error && (
        <div className="flex items-start gap-3 p-4 bg-[#FEF2F2] rounded-xl border border-red-200">
          <AlertCircle size={16} className="text-red-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-red-600 font-medium">{error}</p>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-3 p-4 bg-[#F0FDF4] rounded-xl border border-green-200">
          <CheckCircle size={16} className="text-[#00A36C]" />
          <p className="text-xs text-[#00A36C] font-medium">Model run complete. Redirecting to dashboard...</p>
        </div>
      )}

      <div className="flex justify-end">
        <Button variant="primary" size="lg" onClick={onSubmit} loading={loading} disabled={loading}>
          {loading ? 'Running Model...' : 'Run Model'}
        </Button>
      </div>
    </div>
  );
}
