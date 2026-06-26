'use client';
import { useState } from 'react';
import { useModel } from '@/lib/ModelContext';
import { MetricCard, Card } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { useRouter } from 'next/navigation';
import {
  TrendingUp, PieChart, Target, Layers,
  Building2, DollarSign, Activity, Landmark,
} from 'lucide-react';

const EXCHANGE_RATE = 93; // rough INR per USD — 1 Cr ≈ $0.108M

function EmptyState() {
  const router = useRouter();
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <div className="w-16 h-16 rounded-2xl bg-[#00338D]/10 flex items-center justify-center">
        <Activity size={28} style={{ color: '#00338D' }} />
      </div>
      <div className="text-center">
        <h2 className="text-lg font-semibold text-[#1A1F36] mb-1">No model run yet</h2>
        <p className="text-sm text-[#6B7280]">Set your assumptions and run the model to see results.</p>
      </div>
      <Button variant="primary" onClick={() => router.push('/assumptions')}>
        Go to Assumptions
      </Button>
    </div>
  );
}


const FACILITY_LABELS = {
  retail_colo: 'Retail Colo',
  wholesale:   'Wholesale',
  ai_hpc:      'AI / HPC',
  hyperscale:  'Hyperscale',
};

export default function DashboardPage() {
  const { result, assumptions } = useModel();
  const [showUsd, setShowUsd] = useState(false);

  if (!result) return <EmptyState />;

  const { kpis } = result;

  const subtitle = assumptions
    ? `${Number(assumptions.total_racks).toLocaleString()} Racks · ${assumptions.location} · ` +
      `${FACILITY_LABELS[assumptions.facility_type] || assumptions.facility_type} · ` +
      `${assumptions.projection_years}-Year Model`
    : 'Project summary';

  const fmtCr = (val, dec = 1) => {
    if (val === null || val === undefined) return '—';
    const v = showUsd ? (val * 10 / EXCHANGE_RATE) : val;
    return v.toFixed(dec);
  };

  const crUnit = showUsd ? '$M' : 'Cr';

  const metrics = [
    { label: 'Project IRR',      value: kpis.project_irr?.toFixed(1),    unit: '%',    icon: TrendingUp,  color: '#00338D' },
    { label: 'Equity IRR',       value: kpis.equity_irr?.toFixed(1),     unit: '%',    icon: Target,      color: '#0077C8' },
    { label: 'NPV',              value: fmtCr(kpis.npv),                 unit: crUnit, icon: DollarSign,  color: '#00A36C' },
    { label: 'MOIC',             value: kpis.moic?.toFixed(2),           unit: 'x',    icon: Layers,      color: '#D4A017' },
    { label: 'WACC',             value: kpis.wacc?.toFixed(2),           unit: '%',    icon: Activity,    color: '#6B7280' },
    { label: 'Total CapEx',      value: fmtCr(kpis.total_capex),         unit: crUnit, icon: Building2,   color: '#00338D' },
    { label: 'Equity Invested',  value: fmtCr(kpis.equity_invested),     unit: crUnit, icon: PieChart,    color: '#0077C8' },
    { label: 'Terminal EV',      value: fmtCr(kpis.terminal_value),      unit: crUnit, icon: Landmark,    color: '#00A36C' },
  ];

  return (
    <div className="space-y-6 max-w-screen-xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-[#1A1F36]">Project Dashboard</h1>
          <p className="text-sm text-[#6B7280] mt-0.5">{subtitle}</p>
        </div>
        <button
          onClick={() => setShowUsd(u => !u)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-sm font-medium transition-colors"
          style={showUsd
            ? { background: '#00338D', color: 'white', borderColor: '#00338D' }
            : { background: 'white', color: '#6B7280', borderColor: '#E5E7EB' }}
        >
          {showUsd ? '$ USD' : '₹ INR'}
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map(m => (
          <MetricCard key={m.label} {...m} />
        ))}
      </div>

      {showUsd && (
        <p className="text-xs text-[#9CA3AF]">
          USD values are indicative only. Exchange rate: ₹{EXCHANGE_RATE}/USD. 1 Cr = ${(10 / EXCHANGE_RATE).toFixed(3)}M.
        </p>
      )}
    </div>
  );
}
