'use client';
import { useModel } from '@/lib/ModelContext';
import { Card } from '@/components/shared/Card';
import FinancialTable from '@/components/tables/FinancialTable';

const ROWS = [
  { label: 'Net Revenue',    key: 'net_revenue',   format: 'cr' },
  { label: 'Total OpEx',     key: 'total_opex',    format: 'cr' },
  { label: 'EBITDA',         key: 'ebitda',        format: 'cr', highlight: true },
  { label: 'EBITDA Margin',  key: 'ebitda_margin', format: 'pct' },
  { label: 'Depreciation',   key: 'depreciation',  format: 'cr' },
  { label: 'Interest Expense', key: 'interest',    format: 'cr' },
  { label: 'Tax',            key: 'tax',           format: 'cr' },
  { label: 'PAT',            key: 'pat',           format: 'cr', highlight: true },
];

export default function PnLPage() {
  const { result } = useModel();
  return (
    <div className="space-y-6 max-w-screen-xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-[#1A1F36]">P&L Statement</h1>
        <p className="text-sm text-[#6B7280] mt-0.5">All values in INR Crore</p>
      </div>
      <Card padding="p-0">
        <div className="px-6 py-4 border-b border-[#E2E8F0]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF]">Profit & Loss</div>
        </div>
        <FinancialTable rows={ROWS} data={result?.pnl} years={result?.years} />
      </Card>
    </div>
  );
}
