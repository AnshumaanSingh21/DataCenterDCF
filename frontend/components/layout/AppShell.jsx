'use client';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, SlidersHorizontal, TrendingUp,
  Building2, BarChart2, Waves, ChevronLeft, ChevronRight, Download,
} from 'lucide-react';
import { useModel } from '@/lib/ModelContext';
import { getDownloadUrl } from '@/lib/api';

const NAV_ITEMS = [
  { id: 'dashboard',    label: 'Dashboard',       icon: LayoutDashboard,   href: '/dashboard' },
  { id: 'assumptions',  label: 'Assumptions',     icon: SlidersHorizontal, href: '/assumptions' },
  { id: 'revenue',      label: 'Revenue',         icon: TrendingUp,        href: '/revenue' },
  { id: 'capex',        label: 'Capital Expenditure', icon: Building2,     href: '/capex' },
  { id: 'pnl',          label: 'P&L Statement',   icon: BarChart2,         href: '/pnl' },
  { id: 'cashflow',     label: 'Cash Flow',        icon: Waves,            href: '/cashflow' },
];

function Sidebar({ collapsed, onToggle }) {
  const pathname = usePathname();
  return (
    <div className={`${collapsed ? 'w-16' : 'w-64'} flex-shrink-0 bg-[#0D1428] border-r border-white/[0.06] flex flex-col transition-all duration-300 overflow-hidden h-full`}>
      {/* Logo area */}
      <div className={`flex items-center ${collapsed ? 'justify-center px-2' : 'justify-between px-4'} py-4 border-b border-white/[0.06]`}>
        {!collapsed && (
          <div>
            <div className="text-sm font-bold text-white" style={{ fontFamily: 'var(--font-plus-jakarta), sans-serif' }}>
              K-Nexus.AI
            </div>
            <div className="text-[10px] text-white/40 font-medium">Datacenter DCF</div>
          </div>
        )}
        <button
          onClick={onToggle}
          className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-colors flex-shrink-0"
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {!collapsed && (
          <p className="text-[9px] font-bold uppercase tracking-widest text-white/25 px-2 mb-2">PLATFORM</p>
        )}
        {NAV_ITEMS.map(item => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`flex items-center gap-3 px-2.5 py-2 rounded-lg transition-colors group ${
                isActive
                  ? 'bg-[#00338D]/25 border border-[#00338D]/30 text-white'
                  : 'text-white/50 hover:text-white hover:bg-white/5 border border-transparent'
              }`}
            >
              <Icon size={16} className={`flex-shrink-0 ${isActive ? 'text-[#0077C8]' : 'group-hover:text-white/80'}`} />
              {!collapsed && <span className="text-xs font-semibold truncate">{item.label}</span>}
            </Link>
          );
        })}
      </div>

      {/* Status */}
      <div className="border-t border-white/[0.06] px-2 py-3">
        <div className="flex items-center gap-2 px-2">
          <div className="relative flex-shrink-0">
            <span className="w-2 h-2 rounded-full bg-[#00A36C] block" />
            <span className="absolute inset-0 rounded-full bg-[#00A36C] animate-ping opacity-50" />
          </div>
          {!collapsed && <span className="text-[10px] text-white/40">Model Ready</span>}
        </div>
      </div>
    </div>
  );
}

function Header({ title }) {
  const { result } = useModel();
  const canDownload = result?.excel_ready;

  return (
    <div
      className="h-14 flex-shrink-0 bg-[#1A1F36]/95 border-b border-white/[0.08] flex items-center gap-3 px-4"
      style={{ backdropFilter: 'blur(20px)' }}
    >
      <span className="font-bold text-sm text-white" style={{ fontFamily: 'var(--font-plus-jakarta), sans-serif' }}>
        K-Nexus.AI
      </span>
      <span className="text-white/30">|</span>
      <span className="text-white/70 text-sm">{title}</span>

      <div className="flex-1" />

      <Link
        href="/assumptions"
        className="text-xs text-white/50 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Run Model
      </Link>

      {canDownload ? (
        <a
          href={getDownloadUrl()}
          download="DataCenter_DCF_Model.xlsx"
          className="inline-flex items-center gap-2 bg-[#00338D] text-white text-sm font-semibold px-4 py-1.5 rounded-lg shadow-sm hover:bg-[#0044b8] transition-all duration-200 active:scale-[0.98]"
        >
          <Download size={14} />
          Download Excel
        </a>
      ) : (
        <button
          disabled
          className="inline-flex items-center gap-2 bg-white/10 text-white/30 text-sm font-semibold px-4 py-1.5 rounded-lg cursor-not-allowed"
        >
          <Download size={14} />
          Download Excel
        </button>
      )}
    </div>
  );
}

const PAGE_TITLES = {
  '/dashboard':   'Dashboard',
  '/assumptions': 'Assumptions',
  '/revenue':     'Revenue',
  '/capex':       'Capital Expenditure',
  '/pnl':         'P&L Statement',
  '/cashflow':    'Cash Flow Statement',
};

export default function AppShell({ children }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const title = PAGE_TITLES[pathname] ?? 'Dashboard';

  const toggle = () => setCollapsed(prev => !prev);

  return (
    <div className="flex h-screen overflow-hidden bg-[#F4F6F9]">
      <Sidebar collapsed={collapsed} onToggle={toggle} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
