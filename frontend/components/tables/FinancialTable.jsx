'use client';

function fmt(value, format) {
  if (value === null || value === undefined) return '—';
  const n = Number(value);
  if (isNaN(n)) return '—';
  switch (format) {
    case 'cr':    return n.toFixed(1);
    case 'pct':   return (n * 100).toFixed(0) + '%';
    case 'ratio': return n.toFixed(2) + 'x';
    case 'irr':   return n.toFixed(1) + '%';
    default:      return n.toFixed(1);
  }
}

function dscrColor(value) {
  if (value === null || value === undefined) return '';
  const n = Number(value);
  if (n === 0)    return 'text-[#9CA3AF]';
  if (n < 1.0)   return 'text-[#DC2626] font-semibold';
  if (n < 1.25)  return 'text-[#D4A017] font-semibold';
  return 'text-[#00A36C] font-semibold';
}

export default function FinancialTable({ rows, data, years, unit = 'Cr' }) {
  if (!data || !years) {
    return (
      <div className="text-center py-12 text-[#9CA3AF] text-sm">
        Run the model to see results.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b-2 border-[#E2E8F0]">
            <th className="text-left py-3 px-4 text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] w-52 sticky left-0 bg-white">
              Item
            </th>
            {years.map(y => (
              <th key={y} className="text-right py-3 px-3 text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] min-w-[80px]">
                FY{String(y).slice(2)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => {
            const values = data[row.key] ?? [];
            const isDSCR = row.key === 'dscr';
            return (
              <tr
                key={row.key}
                className={`border-b border-[#E2E8F0] transition-colors hover:bg-[#F4F6F9]/60 ${
                  row.highlight ? 'bg-[#F4F6F9]' : 'bg-white'
                } ${i === 0 ? '' : ''}`}
              >
                <td className={`py-3 px-4 sticky left-0 ${row.highlight ? 'bg-[#F4F6F9]' : 'bg-white'}`}>
                  <span className={`text-xs ${row.highlight ? 'font-semibold text-[#1A1F36]' : 'text-[#6B7280]'}`}>
                    {row.label}
                  </span>
                  {row.format === 'cr' && (
                    <span className="text-[10px] text-[#9CA3AF] ml-1">Cr</span>
                  )}
                </td>
                {years.map((y, j) => {
                  const v = values[j];
                  const display = fmt(v, row.format);
                  const colorClass = isDSCR ? dscrColor(v) : '';
                  return (
                    <td
                      key={y}
                      className={`py-3 px-3 text-right ${row.highlight ? 'font-semibold text-[#1A1F36]' : 'text-[#1A1F36]'} ${colorClass}`}
                      style={{ fontFamily: 'var(--font-jetbrains), monospace', fontSize: '0.8rem' }}
                    >
                      {display}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
