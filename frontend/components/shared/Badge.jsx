'use client';

const colors = {
  blue:  'bg-[#0077C8]/10 text-[#0077C8] border-[#0077C8]/20',
  navy:  'bg-[#00338D]/10 text-[#00338D] border-[#00338D]/20',
  green: 'bg-[#00A36C]/10 text-[#00A36C] border-[#00A36C]/20',
  amber: 'bg-[#D4A017]/10 text-[#D4A017] border-[#D4A017]/20',
  red:   'bg-red-50 text-red-600 border-red-200',
  grey:  'bg-[#F4F6F9] text-[#6B7280] border-[#E2E8F0]',
};

const sizes = {
  xs: 'px-1.5 py-0.5 text-xs',
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
};

export function Badge({ children, color = 'blue', size = 'sm' }) {
  return (
    <span className={`inline-flex items-center font-semibold rounded-md border ${colors[color] ?? colors.blue} ${sizes[size] ?? sizes.sm}`}>
      {children}
    </span>
  );
}

const dotColors = { green: '#00A36C', amber: '#D4A017', blue: '#0077C8', red: '#DC2626', grey: '#9CA3AF' };

export function StatusBadge({ label, status = 'blue' }) {
  return (
    <Badge color={status}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 inline-block" style={{ backgroundColor: dotColors[status] ?? dotColors.blue }} />
      {label}
    </Badge>
  );
}
