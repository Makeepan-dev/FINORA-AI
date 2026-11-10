import React, { useState, useEffect } from 'react';
import {
  CreditCard,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Lock,
  ArrowRight,
  ExternalLink,
  Loader2,
  Receipt,
  Wifi,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { ProductItem } from '../types';

interface PaymentsProps {
  selectedProduct: ProductItem | null;
  activeUserId: string;
  onClearSelectedProduct: () => void;
}

export const Payments: React.FC<PaymentsProps> = ({
  selectedProduct,
  activeUserId,
  onClearSelectedProduct
}) => {
  const [loading, setLoading] = useState(false);
  const [createdOrder, setCreatedOrder] = useState<any | null>(null);
  const [captureResult, setCaptureResult] = useState<any | null>(null);
  const [paymentHistory, setPaymentHistory] = useState<any[]>([]);
  const [configStatus, setConfigStatus] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [connectionTestResult, setConnectionTestResult] = useState<any | null>(null);
  const [testingConnection, setTestingConnection] = useState(false);

  useEffect(() => {
    loadPaymentHistory();
    loadConfigStatus();
  }, []);

  const loadPaymentHistory = async () => {
    try {
      const history = await api.getPaymentHistory();
      setPaymentHistory(history);
    } catch (err) {
      console.error(err);
    }
  };

  const loadConfigStatus = async () => {
    try {
      const status = await api.getPaymentConfigStatus();
      setConfigStatus(status);
    } catch (err) {
      console.error(err);
    }
  };

  const handleTestConnection = async () => {
    setTestingConnection(true);
    setConnectionTestResult(null);
    try {
      const res = await api.testPayPalConnection();
      setConnectionTestResult(res);
    } catch (err: any) {
      setConnectionTestResult({
        configured: false,
        authenticated: false,
        message: err.message
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleCreateOrder = async () => {
    if (!selectedProduct) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const order = await api.createPayPalOrder(selectedProduct.product_id, activeUserId);
      setCreatedOrder(order);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to prepare order');
    } finally {
      setLoading(false);
    }
  };

  const handleCaptureOrder = async () => {
    if (!createdOrder) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const capture = await api.capturePayPalOrder(createdOrder.id);
      setCaptureResult(capture);
      loadPaymentHistory();
    } catch (err: any) {
      setErrorMsg(err.message || 'Capture failed');
    } finally {
      setLoading(false);
    }
  };

  const approvalUrl = createdOrder?.links?.find((l: any) => l.rel === 'approve')?.href;

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header with Prominent Sandbox Mode Indicator */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/30 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <CreditCard className="w-6 h-6 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">PayPal Sandbox Checkout Network</h1>
              {configStatus?.is_live_sandbox_configured ? (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  Live PayPal Sandbox Mode
                </span>
              ) : (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
                  Simulated Sandbox Mode (Offline Safe)
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Official PayPal REST APIs v2 • Server-calculated amounts • Idempotent anti-duplicate capture
            </p>
          </div>
        </div>

        <button
          onClick={handleTestConnection}
          disabled={testingConnection}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
        >
          {testingConnection ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Wifi className="w-3.5 h-3.5 text-cyan-400" />}
          <span>Test Live Sandbox Link</span>
        </button>
      </div>

      {/* Live Handshake Diagnostic Result Banner */}
      {connectionTestResult && (
        <div className={`p-4 rounded-xl border text-xs space-y-1.5 ${
          connectionTestResult.authenticated
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
            : 'bg-slate-900 border-slate-800 text-slate-300'
        }`}>
          <div className="flex items-center justify-between font-bold">
            <span className="flex items-center gap-2">
              {connectionTestResult.authenticated ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-amber-400" />
              )}
              <span>Live Endpoint Audit: {connectionTestResult.authenticated ? "Verified Connected" : "Unverified (Keys Needed in .env)"}</span>
            </span>
            <button onClick={() => setConnectionTestResult(null)} className="text-slate-500 hover:text-white">✕</button>
          </div>
          <p className="text-[11px] leading-relaxed pl-6">
            {connectionTestResult.message}
          </p>
          <div className="text-[10px] font-mono text-slate-500 pl-6">
            Endpoint: {connectionTestResult.api_base} • Mode: {connectionTestResult.mode}
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2 font-medium">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Main Checkout Experience Card */}
      {selectedProduct ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Order Summary & Backend Calculation */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-white text-base">Payment Review & Authorization</h3>
              <button
                onClick={onClearSelectedProduct}
                className="text-xs text-slate-400 hover:text-white"
              >
                Change Item
              </button>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-white text-sm">{selectedProduct.product_name}</h4>
                    <span className="text-xs text-slate-400 capitalize">{selectedProduct.category} • Merchant: {selectedProduct.merchant_id}</span>
                  </div>
                  <span className="text-lg font-black text-white">${selectedProduct.price.toFixed(2)}</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed pt-1">{selectedProduct.description}</p>
              </div>

              {/* Server-Side Calculated Financial Breakdown */}
              <div className="space-y-2 text-xs pt-2">
                <div className="flex justify-between text-slate-400">
                  <span>Authoritative Base Price:</span>
                  <span className="text-white font-medium">${selectedProduct.price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Shipping & Landed Fulfillment:</span>
                  <span className="text-white font-medium">${selectedProduct.shipping_cost.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Estimated Tax:</span>
                  <span className="text-white font-medium">$0.00</span>
                </div>
                <div className="pt-2 border-t border-slate-800 flex justify-between items-baseline text-sm">
                  <span className="font-bold text-slate-200">Total Authorized Amount:</span>
                  <span className="font-black text-xl text-cyan-400">${selectedProduct.total_cost.toFixed(2)} USD</span>
                </div>
              </div>

              {/* Policy Check */}
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs flex items-center gap-3">
                <Lock className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <div className="leading-snug">
                  <span className="font-semibold text-slate-200">Autonomous Security Rule: </span>
                  <span className="text-slate-400">
                    Order total must not exceed $250.00 preset policy without explicit user review confirmation.
                  </span>
                </div>
              </div>
            </div>

            {/* Workflow Step Actions */}
            <div className="pt-4 space-y-3">
              {!createdOrder && (
                <button
                  onClick={handleCreateOrder}
                  disabled={loading}
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:opacity-95 text-slate-950 font-extrabold text-sm shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
                  <span>Step 1: Create Authorized PayPal Order</span>
                </button>
              )}

              {createdOrder && !captureResult && (
                <div className="space-y-4 p-5 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">PayPal Order ID:</span>
                    <span className="font-mono text-cyan-400 font-bold">{createdOrder.id}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Execution Mode:</span>
                    <span className="font-bold uppercase text-slate-200">{createdOrder.source}</span>
                  </div>

                  {approvalUrl && (
                    <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                      <span className="text-slate-400">Approval Redirect Link:</span>
                      <a
                        href={approvalUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 font-mono text-[11px]"
                      >
                        Launch Sandbox Flow <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  )}

                  <p className="text-[11px] text-slate-300 leading-relaxed">
                    Order is staged on the server. Click below to approve and execute order capture through the PayPal Sandbox gateway.
                  </p>

                  <button
                    onClick={handleCaptureOrder}
                    disabled={loading}
                    className="w-full py-3.5 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-black text-sm shadow-md transition-all flex items-center justify-center gap-2"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                    <span>Step 2: Approve & Capture Payment (${selectedProduct.total_cost.toFixed(2)})</span>
                  </button>
                </div>
              )}

              {/* Verified Capture Success Card */}
              {captureResult && (
                <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 space-y-3">
                  <div className="flex items-center gap-2 text-white font-bold text-base">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    <span>PayPal Sandbox Payment Captured & Verified!</span>
                  </div>
                  <div className="space-y-1.5 text-xs text-slate-300">
                    <div className="flex justify-between">
                      <span>Capture ID:</span>
                      <span className="font-mono text-emerald-400 font-bold">{captureResult.capture_id || captureResult.id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Execution Mode:</span>
                      <span className="font-bold uppercase text-emerald-400">{captureResult.source}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Status:</span>
                      <span className="font-bold text-emerald-400 uppercase">{captureResult.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Timestamp:</span>
                      <span>{captureResult.verified_sandbox_timestamp || new Date().toISOString()}</span>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-400 pt-1 border-t border-emerald-500/20">
                    Payment verified and permanently persisted to database ledger.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Side Info & Guardrails */}
          <div className="space-y-4">
            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 text-xs">
              <h4 className="font-bold text-white text-sm">Security Guardrails</h4>
              <ul className="space-y-2 text-slate-400">
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>No client-submitted prices are ever trusted by the API.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Idempotency checks prevent duplicate PayPal captures.</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <span>Autonomous AI agents cannot execute transactions without explicit human review.</span>
                </li>
              </ul>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 text-xs">
              <h4 className="font-bold text-white text-sm">PayPal Sandbox Credentials</h4>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Add your personal credentials to <code className="text-cyan-400">backend/.env</code> to test genuine Sandbox handshakes:
              </p>
              <pre className="p-2.5 rounded bg-slate-950 font-mono text-[10px] text-slate-300 overflow-x-auto">
PAYPAL_CLIENT_ID=your_id{'\n'}PAYPAL_CLIENT_SECRET=your_sec
              </pre>
            </div>
          </div>
        </div>
      ) : (
        /* Empty State */
        <div className="p-12 text-center rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
          <div className="h-16 w-16 rounded-full bg-slate-800/80 flex items-center justify-center mx-auto text-cyan-400">
            <CreditCard className="w-8 h-8" />
          </div>
          <div>
            <h3 className="font-bold text-white text-lg">No Item Staged for Checkout</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
              Select a product in the Shopping Agent to evaluate budget fit and initiate a PayPal Sandbox checkout session.
            </p>
          </div>
        </div>
      )}

      {/* Captured Payments History Ledger */}
      <div className="space-y-3 pt-6">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <Receipt className="w-4 h-4 text-cyan-400" />
            <span>Captured Payments Ledger ({paymentHistory.length})</span>
          </h3>
          <span className="text-xs text-slate-400">Database Persisted Sessions</span>
        </div>

        {paymentHistory.length === 0 ? (
          <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-500">
            No payments captured in this session yet. Complete checkout above to generate the first verified capture.
          </div>
        ) : (
          <div className="overflow-hidden rounded-xl bg-slate-900/70 border border-slate-800">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-4">Order ID</th>
                  <th className="py-2.5 px-4">Capture ID</th>
                  <th className="py-2.5 px-4 text-right">Amount</th>
                  <th className="py-2.5 px-4">Execution Source</th>
                  <th className="py-2.5 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {paymentHistory.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-mono text-cyan-400">{item.id}</td>
                    <td className="py-3 px-4 font-mono text-slate-300">{item.capture_id || 'COMPLETED'}</td>
                    <td className="py-3 px-4 text-right font-bold text-white">
                      ${Number(item.amount || 119.0).toFixed(2)}
                    </td>
                    <td className="py-3 px-4">
                      {item.is_simulated || item.source?.includes('simulated') ? (
                        <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[10px] font-mono">
                          Simulated Sandbox
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono">
                          Live Sandbox API
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">
                        {item.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
