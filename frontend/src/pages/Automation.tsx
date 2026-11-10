import React, { useState, useEffect } from 'react';
import {
  Cpu,
  ShieldCheck,
  Calculator,
  GitMerge,
  Zap,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Play,
  RotateCcw,
  Search,
  ArrowRight,
  Clock,
  DollarSign,
  Layers,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import {
  FormulaEntry,
  FormulaSummary,
  CalculationResult,
  AutomationRule,
  ExecutionLog,
  PreparedAction,
  OptimizationOpportunity,
  CompositionWorkflowResult
} from '../types';

export const Automation: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'automations' | 'safety' | 'formulas' | 'composition' | 'optimization'>('automations');
  const [loading, setLoading] = useState<boolean>(true);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Data states
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [history, setHistory] = useState<ExecutionLog[]>([]);
  const [pendingActions, setPendingActions] = useState<PreparedAction[]>([]);
  const [formulas, setFormulas] = useState<FormulaEntry[]>([]);
  const [summary, setSummary] = useState<FormulaSummary | null>(null);
  const [opportunities, setOpportunities] = useState<OptimizationOpportunity[]>([]);

  // Formula Explorer states
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [formulaSearch, setFormulaSearch] = useState<string>('');
  const [selectedFormula, setSelectedFormula] = useState<FormulaEntry | null>(null);
  const [calcInputs, setCalcInputs] = useState<Record<string, any>>({});
  const [calcResult, setCalcResult] = useState<CalculationResult | null>(null);
  const [calcLoading, setCalcLoading] = useState<boolean>(false);

  // Decision Studio states
  const [decisionType, setDecisionType] = useState<'purchase' | 'subscription' | 'loan'>('purchase');
  const [purchaseForm, setPurchaseForm] = useState({
    item_name: 'Dell UltraSharp 4K Monitor',
    price: 650.0,
    shipping: 15.0,
    tax_pct: 8.5,
    available_liquid_cash: 8450.0,
    monthly_income: 6200.0,
    monthly_expenses: 3400.0,
    essential_expenses: 2400.0
  });
  const [compositionResult, setCompositionResult] = useState<CompositionWorkflowResult | null>(null);
  const [compLoading, setCompLoading] = useState<boolean>(false);

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [rData, hData, pData, fData, sData, oData] = await Promise.all([
        api.getAutomationRules(),
        api.getAutomationHistory(),
        api.getPendingActions(),
        api.getFormulas(),
        api.getFormulaCatalogSummary(),
        api.getOptimizationOpportunities()
      ]);
      setRules(rData);
      setHistory(hData);
      setPendingActions(pData);
      setFormulas(fData);
      setSummary(sData);
      setOpportunities(oData);
      if (fData.length > 0 && !selectedFormula) {
        setSelectedFormula(fData[0]);
        initInputsForFormula(fData[0]);
      }
    } catch (err: any) {
      console.error('Failed to load automation data:', err);
      showNotification(err.message || 'Error loading automation engine', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message: string, type: 'success' | 'error') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleToggleRule = async (ruleId: string, currentEnabled: boolean) => {
    try {
      await api.toggleAutomationRule(ruleId, !currentEnabled);
      setRules(prev => prev.map(r => r.rule_id === ruleId ? { ...r, is_enabled: !currentEnabled } : r));
      showNotification(`Rule ${!currentEnabled ? 'enabled' : 'disabled'} successfully`, 'success');
    } catch (err: any) {
      showNotification('Failed to toggle rule', 'error');
    }
  };

  const handleTestTrigger = async (ruleId: string) => {
    try {
      const res = await api.triggerAutomationTest(ruleId, {
        amount: 450.0,
        merchant: 'Downtown Tech Goods',
        potential_savings: 120.0
      });
      if (res.success) {
        showNotification(`Trigger test executed: ${res.log.status}`, 'success');
        const [updatedHistory, updatedPending] = await Promise.all([
          api.getAutomationHistory(),
          api.getPendingActions()
        ]);
        setHistory(updatedHistory);
        setPendingActions(updatedPending);
      }
    } catch (err: any) {
      showNotification('Failed to trigger test', 'error');
    }
  };

  const handleApproveAction = async (actionId: string) => {
    try {
      const res = await api.approveAction(actionId);
      if (res.success) {
        showNotification('Action approved and executed securely', 'success');
        setPendingActions(prev => prev.filter(a => a.action_id !== actionId));
        const updatedHistory = await api.getAutomationHistory();
        setHistory(updatedHistory);
      }
    } catch (err: any) {
      showNotification(err.message || 'Approval failed', 'error');
    }
  };

  const handleRejectAction = async (actionId: string) => {
    try {
      const res = await api.rejectAction(actionId, 'User declined in action safety center');
      if (res.success) {
        showNotification('Action declined and archived', 'success');
        setPendingActions(prev => prev.filter(a => a.action_id !== actionId));
      }
    } catch (err: any) {
      showNotification('Rejection failed', 'error');
    }
  };

  const initInputsForFormula = (f: FormulaEntry) => {
    const defaultInputs: Record<string, any> = {};
    f.required_inputs.forEach(inp => {
      defaultInputs[inp.name] = inp.default !== null && inp.default !== undefined ? inp.default : (inp.type === 'int' ? 12 : (inp.type === 'Decimal' ? 1000 : ''));
    });
    f.optional_inputs.forEach(inp => {
      if (inp.default !== null && inp.default !== undefined) {
        defaultInputs[inp.name] = inp.default;
      }
    });
    setCalcInputs(defaultInputs);
    setCalcResult(null);
  };

  const handleSelectFormula = (f: FormulaEntry) => {
    setSelectedFormula(f);
    initInputsForFormula(f);
  };

  const handleRunCalculation = async () => {
    if (!selectedFormula) return;
    setCalcLoading(true);
    try {
      const res = await api.executeFormula(selectedFormula.unique_id, calcInputs);
      setCalcResult(res);
      showNotification('Formula executed with exact Decimal precision', 'success');
    } catch (err: any) {
      showNotification(err.message || 'Calculation error', 'error');
    } finally {
      setCalcLoading(false);
    }
  };

  const handleRunPurchaseDecision = async () => {
    setCompLoading(true);
    try {
      const res = await api.evaluatePurchaseAffordability(purchaseForm);
      setCompositionResult(res);
      showNotification(`Affordability evaluated: ${res.decision_verdict}`, 'success');
    } catch (err: any) {
      showNotification(err.message || 'Decision workflow error', 'error');
    } finally {
      setCompLoading(false);
    }
  };

  const filteredFormulas = formulas.filter(f => {
    const matchDomain = selectedDomain === 'ALL' || f.domain.includes(selectedDomain);
    const matchSearch = !formulaSearch || f.name.toLowerCase().includes(formulaSearch.toLowerCase()) || f.description.toLowerCase().includes(formulaSearch.toLowerCase());
    return matchDomain && matchSearch;
  });

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      {notification && (
        <div className={`fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg shadow-xl border text-sm font-medium flex items-center gap-2 ${
          notification.type === 'success'
            ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
            : 'bg-rose-950/90 border-rose-500/50 text-rose-300'
        }`}>
          {notification.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
          {notification.message}
        </div>
      )}

      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-[#0E1526] to-slate-900 border border-slate-800">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
            <Cpu className="w-4 h-4" />
            <span>Autonomous Intelligence & Formula Engine</span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">
            Financial Optimization & Automation Network
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Multi-domain formula registry, multi-step decision composition, and event-driven automation with cryptographic Step 14 user authorization.
          </p>
        </div>

        {/* Quick Metrics */}
        <div className="flex items-center gap-3">
          <div className="px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Registered Formulas</div>
            <div className="text-lg font-bold text-cyan-400">{summary?.total_registered_formulas || 26}</div>
          </div>
          <div className="px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Active Rules</div>
            <div className="text-lg font-bold text-emerald-400">{rules.filter(r => r.is_enabled).length}</div>
          </div>
          <div className="px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-800 text-center">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Pending Approvals</div>
            <div className={`text-lg font-bold ${pendingActions.length > 0 ? 'text-amber-400 animate-pulse' : 'text-slate-400'}`}>
              {pendingActions.length}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubTab('automations')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'automations'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <Zap className="w-3.5 h-3.5" />
          <span>Active Rules ({rules.length})</span>
        </button>

        <button
          onClick={() => setActiveSubTab('safety')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all relative ${
            activeSubTab === 'safety'
              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Action Safety Gate</span>
          {pendingActions.length > 0 && (
            <span className="h-2 w-2 rounded-full bg-amber-400 animate-ping"></span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('formulas')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'formulas'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <Calculator className="w-3.5 h-3.5" />
          <span>Formula Registry & Engine</span>
        </button>

        <button
          onClick={() => setActiveSubTab('composition')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'composition'
              ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <GitMerge className="w-3.5 h-3.5" />
          <span>Decision Composition Studio</span>
        </button>

        <button
          onClick={() => setActiveSubTab('optimization')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'optimization'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
          }`}
        >
          <TrendingUp className="w-3.5 h-3.5" />
          <span>Ranked Opportunities</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* SUB-TAB 1: AUTOMATIONS & TRIGGER MONITOR */}
      {/* ========================================================================= */}
      {activeSubTab === 'automations' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rules.map(rule => (
              <div
                key={rule.rule_id}
                className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
                      {rule.category}
                    </span>
                    <button
                      onClick={() => handleToggleRule(rule.rule_id, rule.is_enabled)}
                      className={`text-xs px-2.5 py-1 rounded-full font-semibold border transition-all ${
                        rule.is_enabled
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                          : 'bg-slate-800 text-slate-500 border-slate-700'
                      }`}
                    >
                      {rule.is_enabled ? 'Active' : 'Disabled'}
                    </button>
                  </div>
                  <h3 className="text-sm font-semibold text-white">{rule.name}</h3>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">{rule.description}</p>
                </div>

                <div className="pt-2 border-t border-slate-800/80 space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Trigger: <strong className="text-slate-300">{rule.trigger_type}</strong></span>
                    <span>Safety: <strong className="text-amber-400">{rule.safety_level.replace('LEVEL_', 'L')}</strong></span>
                  </div>
                  <button
                    onClick={() => handleTestTrigger(rule.rule_id)}
                    className="w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-slate-800/90 hover:bg-slate-800 text-xs text-slate-300 hover:text-white transition-all font-medium border border-slate-700/60"
                  >
                    <Play className="w-3 h-3 text-cyan-400" />
                    <span>Test Trigger</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Execution History Table */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                <span>Live Automation Audit Log</span>
              </h2>
              <span className="text-xs text-slate-500">{history.length} logged events</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">Timestamp</th>
                    <th className="pb-2">Rule</th>
                    <th className="pb-2">Domain</th>
                    <th className="pb-2">Status</th>
                    <th className="pb-2">Audit Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {history.slice(-8).reverse().map(log => (
                    <tr key={log.log_id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 text-slate-500 whitespace-nowrap">
                        {new Date(log.execution_timestamp).toLocaleTimeString()}
                      </td>
                      <td className="py-2.5 font-medium text-slate-200">{log.rule_name}</td>
                      <td className="py-2.5 text-cyan-400">{log.category}</td>
                      <td className="py-2.5">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          log.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400' :
                          log.status === 'USER_APPROVAL_PENDING' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-slate-800 text-slate-400'
                        }`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="py-2.5 text-slate-400 max-w-md truncate">{log.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 2: ACTION SAFETY GATE (LEVEL 2 & 3 USER APPROVAL) */}
      {/* ========================================================================= */}
      {activeSubTab === 'safety' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 flex-shrink-0 text-amber-400 mt-0.5" />
            <div>
              <strong className="font-bold text-white block">Step 14 User Authorization Policy Enforced:</strong>
              Autonomous AI engines and background rules can prepare actions but are cryptographically forbidden from moving money, cancelling subscriptions, or modifying live accounts without explicit user confirmation.
            </div>
          </div>

          {pendingActions.length === 0 ? (
            <div className="p-12 text-center rounded-2xl bg-slate-900/50 border border-slate-800 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
              <h3 className="text-base font-semibold text-white">All Clear</h3>
              <p className="text-xs text-slate-400">Zero pending financial actions requiring approval at this time.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingActions.map(action => (
                <div
                  key={action.action_id}
                  className="p-5 rounded-xl bg-slate-900/90 border border-amber-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg shadow-amber-950/10"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40">
                        Level 3 Approval Required
                      </span>
                      <span className="text-xs text-slate-500 font-mono">ID: {action.action_id}</span>
                    </div>
                    <h3 className="text-base font-bold text-white">{action.title}</h3>
                    <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">{action.description}</p>
                    <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
                      <span>Target: <strong className="text-slate-200">{action.target_merchant_or_payee}</strong></span>
                      <span>Amount: <strong className="text-emerald-400">${action.amount.toFixed(2)} {action.currency}</strong></span>
                      <span>Action Type: <code className="text-cyan-400">{action.action_type}</code></span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button
                      onClick={() => handleRejectAction(action.action_id)}
                      className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5"
                    >
                      <XCircle className="w-3.5 h-3.5 text-rose-400" />
                      <span>Decline</span>
                    </button>
                    <button
                      onClick={() => handleApproveAction(action.action_id)}
                      className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white transition-all shadow-md shadow-emerald-950/30 flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Authorize & Execute</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 3: FORMULA REGISTRY & INTERACTIVE CALCULATOR */}
      {/* ========================================================================= */}
      {activeSubTab === 'formulas' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Formula Catalogue Browser */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search 26+ formulas..."
                  value={formulaSearch}
                  onChange={(e) => setFormulaSearch(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="ALL">All Domains</option>
                <option value="Core_Financial_Math">Core Math (A)</option>
                <option value="Personal_Income_Expenses">Income & Expenses (B)</option>
                <option value="Savings_Financial_Goals">Savings Goals (C)</option>
                <option value="Banking_Deposits">Banking & Deposits (D)</option>
                <option value="Loans_And_Debt">Loans & Debt (E)</option>
                <option value="Credit_Cards">Credit Cards (F)</option>
                <option value="Investments_And_Wealth">Investments (G)</option>
                <option value="Taxation">Taxation (H)</option>
                <option value="Shopping_Commerce">Commerce & TCO (K)</option>
                <option value="Advanced_Financial_Models">Advanced Models (O)</option>
                <option value="Financial_Decision_Metrics">Decision Metrics (P)</option>
              </select>
            </div>

            <div className="space-y-2 max-h-[560px] overflow-y-auto pr-1">
              {filteredFormulas.map(f => (
                <div
                  key={f.unique_id}
                  onClick={() => handleSelectFormula(f)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                    selectedFormula?.unique_id === f.unique_id
                      ? 'bg-cyan-950/30 border-cyan-500/50 shadow-md'
                      : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] text-cyan-400 font-semibold">{f.domain.replace('_', ' ')}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                      f.status === 'EXECUTABLE_TESTED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {f.status.replace('_', ' ')}
                    </span>
                  </div>
                  <h4 className="font-bold text-white">{f.name}</h4>
                  <p className="text-slate-400 text-[11px] line-clamp-1 mt-0.5">{f.description}</p>
                  <div className="mt-1.5 text-[10px] text-slate-500 font-mono truncate">{f.equation_or_def}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Calculator & Mathematical Verification */}
          <div className="lg:col-span-7 space-y-4">
            {selectedFormula && (
              <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-cyan-400 font-bold uppercase">{selectedFormula.domain}</span>
                    <span className="text-xs text-slate-500 font-mono">ID: {selectedFormula.unique_id}</span>
                  </div>
                  <h2 className="text-lg font-bold text-white mt-1">{selectedFormula.name}</h2>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">{selectedFormula.description}</p>
                  <div className="mt-2.5 p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs font-mono text-cyan-300">
                    Equation: {selectedFormula.equation_or_def}
                  </div>
                </div>

                {/* Input Fields */}
                <div className="space-y-3 pt-2 border-t border-slate-800">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Inputs</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {selectedFormula.required_inputs.map(inp => (
                      <div key={inp.name} className="space-y-1">
                        <label className="text-[11px] font-semibold text-slate-300 flex items-center justify-between">
                          <span>{inp.name} ({inp.unit})</span>
                          <span className="text-[10px] text-rose-400">*required</span>
                        </label>
                        <input
                          type={inp.type === 'int' || inp.type === 'Decimal' || inp.type === 'float' ? 'number' : 'text'}
                          value={calcInputs[inp.name] !== undefined ? calcInputs[inp.name] : ''}
                          onChange={(e) => setCalcInputs({ ...calcInputs, [inp.name]: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                        />
                        <span className="text-[10px] text-slate-500 block">{inp.description}</span>
                      </div>
                    ))}
                    {selectedFormula.optional_inputs.map(inp => (
                      <div key={inp.name} className="space-y-1">
                        <label className="text-[11px] font-semibold text-slate-300 flex items-center justify-between">
                          <span>{inp.name} ({inp.unit})</span>
                          <span className="text-[10px] text-slate-500">optional</span>
                        </label>
                        <input
                          type={inp.type === 'int' || inp.type === 'Decimal' || inp.type === 'float' ? 'number' : 'text'}
                          value={calcInputs[inp.name] !== undefined ? calcInputs[inp.name] : (inp.default || '')}
                          onChange={(e) => setCalcInputs({ ...calcInputs, [inp.name]: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                        />
                      </div>
                    ))}
                  </div>

                  <button
                    onClick={handleRunCalculation}
                    disabled={calcLoading || selectedFormula.status !== 'EXECUTABLE_TESTED'}
                    className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                      selectedFormula.status === 'EXECUTABLE_TESTED'
                        ? 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-950/50'
                        : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    }`}
                  >
                    <Calculator className="w-4 h-4" />
                    <span>{calcLoading ? 'Calculating with Decimal Precision...' : 'Execute Calculation'}</span>
                  </button>
                </div>

                {/* Calculation Output Result Card */}
                {calcResult && (
                  <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/40 space-y-2.5 animate-fadeIn">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Calculation Output</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                        EXACT DECIMAL
                      </span>
                    </div>
                    <div className="text-xl font-bold text-white">{calcResult.result_formatted}</div>
                    <p className="text-xs text-slate-300 leading-relaxed">{calcResult.explanation}</p>
                    {calcResult.assumptions.length > 0 && (
                      <div className="text-[11px] text-slate-500 space-y-0.5">
                        <strong className="text-slate-400 block font-semibold">Assumptions:</strong>
                        {calcResult.assumptions.map((asm, i) => (
                          <div key={i}>• {asm}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 4: DECISION COMPOSITION STUDIO */}
      {/* ========================================================================= */}
      {activeSubTab === 'composition' && (
        <div className="space-y-6">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <GitMerge className="w-4 h-4 text-cyan-400" />
                <span>Purchase Affordability & Multi-Formula Decision Recipe</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Combines available liquid cash, essential expenses, 3-month survival buffer, and 10-year opportunity cost to make an authoritative verdict.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-2">
              <div>
                <label className="text-[11px] text-slate-400 font-semibold block mb-1">Item Name</label>
                <input
                  type="text"
                  value={purchaseForm.item_name}
                  onChange={(e) => setPurchaseForm({ ...purchaseForm, item_name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 font-semibold block mb-1">Price ($)</label>
                <input
                  type="number"
                  value={purchaseForm.price}
                  onChange={(e) => setPurchaseForm({ ...purchaseForm, price: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 font-semibold block mb-1">Available Liquid Cash ($)</label>
                <input
                  type="number"
                  value={purchaseForm.available_liquid_cash}
                  onChange={(e) => setPurchaseForm({ ...purchaseForm, available_liquid_cash: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
                />
              </div>
              <div>
                <label className="text-[11px] text-slate-400 font-semibold block mb-1">Essential Living Exp ($/mo)</label>
                <input
                  type="number"
                  value={purchaseForm.essential_expenses}
                  onChange={(e) => setPurchaseForm({ ...purchaseForm, essential_expenses: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white"
                />
              </div>
            </div>

            <button
              onClick={handleRunPurchaseDecision}
              disabled={compLoading}
              className="py-2.5 px-6 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-xs font-bold text-white transition-all shadow-md shadow-cyan-950/40"
            >
              {compLoading ? 'Evaluating Decision Graph...' : 'Evaluate Decision Graph'}
            </button>

            {compositionResult && (
              <div className="p-4 rounded-xl bg-slate-950 border border-cyan-500/40 space-y-3 mt-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-cyan-400 uppercase">Composite Workflow Result</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    compositionResult.decision_verdict === 'AFFORDABLE' ? 'bg-emerald-500/20 text-emerald-300' :
                    compositionResult.decision_verdict === 'AFFORDABLE_WITH_CAUTION' ? 'bg-amber-500/20 text-amber-300' :
                    'bg-rose-500/20 text-rose-300'
                  }`}>
                    {compositionResult.decision_verdict}
                  </span>
                </div>
                <p className="text-xs text-white font-medium leading-relaxed">{compositionResult.summary_explanation}</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-xs">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Total Checkout</span>
                    <strong className="text-white">${compositionResult.step_results.total_checkout_price?.toFixed(2)}</strong>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Post-Purchase Cash</span>
                    <strong className="text-emerald-400">${compositionResult.step_results.liquid_cash_after?.toFixed(2)}</strong>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">3-Mo Emergency Floor</span>
                    <strong className="text-amber-400">${compositionResult.step_results.emergency_reserve_floor?.toFixed(2)}</strong>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">10-Yr Opportunity Cost</span>
                    <strong className="text-cyan-400">${compositionResult.step_results.ten_year_opportunity_cost?.toFixed(2)}</strong>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 5: RANKED FINANCIAL OPTIMIZATION OPPORTUNITIES */}
      {/* ========================================================================= */}
      {activeSubTab === 'optimization' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
            FINORA continuously scans your subscriptions, cash accounts, and spending patterns to rank verified optimization opportunities by net financial impact and break-even duration.
          </div>

          <div className="space-y-3">
            {opportunities.map((opp, idx) => (
              <div
                key={opp.opportunity_id}
                className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
                      Rank #{idx + 1} • {opp.category}
                    </span>
                    <span className="text-[10px] text-slate-400">Evidence: {opp.evidence_quality}</span>
                  </div>
                  <h3 className="text-sm font-bold text-white">{opp.title}</h3>
                  <p className="text-xs text-slate-400 max-w-2xl">{opp.recommendation_summary}</p>
                </div>

                <div className="flex items-center gap-6 flex-shrink-0 text-right">
                  <div>
                    <div className="text-[10px] text-slate-500 uppercase font-semibold">1st-Year Net Savings</div>
                    <div className="text-base font-bold text-emerald-400">+${opp.first_year_net_savings.toFixed(2)}/yr</div>
                  </div>
                  {opp.break_even_months > 0 && (
                    <div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Break-Even</div>
                      <div className="text-xs font-semibold text-slate-300">{opp.break_even_months.toFixed(1)} mo</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
