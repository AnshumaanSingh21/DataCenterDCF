'use client';

export function Card({ children, className = '', hover = false, onClick, padding = 'p-6' }) {
  const shadow = hover
    ? 'hover:shadow-[0_10px_25px_-5px_rgba(0,51,141,0.12),0_4px_10px_-5px_rgba(0,51,141,0.08)] hover:-translate-y-0.5 cursor-pointer'
    : 'shadow-[0_1px_3px_0_rgba(0,0,0,0.08),0_1px_2px_-1px_rgba(0,0,0,0.06)]';
  return (
    <div
      className={`bg-white rounded-2xl border border-[#E2E8F0] transition-all duration-200 ${shadow} ${padding} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

export function DarkCard({ children, className = '', padding = 'p-6' }) {
  return (
    <div className={`bg-[#1A1F36] rounded-2xl border border-white/10 ${padding} ${className}`}>
      {children}
    </div>
  );
}

export function MetricCard({ label, value, unit, icon: Icon, color = '#0077C8', trend }) {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 shadow-[0_1px_3px_0_rgba(0,0,0,0.08)] hover:shadow-[0_4px_12px_rgba(0,51,141,0.1)] transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: color + '18' }}>
          {Icon && <Icon size={20} style={{ color }} />}
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${trend >= 0 ? 'text-[#00A36C] bg-[#00A36C]/10' : 'text-[#DC2626] bg-[#DC2626]/10'}`}>
            {trend >= 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
      <div className="font-bold text-2xl text-[#1A1F36]" style={{ fontFamily: 'var(--font-jetbrains), monospace' }}>
        {value}
        {unit && <span className="text-sm font-normal text-[#6B7280] ml-1">{unit}</span>}
      </div>
      <div className="text-sm text-[#6B7280] mt-1 font-medium">{label}</div>
    </div>
  );
}

export function KPICard({ title, value, unit, statusColor = '#0077C8' }) {
  return (
    <div
      className="bg-white rounded-xl border border-[#E2E8F0] border-l-[3px] p-4 min-w-[160px] shadow-sm hover:shadow-md transition-all duration-200"
      style={{ borderLeftColor: statusColor }}
    >
      <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-1">{title}</div>
      <div className="text-2xl font-semibold text-[#1A1F36]" style={{ fontFamily: 'var(--font-jetbrains), monospace' }}>
        {value}
      </div>
      {unit && <div className="text-xs text-[#9CA3AF] mt-0.5">{unit}</div>}
    </div>
  );
}
