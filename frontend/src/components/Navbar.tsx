import React from 'react';
import { ShieldCheck, UserCheck, Sparkles, AlertCircle } from 'lucide-react';
import { UserProfile } from '../types';

interface NavbarProps {
  currentUser: UserProfile | null;
  onSelectUser: (userId: string) => void;
  activeScenarioId?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ currentUser, onSelectUser, activeScenarioId }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-[#0B0F19]/90 backdrop-blur sticky top-0 z-40 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Sparkles className="w-5 h-5 text-slate-950 font-bold" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-lg tracking-wider text-white">FINORA</span>
            <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              PayPal AI Hackathon 2026
            </span>
          </div>
          <p className="text-[11px] text-slate-400">Financial Intelligence Network & Autonomous Payments</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Synthetic Data Marker Badge */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Synthetic Data Bank: Verified</span>
        </div>

        {/* Active Scenario Indicator */}
        {activeScenarioId && (
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-mono">
            <span>Scenario: {activeScenarioId.replace('scen_', '')}</span>
          </div>
        )}

        {/* Controlled Single-User Session Persona (usr_alex_chen) */}
        <div
          className="flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5"
          title="Controlled Single-User Hackathon Demo Session (usr_alex_chen)"
        >
          <UserCheck className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-medium text-slate-200">
            {currentUser?.full_name || 'Alex Chen'} (Senior SWE)
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            usr_alex_chen
          </span>
        </div>
      </div>
    </header>
  );
};
