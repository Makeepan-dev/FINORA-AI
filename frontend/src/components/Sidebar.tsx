import React from 'react';
import {
  LayoutDashboard,
  Receipt,
  TrendingUp,
  Bot,
  ShoppingBag,
  CreditCard,
  Link2,
  Settings,
  ArrowUpRight,
  Cpu,
  MapPin,
  Sparkles
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  savingsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, savingsCount = 0 }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions & CSV', icon: Receipt },
    {
      id: 'guardian',
      label: 'AI Advisor & Subscriptions',
      icon: Bot,
      badge: savingsCount > 0 ? `+$${savingsCount}/mo` : undefined
    },
    { id: 'nearby', label: 'Nearby Savings (GPS)', icon: MapPin, badge: 'GPS' },
    { id: 'savings', label: 'Money-Saving Insights', icon: Sparkles, badge: 'Save $100+' },
    { id: 'payments', label: 'PayPal Sandbox Action', icon: CreditCard },
    { id: 'income', label: 'Income Intelligence', icon: TrendingUp },
    { id: 'automation', label: 'Automation & Engine', icon: Cpu, badge: 'Active' },
    { id: 'shopping', label: 'Shopping Agent', icon: ShoppingBag },
    { id: 'connections', label: 'Connected Accounts', icon: Link2 },
    { id: 'settings', label: 'Settings & Data Bank', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0B0F19] flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <nav className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-500">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Security & Sandbox Info Card */}
      <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2">
        <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
          <span>Sandbox Mode</span>
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Payments execute in official PayPal Sandbox. Zero live money credentials are required.
        </p>
        <div className="pt-1">
          <a
            href="https://developer.paypal.com/dashboard/"
            target="_blank"
            rel="noreferrer"
            className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
          >
            PayPal Developer Portal <ArrowUpRight className="w-3 h-3" />
          </a>
        </div>
      </div>
    </aside>
  );
};
