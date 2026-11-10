import React, { useState, useEffect } from 'react';
import {
  Link2,
  ShieldCheck,
  RefreshCw,
  Trash2,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Lock,
  Loader2,
  ExternalLink,
  History
} from 'lucide-react';
import { api } from '../services/api';
import { ConnectedAccountItem, InstitutionItem } from '../types';

interface ConnectionsProps {
  activeUserId: string;
}

export const Connections: React.FC<ConnectionsProps> = ({ activeUserId }) => {
  const [connections, setConnections] = useState<ConnectedAccountItem[]>([]);
  const [institutions, setInstitutions] = useState<InstitutionItem[]>([]);
  const [syncHistory, setSyncHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingId, setSyncingId] = useState<string | null>(null);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    loadConnectionsData();
  }, [activeUserId]);

  const loadConnectionsData = async () => {
    setLoading(true);
    try {
      const [conns, insts, history] = await Promise.all([
        api.getConnectedAccounts(activeUserId),
        api.getSupportedInstitutions(),
        api.getSyncHistory(activeUserId)
      ]);
      setConnections(conns);
      setInstitutions(insts);
      setSyncHistory(history);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async (connId: string) => {
    setSyncingId(connId);
    setStatusMessage(null);
    try {
      const res = await api.syncConnection(connId);
      setStatusMessage(`Synchronization complete: ${res.records_synchronized} records updated, ${res.income_streams_detected} income streams analyzed.`);
      await loadConnectionsData();
    } catch (err: any) {
      setStatusMessage(`Sync error: ${err.message}`);
    } finally {
      setSyncingId(null);
    }
  };

  const handleRevoke = async (connId: string) => {
    if (!confirm("Revoke OAuth permissions? FINORA will immediately cease pulling financial records from this account.")) return;
    try {
      await api.revokeConnection(connId);
      setStatusMessage("Account connection revoked successfully.");
      await loadConnectionsData();
    } catch (err: any) {
      setStatusMessage(`Revocation error: ${err.message}`);
    }
  };

  const handleConnectInstitution = async (instId: string) => {
    setShowConnectModal(false);
    setLoading(true);
    try {
      const res = await api.connectAccount(instId, "checking", activeUserId);
      setStatusMessage(`Successfully linked ${res.institution} (${res.mask}). Initial sync completed.`);
      await loadConnectionsData();
    } catch (err: any) {
      setStatusMessage(`Connection failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/30 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Connected Financial Accounts</h1>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Zero-Manual-Entry Sync
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Automatic streaming of transactions, income streams, and balance snapshots via authorized Open Banking & PayPal APIs
          </p>
        </div>

        <button
          onClick={() => setShowConnectModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Connect Financial Institution</span>
        </button>
      </div>

      {statusMessage && (
        <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs flex items-center justify-between">
          <span>{statusMessage}</span>
          <button onClick={() => setStatusMessage(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Security Guarantee Notice */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-start gap-3 text-xs text-slate-300">
        <Lock className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-bold text-white">OAuth Security & Zero Raw Passwords: </span>
          <span>
            FINORA never requests or stores raw banking passwords. All financial data flows through secure read-only token grants authorized by you. You may revoke access at any time.
          </span>
        </div>
      </div>

      {/* Connected Accounts List */}
      <div className="space-y-4">
        <h3 className="font-bold text-white text-base">Active Financial Links ({connections.length})</h3>

        {connections.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-slate-900/40 border border-slate-800 text-slate-400 text-xs">
            No accounts currently connected. Click "Connect Financial Institution" above to link an account.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {connections.map((conn) => {
              const isSyncing = syncingId === conn.id;
              const isRevoked = conn.connection_status === 'revoked';
              return (
                <div
                  key={conn.id}
                  className={`p-5 rounded-2xl border space-y-4 transition-all ${
                    isRevoked
                      ? 'bg-slate-950/60 border-slate-800 opacity-60'
                      : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 shadow-md'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center text-cyan-400">
                        <Link2 className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white text-sm leading-snug">{conn.institution_name}</h4>
                        <span className="text-[11px] font-mono text-slate-400">{conn.account_mask} • {conn.account_type}</span>
                      </div>
                    </div>

                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded capitalize ${
                      isRevoked
                        ? 'bg-slate-800 text-slate-500'
                        : conn.health_status === 'healthy'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {conn.connection_status}
                    </span>
                  </div>

                  {/* Metadata & Freshness */}
                  <div className="space-y-1.5 text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                    <div className="flex justify-between">
                      <span>Provider Gateway:</span>
                      <span className="font-mono text-slate-300 capitalize">{conn.provider_type.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Data Freshness:</span>
                      <span className="text-slate-300 font-medium">{conn.last_sync}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Sync Mode:</span>
                      <span className="text-cyan-400 font-medium capitalize">{conn.sync_frequency} auto-sync</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
                    {!isRevoked ? (
                      <>
                        <button
                          onClick={() => handleSync(conn.id)}
                          disabled={isSyncing}
                          className="flex-1 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                        >
                          {isSyncing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                          <span>Sync Now</span>
                        </button>

                        <button
                          onClick={() => handleRevoke(conn.id)}
                          className="py-2 px-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold flex items-center gap-1 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          <span>Revoke</span>
                        </button>
                      </>
                    ) : (
                      <span className="text-xs text-slate-500 italic">Permissions revoked. Re-connect below if needed.</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Sync Audit History */}
      <div className="space-y-3 pt-6">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-white text-base flex items-center gap-2">
            <History className="w-4 h-4 text-cyan-400" />
            <span>Automatic Synchronization Audit Log</span>
          </h3>
          <span className="text-xs text-slate-400">Recent API ingestion cycles</span>
        </div>

        <div className="overflow-hidden rounded-xl bg-slate-900/70 border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4">Connection</th>
                <th className="py-2.5 px-4 text-center">Records Ingested</th>
                <th className="py-2.5 px-4 text-center">Income Detected</th>
                <th className="py-2.5 px-4 text-center">Duration</th>
                <th className="py-2.5 px-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {syncHistory.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30">
                  <td className="py-3 px-4 text-slate-400">{log.timestamp || 'Just now'}</td>
                  <td className="py-3 px-4 font-mono text-cyan-400">{log.connection_id}</td>
                  <td className="py-3 px-4 text-center text-white">{log.records_ingested}</td>
                  <td className="py-3 px-4 text-center text-emerald-400 font-semibold">{log.income_detected}</td>
                  <td className="py-3 px-4 text-center text-slate-400">{log.duration_ms} ms</td>
                  <td className="py-3 px-4 text-right">
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase">
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Connect Modal */}
      {showConnectModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-slate-700 p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <Link2 className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-white text-base">Select Financial Institution</h3>
              </div>
              <button onClick={() => setShowConnectModal(false)} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Choose an institution to launch the secure OAuth 2.0 connection. No banking passwords are ever stored by FINORA.
            </p>

            <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
              {institutions.map((inst) => (
                <div
                  key={inst.id}
                  onClick={() => handleConnectInstitution(inst.id)}
                  className="p-3.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-cyan-500/50 cursor-pointer transition-all flex items-center justify-between"
                >
                  <div>
                    <h4 className="font-bold text-white text-xs">{inst.name}</h4>
                    <p className="text-[11px] text-slate-400 mt-0.5">{inst.description}</p>
                  </div>
                  <span className="text-xs font-semibold text-cyan-400">Connect →</span>
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowConnectModal(false)}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
