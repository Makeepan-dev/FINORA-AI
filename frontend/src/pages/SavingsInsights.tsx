import React, { useState, useEffect } from 'react';
import {
  Sparkles, CheckCircle2, XCircle, Clock, ShieldCheck, ArrowRight,
  Target, TrendingUp, AlertCircle, DollarSign, Award
} from 'lucide-react';
import { api } from '../services/api';
import { ProductItem } from '../types';

interface SavingsInsightsProps {
  activeUserId: string;
  onSelectForCheckout?: (product: ProductItem) => void;
  onNavigateToGuardian?: () => void;
}

export const SavingsInsights: React.FC<SavingsInsightsProps> = ({
  activeUserId = 'usr_alex_chen',
  onSelectForCheckout,
  onNavigateToGuardian
}) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionToast, setActionToast] = useState<string | null>(null);

  const loadSavings = async () => {
    setLoading(true);
    try {
      const res = await api.getSavingsDashboard(activeUserId);
      setData(res);
    } catch (err) {
      console.error('Error loading savings dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSavings();
  }, [activeUserId]);

  const handleDecision = async (recId: string, decision: string) => {
    try {
      const res = await api.updateRecommendationDecision(recId, decision, activeUserId);
      setActionToast(res.note);
      await loadSavings();
    } catch (err) {
      console.error('Error updating recommendation decision:', err);
    }
  };

  const handleSandboxSwitch = (rec: any) => {
    if (!onSelectForCheckout) return;
    const isGym = rec.title.toLowerCase().includes('gym');
    onSelectForCheckout({
      product_id: isGym ? 'sav_gym_planet_20' : 'sav_stratavault_200gb',
      product_name: isGym
        ? 'Planet Fitness Classic Membership (1st Month Switch)'
        : 'StrataVault 200GB Right-Sized Storage Plan',
      category: 'subscriptions',
      merchant_id: 'm_verified_partner',
      price: isGym ? 20.0 : 4.99,
      shipping_cost: 0,
      total_cost: isGym ? 20.0 : 4.99,
      currency: 'USD',
      availability: true,
      rating: 4.9,
      review_count: 310,
      delivery_days: 0,
      warranty_months: 12,
      specifications: { plan_type: 'Money-Saving Switch' },
      description: `User-approved money-saving switch for: ${rec.title}`
    });
  };

  if (loading && !data) {
    return <div className="p-8 text-slate-400 text-sm">Loading Daily Money-Saving Intelligence...</div>;
  }

  if (!data) return null;

  const { summary, daily_insights, ranked_recommendations, goals } = data;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Daily Money-Saving Intelligence & Action Hub
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Multi-factor ranked savings opportunities combining Ledger, Subscriptions, GPS & AI Analysis
          </p>
        </div>

        {onNavigateToGuardian && (
          <button
            onClick={onNavigateToGuardian}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20"
          >
            <Sparkles className="w-4 h-4" />
            Ask AI Advisor: "Help me save $100 this month"
          </button>
        )}
      </div>

      {/* Critical Distinction Notice */}
      <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-200 leading-relaxed">
          <span className="font-bold text-amber-300 uppercase tracking-wide block mb-0.5">
            Financial Accounting Integrity Rule: Potential vs. Realized Savings
          </span>
          {summary.distinction_notice}
        </div>
      </div>

      {/* 4-Card Savings Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/90 border border-emerald-500/30">
          <span className="text-xs text-slate-400 block">Total Potential Monthly Savings</span>
          <p className="text-2xl font-extrabold text-emerald-400 mt-1">
            +${summary.potential_monthly_savings.toFixed(2)}/mo
          </p>
          <span className="text-[11px] text-emerald-300/80">
            +${summary.potential_annual_savings.toFixed(2)}/year estimated
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800">
          <span className="text-xs text-slate-400 block">Awaiting User Review ({summary.pending_count})</span>
          <p className="text-2xl font-bold text-amber-400 mt-1">
            ${summary.pending_review_monthly.toFixed(2)}/mo
          </p>
          <span className="text-[11px] text-slate-500">Requires explicit user approval</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-cyan-500/30">
          <span className="text-xs text-slate-400 block">Actions Accepted ({summary.accepted_count})</span>
          <p className="text-2xl font-bold text-cyan-400 mt-1">
            ${summary.accepted_actions_monthly.toFixed(2)}/mo
          </p>
          <span className="text-[11px] text-slate-400">Approved; pending next billing cycle</span>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/90 border border-purple-500/30">
          <span className="text-xs text-slate-400 block">Verified Realized Savings ({summary.realized_count})</span>
          <p className="text-2xl font-bold text-purple-400 mt-1">
            ${summary.verified_realized_savings.toFixed(2)}
          </p>
          <span className="text-[11px] text-slate-400">Confirmed by ledger refund/reduction</span>
        </div>
      </div>

      {actionToast && (
        <div className="p-3.5 rounded-xl bg-cyan-500/15 border border-cyan-500/40 text-cyan-200 text-xs font-medium flex items-center justify-between">
          <span>{actionToast}</span>
          <button onClick={() => setActionToast(null)} className="text-slate-400 hover:text-white font-bold">✕</button>
        </div>
      )}

      {/* Daily Insights Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
          Today's Personalized Money-Saving Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {daily_insights.map((ins: any) => (
            <div key={ins.id} className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">{ins.title}</span>
                <span className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 text-[11px] font-bold">
                  Impact: ~${Number(ins.impact_monthly).toFixed(2)}/mo
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{ins.message}</p>
              <div className="text-[10px] text-slate-500 font-mono">
                Evidence Source: {ins.evidence_type}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Multi-Factor Ranked Recommendations */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
            Prioritized Savings Opportunities (Ranked by Impact, Evidence Quality, Confidence & Effort)
          </h2>
        </div>

        <div className="space-y-4">
          {ranked_recommendations.map((rec: any, index: number) => (
            <div
              key={rec.id}
              className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                  <span className="h-7 w-7 rounded-lg bg-cyan-500/20 text-cyan-400 font-extrabold text-xs flex items-center justify-center border border-cyan-500/30">
                    #{index + 1}
                  </span>
                  <div>
                    <h3 className="font-bold text-white text-base">{rec.title}</h3>
                    <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px]">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 font-mono">
                        Rank Score: {rec.composite_rank_score}/100
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        Confidence: {(rec.confidence_score * 100).toFixed(0)}%
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 capitalize">
                        Effort: {rec.effort_level}
                      </span>
                      <span className={`px-2 py-0.5 rounded font-bold uppercase ${
                        rec.status === 'accepted'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : rec.status === 'rejected'
                          ? 'bg-rose-500/20 text-rose-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        Status: {rec.status}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-lg font-extrabold text-emerald-400">
                    +${rec.estimated_monthly_savings.toFixed(2)}/mo
                  </span>
                  <span className="block text-xs text-slate-400">
                    +${rec.estimated_annual_savings.toFixed(2)}/year
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <span className="text-rose-400 font-bold block mb-1">1. Problem Identified</span>
                  <p className="text-slate-300 leading-relaxed">{rec.problem_identified}</p>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <span className="text-cyan-400 font-bold block mb-1">2. Supporting Financial Evidence</span>
                  <p className="text-slate-300 leading-relaxed">{rec.supporting_evidence}</p>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <span className="text-emerald-400 font-bold block mb-1">3. Recommended Action</span>
                  <p className="text-slate-300 leading-relaxed">{rec.recommended_action}</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                <span className="text-[11px] text-slate-500">
                  User Permission Gate: FINORA never cancels or switches services without your confirmation.
                </span>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => handleDecision(rec.id, 'accepted')}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-bold"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Accept Recommendation
                  </button>

                  <button
                    onClick={() => handleDecision(rec.id, 'rejected')}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-500/20 text-slate-300 hover:text-rose-300 text-xs font-semibold"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Dismiss
                  </button>

                  {(rec.action_type === 'switch_alternative' || rec.title.toLowerCase().includes('storage')) && (
                    <button
                      onClick={() => handleSandboxSwitch(rec)}
                      className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs"
                    >
                      Execute Switch in PayPal Sandbox
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Savings Goal Progress */}
      {goals && goals.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white">Active Financial Goal: {goals[0].title}</h3>
            </div>
            <span className="text-xs text-cyan-400 font-bold">
              ${goals[0].current_amount.toFixed(2)} / ${goals[0].target_amount.toFixed(2)} ({goals[0].progress_percent}%)
            </span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400"
              style={{ width: `${Math.min(100, goals[0].progress_percent)}%` }}
            />
          </div>
          <p className="text-xs text-slate-400">
            Target Date: {goals[0].target_date} • Redirecting your +${summary.potential_monthly_savings.toFixed(2)}/mo in identified savings accelerates completion by 4.5 months.
          </p>
        </div>
      )}
    </div>
  );
};
