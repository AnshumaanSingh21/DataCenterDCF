'use client';
import { useModel } from '@/lib/ModelContext';
import { MetricCard, Card } from '@/components/shared/Card';
import { Button } from '@/components/shared/Button';
import { useRouter } from 'next/navigation';
import {
  TrendingUp, PieChart, Target, Layers,
  Building2, DollarSign, Activity, Landmark,
} from 'lucide-react';

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

function DSCRStrip({ years, dscr }) {
  const colorFor = (v) => {
    if (!v || v === 0) return { bg: '#F4F6F9', text: '#9CA3AF' };
    if (v < 1.0)      return { bg: '#FEF2F2', text: '#DC2626' };
    if (v < 1.25)     return { bg: '#FFFBEB', text: '#D4A017' };
    return             { bg: '#F0FDF4', text: '#00A36C' };
  };
  return (
    <Card padding="p-5">
      <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-3">DSCR — Year by Year</div>
      <div className="flex gap-2 flex-wrap">
        {years.map((y, i) => {
          const v = dscr?.[i];
          const { bg, text } = colorFor(v);
          return (
            <div key={y} className="flex flex-col items-center gap-1 min-w-[52px]">
              <div
                className="rounded-lg px-2 py-1.5 text-xs font-bold w-full text-center"
                style={{ backgroundColor: bg, color: text, fontFamily: 'var(--font-jetbrains), monospace' }}
              >
                {v !== null && v !== undefined ? v.toFixed(2) + 'x' : '—'}
              </div>
              <span className="text-[10px] text-[#9CA3AF]">FY{String(y).slice(2)}</span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export default function DashboardPage() {
  const { result } = useModel();

  if (!result) return <EmptyState />;

  const { kpis, years, cashflow } = result;

  const metrics = [
    { label: 'Project IRR',      value: kpis.project_irr?.toFixed(1),    unit: '%',  icon: TrendingUp,  color: '#00338D' },
    { label: 'Equity IRR',       value: kpis.equity_irr?.toFixed(1),     unit: '%',  icon: Target,      color: '#0077C8' },
    { label: 'NPV',              value: kpis.npv?.toFixed(1),            unit: 'Cr', icon: DollarSign,  color: '#00A36C' },
    { label: 'MOIC',             value: kpis.moic?.toFixed(2),           unit: 'x',  icon: Layers,      color: '#D4A017' },
    { label: 'WACC',             value: kpis.wacc?.toFixed(2),           unit: '%',  icon: Activity,    color: '#6B7280' },
    { label: 'Total CapEx',      value: kpis.total_capex?.toFixed(1),    unit: 'Cr', icon: Building2,   color: '#00338D' },
    { label: 'Equity Invested',  value: kpis.equity_invested?.toFixed(1),unit: 'Cr', icon: PieChart,    color: '#0077C8' },
    { label: 'Terminal EV',      value: kpis.terminal_value?.toFixed(1), unit: 'Cr', icon: Landmark,    color: '#00A36C' },
  ];

  return (
    <div className="space-y-6 max-w-screen-xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-[#1A1F36]">Project Dashboard</h1>
        <p className="text-sm text-[#6B7280] mt-0.5">1,000 Racks · Mumbai · Retail Colo · 10-Year Model</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map(m => (
          <MetricCard key={m.label} {...m} />
        ))}
      </div>

      <DSCRStrip years={years} dscr={cashflow?.dscr} />
    </div>
  );
}
