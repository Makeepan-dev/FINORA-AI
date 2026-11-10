import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Clock,
  Calendar,
  AlertCircle,
  ShieldCheck,
  CheckCircle2,
  DollarSign,
  PieChart as PieIcon,
  HelpCircle,
  Loader2,
  ArrowRight
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { api } from '../services/api';
import { IncomeIntelligenceData } from '../types';

interface IncomeProps {
  activeUserId: string;
}

const STREAM_COLORS = ['#10B981', '#06B6D4', '#8B5CF6', '#F59E0B', '#EC4899', '#64748B'];

export const Income: React.FC<IncomeProps> = ({ activeUserId }) => {
  const [data, setData] = useState<IncomeIntelligenceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIncomeData();
  }, [activeUserId]);

  const loadIncomeData = async () => {
    setLoading(true);
    try {
      const res = await api.getIncomeIntelligence(activeUserId);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center p-20 text-slate-400 text-sm gap-2">
        <Loader2 className="w-5 h-5 animate-spin text-emerald-400" />
        <span>Synthesizing multi-stream income intelligence...</span>
      </div>
    );
  }

  const { income_summary, stability_analysis, source_breakdown, expected_streams, estimated_streams, cash_flow_forecast } = data;

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-emerald-950/40 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Income Intelligence</h1>
            <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Multi-Stream Detection
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            First-class income classification, expected payment pipelines, volatility tracking & forward runway
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Accounting Rule: Never count expected income as money in hand</span>
        </div>
      </div>

      {/* 3 Core Income Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Received Income Card */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-emerald-500/30 space-y-2 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-xs font-semibold text-emerald-400">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>Received Income (Cleared)</span>
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 font-mono">In Bank</span>
          </div>
          <div className="text-3xl font-black text-white">
            ${income_summary.received_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">
            Actual settled funds verified across your connected accounts.
          </p>
        </div>

        {/* Expected Income Card */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-cyan-500/30 space-y-2 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-xs font-semibold text-cyan-400">
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              <span>Expected Income (Contractual)</span>
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 font-mono">Scheduled</span>
          </div>
          <div className="text-3xl font-black text-cyan-400">
            ${income_summary.expected_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">
            Contractual upcoming salary/retainers. <span className="text-cyan-300 font-medium">Not counted as settled.</span>
          </p>
        </div>

        {/* Estimated Income Card */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-amber-500/30 space-y-2 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl"></div>
          <div className="flex items-center justify-between text-xs font-semibold text-amber-400">
            <span className="flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4" />
              <span>Estimated Income (Pipeline)</span>
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 font-mono">Probabilistic</span>
          </div>
          <div className="text-3xl font-black text-amber-400">
            ${income_summary.estimated_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">
            Variable freelance proposals and quarterly dividend projections.
          </p>
        </div>
      </div>

      {/* Volatility & Stability Alert */}
      <div className={`p-4 rounded-xl flex items-start gap-3 border ${
        stability_analysis.irregular_income_detected
          ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
          : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
      }`}>
        <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">Income Stability: {stability_analysis.stability_rating}</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              Volatility: {stability_analysis.volatility_percentage}%
            </span>
          </div>
          <p className="text-slate-300 mt-1 leading-relaxed">
            {stability_analysis.notes} Baseline frequency: <span className="capitalize font-semibold text-white">{stability_analysis.frequency}</span>.
          </p>
        </div>
      </div>

      {/* Income Stream Breakdown & Expected Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Source Breakdown Pie Chart */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
          <div>
            <h3 className="font-bold text-white text-base">Income Stream Breakdown</h3>
            <p className="text-xs text-slate-400 mt-0.5">Automated classification across transaction markers</p>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={source_breakdown}
                  dataKey="amount"
                  nameKey="stream"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={4}
                >
                  {source_breakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={STREAM_COLORS[index % STREAM_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Received']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 pt-2 border-t border-slate-800/80">
            {source_breakdown.map((s, idx) => (
              <div key={s.stream} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2 text-slate-300">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: STREAM_COLORS[idx % STREAM_COLORS.length] }}></span>
                  <span>{s.stream}</span>
                </span>
                <span className="font-bold text-white">
                  ${s.amount.toLocaleString()} <span className="text-[11px] text-slate-500 font-normal">({s.percentage}%)</span>
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Expected & Estimated Streams Schedule */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
          <div>
            <h3 className="font-bold text-white text-base">Upcoming Inflows Schedule</h3>
            <p className="text-xs text-slate-400 mt-0.5">Contractual expected paydays & milestone billing</p>
          </div>

          <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
            {expected_streams.map((exp) => (
              <div key={exp.stream_id} className="p-3.5 rounded-xl bg-slate-950/60 border border-cyan-500/20 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-xs">{exp.source}</span>
                  <span className="text-xs font-black text-cyan-400">+${exp.amount.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Due: <span className="text-white font-medium">{exp.expected_date}</span></span>
                  <span className="text-emerald-400 font-semibold font-mono">Confidence: {Math.round(exp.confidence_score * 100)}%</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-snug">{exp.notes}</p>
              </div>
            ))}

            {estimated_streams.map((est) => (
              <div key={est.stream_id} className="p-3.5 rounded-xl bg-slate-950/60 border border-amber-500/20 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-xs">{est.source}</span>
                  <span className="text-xs font-black text-amber-400">+${est.amount.toFixed(2)}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Window: <span className="text-white font-medium">{est.projected_window}</span></span>
                  <span className="text-amber-400 font-semibold font-mono">Confidence: {Math.round(est.confidence_score * 100)}%</span>
                </div>
                <p className="text-[11px] text-slate-400 leading-snug">{est.notes}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 30 / 60 / 90 Day Cash-Flow & Runway Forecast */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/80 space-y-4">
        <div>
          <h3 className="font-bold text-white text-base">Forward 30 / 60 / 90 Day Cash-Flow Forecast</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Combined projections factoring verified liquid cash, contractual inflows, and fixed category obligations
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {cash_flow_forecast.map((fc) => (
            <div key={fc.period} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{fc.period}</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">
                  {fc.runway_months} mo runway
                </span>
              </div>

              <div className="space-y-1.5 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span className="text-slate-500">Starting Liquid Cash:</span>
                  <span>${fc.current_liquid_cash.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Expected Inflows:</span>
                  <span className="text-emerald-400 font-medium">+${fc.expected_inflows.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Fixed Outflows:</span>
                  <span className="text-rose-400 font-medium">-${fc.projected_fixed_outflows.toLocaleString()}</span>
                </div>
                <div className="pt-2 border-t border-slate-800 flex justify-between font-bold text-sm">
                  <span className="text-slate-200">Projected Cash:</span>
                  <span className="text-cyan-400">${fc.projected_end_cash.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
