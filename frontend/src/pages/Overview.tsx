import React from 'react';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { DashboardData } from '../types';

interface OverviewProps {
  data: DashboardData;
  onNavigateToGuardian: () => void;
  onNavigateToShopping: () => void;
}

const PIE_COLORS = ['#06B6D4', '#10B981', '#8B5CF6', '#F59E0B', '#EC4899', '#3B82F6', '#64748B'];

export const Overview: React.FC<OverviewProps> = ({
  data,
  onNavigateToGuardian,
  onNavigateToShopping
}) => {
  const { summary, spending_breakdown, monthly_trends, budget_progress, recurring_payments, alerts, user } = data;

  return (
    <div className="space-y-6 pb-12">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Financial Intelligence Overview
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Active Profile: <span className="text-cyan-400 font-semibold">{user.full_name}</span> ({user.employment}) • Risk Profile: <span className="capitalize text-slate-300">{user.risk_preference}</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onNavigateToGuardian}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Ask AI Advisor: "Help me save $100/mo"</span>
          </button>
          <button
            onClick={onNavigateToShopping}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs border border-slate-700 transition-all"
          >
            <span>Shopping Assistant</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Remaining Available Money */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-cyan-500/30 space-y-2">
          <div className="flex items-center justify-between text-cyan-300 text-xs font-medium">
            <span>Remaining Available Money</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white">
            ${summary.net_cash_flow.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">
            Income − Expenses (Total Balance: ${summary.total_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })})
          </p>
        </div>

        {/* Monthly Income */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Monthly Inflows</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-emerald-400">
            +${summary.monthly_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">
            Verified salary & client deposits
          </p>
        </div>

        {/* Monthly Expenses */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Monthly Expenses</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-rose-400">
            -${summary.monthly_expenses.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">
            Net cash flow: <span className="font-semibold text-cyan-400">${summary.net_cash_flow.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
          </p>
        </div>

        {/* Optimization Savings */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Identified Potential Savings</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <PiggyBank className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-amber-400">
            ${summary.potential_monthly_savings.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            <span className="text-xs font-normal text-slate-400">/mo</span>
          </div>
          <p className="text-[11px] text-slate-400">
            From low-usage subscriptions & API idle seats
          </p>
        </div>
      </div>

      {/* Alerts Row */}
      {alerts && alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-xl flex items-start gap-3 border ${
                alert.type === 'opportunity'
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              }`}
            >
              <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-white">{alert.title}</h4>
                <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">{alert.description}</p>
              </div>
              <button
                onClick={onNavigateToGuardian}
                className="text-xs font-semibold underline underline-offset-4 hover:opacity-80"
              >
                Review with AI
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monthly Trend Bar Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-white text-base">Historical Cash Flow (Last 6 Months)</h3>
              <p className="text-xs text-slate-400 mt-0.5">Authoritative monthly income vs expenses</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-3 h-3 rounded-sm bg-emerald-500"></span> Income
              </span>
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-3 h-3 rounded-sm bg-rose-500"></span> Expenses
              </span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly_trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="month" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(value: any) => [`$${Number(value).toLocaleString()}`, '']}
                />
                <Bar dataKey="income" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="expenses" fill="#F43F5E" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Spending Pie Chart */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
          <div>
            <h3 className="font-bold text-white text-base">Monthly Spending Breakdown</h3>
            <p className="text-xs text-slate-400 mt-0.5">Category distribution</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={spending_breakdown}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {spending_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Spent']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
            {spending_breakdown.slice(0, 4).map((c, i) => (
              <div key={c.category} className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}></span>
                <span className="truncate">{c.category}: {c.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Budget Progress & Recurring Subscriptions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Budget Progress Bars */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-base">Monthly Budget Progress</h3>
            <span className="text-xs text-slate-400">Threshold alerts at 85%</span>
          </div>
          <div className="space-y-3.5">
            {budget_progress.map((b) => (
              <div key={b.category} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-200">{b.category}</span>
                  <span className="text-slate-400">
                    <span className="text-white font-medium">${b.spent.toFixed(2)}</span> of ${b.limit.toFixed(2)} ({b.percentage_used}%)
                  </span>
                </div>
                <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      b.status === 'exceeded'
                        ? 'bg-rose-500'
                        : b.status === 'warning'
                        ? 'bg-amber-400'
                        : 'bg-cyan-500'
                    }`}
                    style={{ width: `${Math.min(100, b.percentage_used)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recurring Payments Table */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-base">Recurring Commitments</h3>
            <span className="text-xs font-semibold text-cyan-400">${summary.total_subscription_cost.toFixed(2)}/mo total</span>
          </div>
          <div className="divide-y divide-slate-800/80 overflow-y-auto max-h-72 pr-1">
            {recurring_payments.map((sub) => (
              <div key={sub.subscription_id} className="py-3 flex items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-white">{sub.name}</span>
                    {sub.evidence_status === 'confirmed_low_usage' && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                        Low Usage
                      </span>
                    )}
                    {sub.evidence_status === 'unverified_missing' && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                        No Telemetry
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {sub.merchant_name} • Renews on {sub.next_date}
                  </p>
                </div>
                <div className="text-right">
                  <span className="font-bold text-sm text-slate-200">${sub.amount.toFixed(2)}</span>
                  <span className="text-[11px] text-slate-500 block">/{sub.frequency}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
