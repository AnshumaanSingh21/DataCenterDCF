'use client';
import { useModel } from '@/lib/ModelContext';
import { Card } from '@/components/shared/Card';
import FinancialTable from '@/components/tables/FinancialTable';

const ROWS = [
  { label: 'CFADS',                key: 'cfads',        format: 'cr', highlight: true },
  { label: 'Interest Expense',     key: 'interest',     format: 'cr' },
  { label: 'Principal Repayment',  key: 'principal',    format: 'cr' },
  { label: 'Debt Service',         key: 'debt_service', format: 'cr' },
  { label: 'DSCR',                 key: 'dscr',         format: 'ratio', highlight: true },
  { label: 'Closing Debt Balance', key: 'closing_debt', format: 'cr' },
];

export default function CashflowPage() {
  const { result } = useModel();
  return (
    <div className="space-y-6 max-w-screen-xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-[#1A1F36]">Cash Flow Statement</h1>
        <p className="text-sm text-[#6B7280] mt-0.5">All values in INR Crore · DSCR colour-coded: green ≥ 1.25x · amber 1.0–1.25x · red &lt; 1.0x</p>
      </div>
      <Card padding="p-0">
        <div className="px-6 py-4 border-b border-[#E2E8F0]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF]">Debt Service Coverage</div>
        </div>
        <FinancialTable rows={ROWS} data={result?.cashflow} years={result?.years} />
      </Card>
    </div>
  );
}
