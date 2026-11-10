import React, { useState, useEffect } from 'react';
import {
  Search, Filter, Shield, Upload, Plus, CheckCircle2, AlertTriangle,
  Trash2, FileSpreadsheet, DollarSign, TrendingUp, TrendingDown, Wallet
} from 'lucide-react';
import { TransactionItem } from '../types';
import { api } from '../services/api';

interface TransactionsProps {
  transactions: TransactionItem[];
  activeUserId?: string;
  onDataUpdated?: () => void;
}

const SAMPLE_CSV_TEXT = `date,merchant,description,amount,type,category
2026-10-28,Trader Joe's,Weekly Grocery Basket,64.80,expense,groceries
2026-10-28,DoorDash,Late Night Thai Delivery,42.50,expense,food_dining
2026-10-29,Internal Transfer,Transfer to High-Yield Savings,400.00,transfer,transfers
2026-10-30,Stripe Client Payout,Freelance UI Consulting Milestone,550.00,income,salary_income`;

export const Transactions: React.FC<TransactionsProps> = ({
  transactions: initialTransactions,
  activeUserId = 'usr_alex_chen',
  onDataUpdated
}) => {
  const [persistedTxs, setPersistedTxs] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [dataScope, setDataScope] = useState<string>('auto');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedTx, setSelectedTx] = useState<any | null>(null);

  // CSV Import Modal State
  const [showCsvModal, setShowCsvModal] = useState(false);
  const [csvText, setCsvText] = useState(SAMPLE_CSV_TEXT);
  const [csvPreview, setCsvPreview] = useState<any | null>(null);
  const [importStatus, setImportStatus] = useState<string | null>(null);

  // Manual Entry Modal State
  const [showManualModal, setShowManualModal] = useState(false);
  const [manualMerchant, setManualMerchant] = useState('');
  const [manualDesc, setManualDesc] = useState('');
  const [manualAmount, setManualAmount] = useState('');
  const [manualType, setManualType] = useState('expense');
  const [manualCategory, setManualCategory] = useState('food_dining');

  const loadPersistedData = async (scope: string = dataScope) => {
    try {
      const [txRes, sumRes] = await Promise.all([
        api.getPersistedTransactions(activeUserId, undefined, undefined, scope),
        api.getFinancialSummary(activeUserId, undefined, scope)
      ]);
      setPersistedTxs(txRes.transactions || []);
      setSummary(sumRes);
    } catch (err) {
      console.error('Error loading persisted transactions:', err);
    }
  };

  useEffect(() => {
    loadPersistedData(dataScope);
  }, [activeUserId, dataScope]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      if (typeof ev.target?.result === 'string') {
        setCsvText(ev.target.result);
      }
    };
    reader.readAsText(file);
  };

  const handlePreviewCsv = async () => {
    setImportStatus(null);
    try {
      const prev = await api.previewCsvImport(activeUserId, csvText);
      setCsvPreview(prev);
    } catch (err: any) {
      setImportStatus(`Preview error: ${err.message}`);
    }
  };

  const handleConfirmCsv = async () => {
    if (!csvPreview?.records) return;
    try {
      const res = await api.confirmCsvImport(activeUserId, csvPreview.records, true);
      setImportStatus(`Imported ${res.imported_count} valid transactions (${res.skipped_count} duplicates/invalid skipped).`);
      setCsvPreview(null);
      await loadPersistedData();
      if (onDataUpdated) onDataUpdated();
    } catch (err: any) {
      setImportStatus(`Import error: ${err.message}`);
    }
  };

  const handleAddManual = async (e: React.FormEvent) => {
    e.preventDefault();
    const amt = parseFloat(manualAmount);
    if (!manualMerchant || isNaN(amt) || amt <= 0) return;
    try {
      await api.addManualTransaction(activeUserId, {
        merchant: manualMerchant,
        description: manualDesc || manualMerchant,
        amount: amt,
        transaction_type: manualType,
        category: manualCategory
      });
      setManualMerchant('');
      setManualDesc('');
      setManualAmount('');
      setShowManualModal(false);
      await loadPersistedData();
      if (onDataUpdated) onDataUpdated();
    } catch (err) {
      console.error('Failed to add manual transaction:', err);
    }
  };

  const handleDeleteTx = async (txId: string) => {
    try {
      await api.deleteTransaction(activeUserId, txId);
      await loadPersistedData();
      if (onDataUpdated) onDataUpdated();
    } catch (err) {
      console.error('Failed to delete transaction:', err);
    }
  };

  const displayList = persistedTxs.length > 0 ? persistedTxs : initialTransactions.map(t => ({
    id: t.transaction_id,
    date: t.timestamp.substring(0, 10),
    merchant: t.merchant_id,
    description: t.description,
    amount: t.amount,
    currency: t.currency,
    transaction_type: t.type,
    category: t.category,
    source: t.payment_method,
    is_demo: true
  }));

  const filtered = displayList.filter((tx) => {
    const matchesSearch =
      (tx.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tx.merchant || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tx.id || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat =
      selectedCategory === 'all' ||
      (tx.category || '').toLowerCase().replace('_', ' ') === selectedCategory.toLowerCase().replace('_', ' ');
    return matchesSearch && matchesCat;
  });

  const categories = ['all', ...Array.from(new Set(displayList.map(t => (t.category || 'general').toLowerCase())))];

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Primary Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Smart Personal Finance Tracker</h1>
          <p className="text-sm text-slate-400 mt-1">
            SQLite-persisted transaction ledger with CSV import, deduplication & Decimal precision
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-xl p-1 text-xs">
            {[
              { id: 'auto', label: 'Auto (Isolated)' },
              { id: 'personal', label: 'Personal Only' },
              { id: 'demo', label: 'Demo Only' }
            ].map((sc) => (
              <button
                key={sc.id}
                onClick={() => setDataScope(sc.id)}
                className={`px-2.5 py-1 rounded-lg font-semibold transition-all ${
                  dataScope === sc.id ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'
                }`}
              >
                {sc.label}
              </button>
            ))}
          </div>
          <button
            onClick={() => { setShowCsvModal(true); handlePreviewCsv(); }}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-lg shadow-cyan-500/20"
          >
            <Upload className="w-4 h-4" />
            Import CSV Transactions
          </button>
          <button
            onClick={() => setShowManualModal(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 font-semibold text-xs transition-all"
          >
            <Plus className="w-4 h-4 text-emerald-400" />
            Add Manual Entry
          </button>
        </div>
      </div>

      {/* Authoritative Summary Bar */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Monthly Income ({summary.month})</span>
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-xl font-bold text-emerald-400 mt-1">${summary.total_income.toFixed(2)}</p>
            <span className="text-[11px] text-slate-500">Verified deposits & payouts</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Monthly Expenses</span>
              <TrendingDown className="w-4 h-4 text-rose-400" />
            </div>
            <p className="text-xl font-bold text-white mt-1">${summary.total_expenses.toFixed(2)}</p>
            <span className="text-[11px] text-slate-500">Transfers strictly excluded</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-cyan-500/30">
            <div className="flex items-center justify-between text-xs text-cyan-300">
              <span>Remaining Available Money</span>
              <Wallet className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-xl font-bold text-cyan-400 mt-1">${summary.remaining_available_money.toFixed(2)}</p>
            <span className="text-[10px] text-slate-400">Income − Expenses (Decimal Verified)</span>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-emerald-500/30">
            <div className="flex items-center justify-between text-xs text-emerald-300">
              <span>Potential Monthly Savings</span>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-xl font-bold text-emerald-400 mt-1">+${summary.potential_monthly_savings.toFixed(2)}/mo</p>
            <span className="text-[10px] text-slate-400">${summary.potential_annual_savings.toFixed(2)}/yr estimated</span>
          </div>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/50 p-3 rounded-xl border border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search merchant, description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 w-64"
            />
          </div>

          <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs">
            <Filter className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer capitalize"
            >
              {categories.map((c) => (
                <option key={c} value={c} className="bg-slate-900 text-white capitalize">
                  {c.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="text-[11px] text-slate-400 flex items-center gap-3">
          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold">
            Real Imported / Manual
          </span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            Demo Seed Labelled
          </span>
        </div>
      </div>

      {/* Ledger Table */}
      <div className="overflow-hidden rounded-2xl bg-slate-900/70 border border-slate-800/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Merchant & Description</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Provenance</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4 text-center">Type</th>
                <th className="py-3 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {filtered.map((tx) => {
                const isIncome = tx.transaction_type === 'income' || tx.transaction_type === 'refund';
                const isTransfer = tx.transaction_type === 'transfer';
                return (
                  <tr
                    key={tx.id}
                    className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                    onClick={() => setSelectedTx(tx)}
                  >
                    <td className="py-3.5 px-4 text-slate-400 whitespace-nowrap font-mono">
                      {tx.date}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-white">{tx.merchant}</div>
                      <div className="text-[11px] text-slate-400">{tx.description}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-1 rounded-md bg-slate-800 text-slate-300 text-[11px] capitalize">
                        {(tx.category || '').replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {tx.is_demo ? (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 border border-slate-700">
                          Demo Mode Data
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold uppercase">
                          {tx.source || 'User Persisted'}
                        </span>
                      )}
                    </td>
                    <td className={`py-3.5 px-4 text-right font-bold ${
                      isTransfer ? 'text-amber-400' : isIncome ? 'text-emerald-400' : 'text-slate-200'
                    }`}>
                      {isTransfer ? '⇄ ' : isIncome ? '+' : '-'}${Number(tx.amount).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        isTransfer
                          ? 'bg-amber-500/10 text-amber-400'
                          : isIncome
                          ? 'bg-emerald-500/10 text-emerald-400'
                          : 'bg-slate-800 text-slate-300'
                      }`}>
                        {tx.transaction_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDeleteTx(tx.id); }}
                          className="p-1.5 rounded bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                          title="Delete record"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* CSV Import Modal */}
      {showCsvModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-3xl rounded-2xl bg-slate-900 border border-slate-700 p-6 space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-white text-base">Import & Validate CSV Transactions</h3>
              </div>
              <button onClick={() => setShowCsvModal(false)} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300">Upload CSV File or Edit CSV Content Below:</label>
                <input
                  type="file"
                  accept=".csv,text/csv"
                  onChange={handleFileUpload}
                  className="text-xs text-slate-400 file:mr-3 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-cyan-400 hover:file:bg-slate-700"
                />
              </div>

              <textarea
                rows={5}
                value={csvText}
                onChange={(e) => setCsvText(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500/50"
              />

              <div className="flex items-center gap-3">
                <button
                  onClick={handlePreviewCsv}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 font-semibold text-xs border border-cyan-500/30"
                >
                  1. Preview & Validate Records
                </button>
                {csvPreview && csvPreview.valid_count > 0 && (
                  <button
                    onClick={handleConfirmCsv}
                    className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs"
                  >
                    2. Confirm Import ({csvPreview.valid_count} Valid Rows)
                  </button>
                )}
              </div>

              {importStatus && (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium">
                  {importStatus}
                </div>
              )}

              {csvPreview && (
                <div className="space-y-2 pt-2">
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-emerald-400 font-semibold">✓ Valid: {csvPreview.valid_count}</span>
                    <span className="text-amber-400 font-semibold">⚠ Duplicates Flagged: {csvPreview.duplicate_count}</span>
                    <span className="text-rose-400 font-semibold">✕ Invalid Rejected: {csvPreview.invalid_count}</span>
                  </div>
                  <div className="max-h-52 overflow-y-auto rounded-xl border border-slate-800">
                    <table className="w-full text-left text-[11px]">
                      <thead className="bg-slate-950 text-slate-400">
                        <tr>
                          <th className="p-2">Row</th>
                          <th className="p-2">Date</th>
                          <th className="p-2">Merchant</th>
                          <th className="p-2">Amount</th>
                          <th className="p-2">Category / Type</th>
                          <th className="p-2">Validation Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {csvPreview.records.map((r: any, idx: number) => (
                          <tr key={idx} className="bg-slate-900/60">
                            <td className="p-2 text-slate-500">#{r.row_number}</td>
                            <td className="p-2 text-slate-300">{r.date}</td>
                            <td className="p-2 text-white font-medium">{r.merchant}</td>
                            <td className="p-2 text-slate-200">${Number(r.amount).toFixed(2)}</td>
                            <td className="p-2 text-slate-400">{r.category} ({r.transaction_type})</td>
                            <td className="p-2">
                              {!r.is_valid ? (
                                <span className="text-rose-400 font-semibold">
                                  Invalid: {r.validation_errors.join(', ')}
                                </span>
                              ) : r.is_duplicate ? (
                                <span className="text-amber-400 font-semibold">Duplicate (Will Skip)</span>
                              ) : (
                                <span className="text-emerald-400 font-semibold">Ready to Import</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Manual Transaction Modal */}
      {showManualModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <form
            onSubmit={handleAddManual}
            className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-700 p-6 space-y-4 shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-base">Log Manual Transaction</h3>
              <button type="button" onClick={() => setShowManualModal(false)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Merchant / Payee *</label>
                <input
                  type="text"
                  required
                  value={manualMerchant}
                  onChange={(e) => setManualMerchant(e.target.value)}
                  placeholder="e.g., Trader Joe's, Shell Fuel..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Description</label>
                <input
                  type="text"
                  value={manualDesc}
                  onChange={(e) => setManualDesc(e.target.value)}
                  placeholder="Weekly groceries..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1">Amount (USD) *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    required
                    value={manualAmount}
                    onChange={(e) => setManualAmount(e.target.value)}
                    placeholder="45.00"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Type</label>
                  <select
                    value={manualType}
                    onChange={(e) => setManualType(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                  >
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                    <option value="transfer">Transfer (Excluded from Expense)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Category</label>
                <select
                  value={manualCategory}
                  onChange={(e) => setManualCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white"
                >
                  <option value="groceries">Groceries</option>
                  <option value="food_dining">Food & Dining</option>
                  <option value="fitness_wellness">Fitness & Wellness</option>
                  <option value="tech_subscriptions">Tech Subscriptions</option>
                  <option value="transportation">Transportation & Fuel</option>
                  <option value="utilities_housing">Utilities & Housing</option>
                  <option value="shopping">Shopping</option>
                  <option value="salary_income">Salary / Income</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowManualModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs"
              >
                Save Transaction
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
