'use client';
import { useModel } from '@/lib/ModelContext';
import { Card } from '@/components/shared/Card';
import FinancialTable from '@/components/tables/FinancialTable';

const ROWS = [
  { label: 'Rack Revenue',          key: 'rack_revenue',          format: 'cr' },
  { label: 'Power Revenue',         key: 'power_revenue',         format: 'cr' },
  { label: 'OTC Revenue',           key: 'otc_revenue',           format: 'cr' },
  { label: 'Cross-Connect Revenue', key: 'cross_connect_revenue', format: 'cr' },
  { label: 'Net Revenue',           key: 'net_revenue',           format: 'cr', highlight: true },
];

// Revenue streams shown in the mix pies (OTC excluded — negligible, ~0.2%)
const STREAMS = [
  { label: 'Colocation',    key: 'rack_revenue',          color: '#00338D' },
  { label: 'Power',         key: 'power_revenue',         color: '#00A36C' },
  { label: 'Cross-Connect', key: 'cross_connect_revenue', color: '#7C3AED' },
];

// Lightweight dependency-free SVG donut
function Donut({ segments, size = 132, stroke = 20 }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const total = segments.reduce((s, x) => s + x.value, 0) || 1;
  let offset = 0;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="shrink-0">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#F1F5F9" strokeWidth={stroke} />
      <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
        {segments.map((seg, i) => {
          const dash = (seg.value / total) * c;
          const el = (
            <circle
              key={i}
              cx={size / 2}
              cy={size / 2}
              r={r}
              fill="none"
              stroke={seg.color}
              strokeWidth={stroke}
              strokeDasharray={`${dash} ${c - dash}`}
              strokeDashoffset={-offset}
            />
          );
          offset += dash;
          return el;
        })}
      </g>
    </svg>
  );
}

function RevenuePie({ revenue, idx, year, caption }) {
  const segs = STREAMS.map((s) => ({ ...s, value: revenue?.[s.key]?.[idx] || 0 }));
  const total = segs.reduce((a, b) => a + b.value, 0) || 1;
  return (
    <Card padding="p-5">
      <div className="text-center mb-4">
        <div className="text-base font-bold text-[#1A1F36]">{year}</div>
        <div className="text-[11px] text-[#9CA3AF]">{caption}</div>
      </div>
      <div className="flex flex-col items-center gap-4">
        <Donut segments={segs} />
        <div className="w-full space-y-1.5">
          {segs.map((s) => (
            <div key={s.key} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-sm shrink-0" style={{ background: s.color }} />
                <span className="text-[#6B7280]">{s.label}</span>
              </div>
              <span className="font-semibold text-[#1A1F36]">
                {((s.value / total) * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export default function RevenuePage() {
  const { result } = useModel();
  const yrs = result?.years || [];
  const n = yrs.length;
  // First operating year, a mid year, and the final year — de-duped and horizon-safe
  const picks = [...new Set([1, Math.min(5, n - 1), n - 1])].filter((i) => i >= 1 && i < n);

  return (
    <div className="space-y-6 max-w-screen-xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-[#1A1F36]">Revenue</h1>
        <p className="text-sm text-[#6B7280] mt-0.5">All values in INR Crore</p>
      </div>

      <Card padding="p-0">
        <div className="px-6 py-4 border-b border-[#E2E8F0]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF]">Revenue Breakdown</div>
        </div>
        <FinancialTable rows={ROWS} data={result?.revenue} years={result?.years} />
      </Card>

      {result?.revenue && picks.length > 0 && (
        <div>
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-3">
            Revenue Mix by Stream
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {picks.map((idx, i) => (
              <RevenuePie
                key={idx}
                revenue={result.revenue}
                idx={idx}
                year={yrs[idx]}
                caption={`Year ${idx}${i === 0 ? ' (Operating)' : ''}`}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
