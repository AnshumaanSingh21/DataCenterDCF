'use client';
import { useModel } from '@/lib/ModelContext';
import { Card } from '@/components/shared/Card';
import FinancialTable from '@/components/tables/FinancialTable';

const ROWS = [
  { label: 'Rack Revenue',   key: 'rack_revenue',  format: 'cr' },
  { label: 'Power Revenue',  key: 'power_revenue', format: 'cr' },
  { label: 'OTC Revenue',    key: 'otc_revenue',   format: 'cr' },
  { label: 'Net Revenue',    key: 'net_revenue',   format: 'cr', highlight: true },
];

export default function RevenuePage() {
  const { result } = useModel();
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
    </div>
  );
}
