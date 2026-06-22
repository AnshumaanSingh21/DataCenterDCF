'use client';
import { useModel } from '@/lib/ModelContext';
import { Card } from '@/components/shared/Card';
import FinancialTable from '@/components/tables/FinancialTable';

const ROWS = [
  { label: 'Civil',        key: 'civil',       format: 'cr' },
  { label: 'Electrical',   key: 'electrical',  format: 'cr' },
  { label: 'Mechanical',   key: 'mechanical',  format: 'cr' },
  { label: 'IT Hardware',  key: 'it',          format: 'cr' },
  { label: 'Network',      key: 'network',     format: 'cr' },
  { label: 'Total CapEx',  key: 'total_capex', format: 'cr', highlight: true },
];

export default function CapExPage() {
  const { result } = useModel();
  return (
    <div className="space-y-6 max-w-screen-xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-[#1A1F36]">Capital Expenditure</h1>
        <p className="text-sm text-[#6B7280] mt-0.5">All values in INR Crore</p>
      </div>
      <Card padding="p-0">
        <div className="px-6 py-4 border-b border-[#E2E8F0]">
          <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF]">CapEx by Category</div>
        </div>
        <FinancialTable rows={ROWS} data={result?.capex} years={result?.years} />
      </Card>
    </div>
  );
}
