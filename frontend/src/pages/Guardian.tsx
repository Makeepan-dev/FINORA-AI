import React, { useState } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  CheckCircle,
  HelpCircle,
  AlertTriangle,
  Lightbulb,
  ShieldCheck,
  ShieldAlert,
  Loader2,
  TrendingDown,
  ArrowRight,
  Activity,
  Layers,
  Info,
  BookOpen,
  Compass
} from 'lucide-react';
import { api } from '../services/api';
import { ChatMessage, DashboardData, SubscriptionClassification } from '../types';

interface GuardianProps {
  dashboardData: DashboardData;
  activeUserId: string;
}

const PROMPT_SUGGESTIONS = [
  "Help me save $100 this month",
  "How much did I spend this month and where is most of my money going?",
  "Can I afford to buy a $1200 laptop?",
  "Perform a complete subscription audit. Classify every active subscription as KEEP, REDUCE, REPLACE, ELIMINATE or INVESTIGATE.",
  "Is this $120 gym membership worth keeping?",
  "How much am I spending on subscriptions?",
  "Should I pay an extra $250/mo on my loan early?",
  "What is my composite financial health score?",
  "How much do I need to save monthly for a $10,000 goal in 24 months?",
  "What is the opportunity cost of spending $1,500 over 10 years?",
  "I have changed my circumstances. I am now using AI APIs every day for my development work and consuming approximately 50,000 tokens daily. Should I still downgrade Cognition Engine Pro ($35/month), considering that its usage was previously zero for 45 days?"
];

export const Guardian: React.FC<GuardianProps> = ({ dashboardData, activeUserId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'agent',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      aiResponse: {
        provider: 'gemini',
        model: 'gemini-flash-lite-latest',
        status: 'ready',
        is_fallback: false,
        factual_analysis: (
          `Hello! I am your FINORA Financial Guardian.\n\n` +
          `I have ingested your reconciled financial records. Current monthly income is **$${dashboardData.summary.monthly_income.toLocaleString()}**, monthly expenses are **$${dashboardData.summary.monthly_expenses.toLocaleString()}**, and I have identified **$${dashboardData.summary.potential_monthly_savings}/mo** in actionable subscription optimizations.\n\n` +
          `Ask me to perform a complete subscription audit, evaluate which expensive services to keep, or audit budget variance.`
        ),
        estimates: [
          { label: "Total Active Commitments", value: "7 services" },
          { label: "Annual Optimization Cushion", value: `$${dashboardData.summary.potential_monthly_savings * 12}/yr` }
        ],
        recommendations: [
          "Perform a complete subscription audit across all 7 commitments.",
          "Identify high-cost utilities that should be retained for business continuity."
        ],
        unknowns: "External private investment portfolios not connected to demo accounts."
      }
    }
  ]);

  const [inputPrompt, setInputPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (promptToSend?: string) => {
    const text = promptToSend || inputPrompt;
    if (!text.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt('');
    setLoading(true);

    try {
      const res = await api.chatWithGuardian(text, activeUserId);
      const agentMsg: ChatMessage = {
        id: `agent_${Date.now()}`,
        sender: 'agent',
        aiResponse: res.ai_response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'agent',
        text: `Error contacting intelligence engine: ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const getClassificationBadge = (classification: string) => {
    const c = classification.toUpperCase();
    switch (c) {
      case 'KEEP':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'REDUCE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'REPLACE':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'ELIMINATE':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'INVESTIGATE':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/30 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Bot className="w-6 h-6 text-slate-950 font-bold" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Financial Guardian Agent
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                AI Reasoning Connected
              </span>
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Deterministic calculations • Google Gemini Free-Tier • 100% Zero-Cost Guarantee
            </p>
          </div>
        </div>

        <div className="text-right hidden sm:block">
          <span className="text-[11px] text-slate-500 uppercase tracking-widest font-bold">Optimization Cushion</span>
          <span className="text-lg font-black text-amber-400 block">+${dashboardData.summary.potential_monthly_savings}/mo</span>
        </div>
      </div>

      {/* Suggested Prompts Pills */}
      <div className="space-y-1.5">
        <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Suggested Questions:</span>
        <div className="flex flex-wrap gap-2">
          {PROMPT_SUGGESTIONS.map((sug, i) => (
            <button
              key={i}
              onClick={() => handleSend(sug)}
              disabled={loading}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium transition-all hover:border-cyan-500/40 text-left"
            >
              {sug.length > 70 ? `${sug.slice(0, 68)}...` : sug}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Log */}
      <div className="space-y-4 min-h-[420px]">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'user' ? (
              <div className="max-w-xl px-4 py-3 rounded-2xl bg-cyan-600 text-white text-xs font-medium shadow-md">
                {msg.text}
              </div>
            ) : (
              <div className="max-w-4xl w-full p-5 rounded-2xl bg-slate-900/95 border border-slate-800 space-y-5 shadow-xl">
                {/* Agent Header with Model Info */}
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold text-white tracking-wide">Financial Guardian Reasoning</span>
                    
                    {/* Model / Provider Badge */}
                    <div className="flex items-center gap-1.5">
                      {msg.aiResponse?.is_fallback ? (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          Deterministic Fallback
                        </span>
                      ) : msg.aiResponse?.escalated_to_ai ? (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          Google Gemini ({msg.aiResponse.model || 'gemini-flash-lite-latest'})
                        </span>
                      ) : msg.aiResponse?.knowledge_sufficiency === 'SUFFICIENT' ? (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono flex items-center gap-1">
                          <BookOpen className="w-3 h-3" />
                          Internal Knowledge & Algorithms (Zero AI)
                        </span>
                      ) : (
                        <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                          {msg.aiResponse?.provider || 'Verified Deterministic Engine'}
                        </span>
                      )}

                      {/* Applied Knowledge IDs */}
                      {msg.aiResponse?.applied_knowledge_ids && msg.aiResponse.applied_knowledge_ids.length > 0 && (
                        <span className="hidden sm:inline-block text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                          {msg.aiResponse.applied_knowledge_ids.join(', ')}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-[11px] text-slate-500">{msg.timestamp}</span>
                </div>

                {/* Fallback Notice if triggered */}
                {msg.aiResponse?.is_fallback && msg.aiResponse.fallback_reason && (
                  <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-center gap-2">
                    <Info className="w-4 h-4 flex-shrink-0" />
                    <span>{msg.aiResponse.fallback_reason}</span>
                  </div>
                )}

                {/* Plain text fallback */}
                {msg.text && <p className="text-xs text-slate-200">{msg.text}</p>}

                {msg.aiResponse && (
                  <div className="space-y-5 text-xs">
                    {/* 1. Verified Financial Facts / Factual Analysis */}
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-1.5 text-cyan-400 font-semibold uppercase tracking-wider text-[11px]">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>Verified Financial Facts & Synthesis</span>
                      </div>
                      <div className="text-slate-200 leading-relaxed whitespace-pre-line pl-4 border-l-2 border-cyan-500/30">
                        {msg.aiResponse.factual_analysis}
                      </div>
                    </div>

                    {/* 2. Structured Subscription Classifications Table / Cards */}
                    {msg.aiResponse.classifications && msg.aiResponse.classifications.length > 0 && (
                      <div className="space-y-2 pt-1">
                        <div className="flex items-center justify-between text-cyan-400 font-semibold uppercase tracking-wider text-[11px]">
                          <div className="flex items-center gap-1.5">
                            <Layers className="w-3.5 h-3.5" />
                            <span>
                              {msg.aiResponse.is_subscription_audit
                                ? `Active Commitments Audit (${msg.aiResponse.classifications.length} Services Evaluated)`
                                : `Evaluated Subscription Context`}
                            </span>
                          </div>
                          <span className="text-slate-500 text-[10px] lowercase">
                            {msg.aiResponse.is_subscription_audit ? '100% complete audit' : 'contextual evaluation'}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 gap-2.5 pl-2">
                          {msg.aiResponse.classifications.map((item: SubscriptionClassification, i: number) => (
                            <div
                              key={i}
                              className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700/80 transition-all space-y-2"
                            >
                              <div className="flex flex-wrap items-center justify-between gap-2">
                                <div className="flex items-center gap-2">
                                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${getClassificationBadge(item.classification)}`}>
                                    {item.classification}
                                  </span>
                                  <span className="font-bold text-white text-xs">{item.subscription_name}</span>
                                  <span className="text-[11px] text-slate-400">({item.merchant})</span>
                                </div>
                                <div className="flex items-center gap-2 text-right">
                                  <span className="text-white font-mono font-bold">${item.monthly_cost.toFixed(2)}/mo</span>
                                  <span className="text-slate-500 text-[10px] font-mono">(${item.annual_cost.toFixed(2)}/yr)</span>
                                  {item.potential_savings > 0 && (
                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                                      Save ${item.potential_savings.toFixed(2)}/mo
                                    </span>
                                  )}
                                </div>
                              </div>

                              <div className="text-[11px] text-slate-300 pl-2 border-l border-slate-800 space-y-1">
                                <p><span className="text-slate-400 font-semibold">Evidence:</span> {item.usage_evidence}</p>
                                <p><span className="text-slate-400 font-semibold">Assessment:</span> {item.value_assessment}</p>
                                <p><span className="text-cyan-400 font-semibold">Action:</span> {item.recommendation}</p>
                              </div>

                              <div className="flex flex-wrap items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-900">
                                <span>Confidence: {Math.round(item.confidence_score * 100)}%</span>
                                {item.user_confirmation_needed ? (
                                  <span className="text-amber-400 flex items-center gap-1">
                                    <AlertTriangle className="w-3 h-3" />
                                    Requires User Confirmation
                                  </span>
                                ) : (
                                  <span className="text-emerald-400 flex items-center gap-1">
                                    <ShieldCheck className="w-3 h-3" />
                                    Autonomous Verification Grounded
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 3. Estimates & Calculated Projections */}
                    {msg.aiResponse.estimates && msg.aiResponse.estimates.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <div className="flex items-center gap-1.5 text-amber-400 font-semibold uppercase tracking-wider text-[11px]">
                          <Lightbulb className="w-3.5 h-3.5" />
                          <span>Calculated Projections & Savings</span>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pl-2">
                          {msg.aiResponse.estimates.map((est, i) => (
                            <div key={i} className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60">
                              <span className="text-[10px] text-slate-400 block truncate">{est.label}</span>
                              <span className="text-xs font-bold text-amber-300 block mt-0.5">{est.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 4. Actionable Recommendations */}
                    {msg.aiResponse.recommendations && msg.aiResponse.recommendations.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <div className="flex items-center gap-1.5 text-emerald-400 font-semibold uppercase tracking-wider text-[11px]">
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Actionable Recommendations</span>
                        </div>
                        <ul className="space-y-1 pl-4 list-disc list-inside text-slate-300">
                          {msg.aiResponse.recommendations.map((rec, i) => (
                            <li key={i} className="leading-relaxed">{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 5. Unknown Information & Data Boundaries */}
                    {msg.aiResponse.unknowns && (
                      <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-[11px] text-slate-400 flex items-start gap-2">
                        <HelpCircle className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="font-semibold text-slate-300">Data Boundaries & Unknowns: </span>
                          <span>{msg.aiResponse.unknowns}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
            <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
            <span>Financial Guardian is evaluating deterministic records with AI reasoning...</span>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => { e.preventDefault(); handleSend(); }}
        className="flex items-center gap-2 p-2 rounded-2xl bg-slate-900 border border-slate-800 focus-within:border-cyan-500/50 shadow-2xl"
      >
        <input
          type="text"
          placeholder="Ask Financial Guardian about subscription audits, expensive utilities to keep, or missing evidence..."
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          className="flex-1 bg-transparent px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !inputPrompt.trim()}
          className="p-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 font-bold transition-all shadow-md shadow-cyan-500/20"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
