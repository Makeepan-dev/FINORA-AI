import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { Transactions } from './pages/Transactions';
import { Income } from './pages/Income';
import { Guardian } from './pages/Guardian';
import { Automation } from './pages/Automation';
import { Shopping } from './pages/Shopping';
import { Payments } from './pages/Payments';
import { Connections } from './pages/Connections';
import { SettingsPage } from './pages/Settings';
import { NearbySavings } from './pages/NearbySavings';
import { SavingsInsights } from './pages/SavingsInsights';
import { api } from './services/api';
import { DashboardData, ProductItem } from './types';
import { Loader2 } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [activeUserId, setActiveUserId] = useState<string>('usr_alex_chen');
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<ProductItem | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeScenarioId, setActiveScenarioId] = useState<string>('scen_01_normal_spending');

  useEffect(() => {
    loadDashboard(activeUserId);
  }, [activeUserId]);

  const loadDashboard = async (userId: string) => {
    setLoading(true);
    try {
      const data = await api.getDashboard(userId);
      setDashboardData(data);
      if (data.active_scenario_id) {
        setActiveScenarioId(data.active_scenario_id);
      }
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectUser = (userId: string) => {
    if (userId !== 'usr_alex_chen') {
      return;
    }
    setActiveUserId('usr_alex_chen');
  };

  const handleSelectProductForCheckout = (product: ProductItem) => {
    setSelectedProduct(product);
    setCurrentTab('payments');
  };

  const handleScenarioActivated = (scenarioId: string) => {
    setActiveScenarioId(scenarioId);
    loadDashboard(activeUserId);
  };

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen bg-[#0B0F19] text-white flex flex-col items-center justify-center space-y-4">
        <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center animate-pulse">
          <Loader2 className="w-6 h-6 text-slate-950 animate-spin" />
        </div>
        <p className="text-sm font-semibold tracking-wider text-slate-300">
          Initializing FINORA Financial Intelligence Network...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col selection:bg-cyan-500/20 selection:text-cyan-300">
      <Navbar
        currentUser={dashboardData?.user || null}
        onSelectUser={handleSelectUser}
        activeScenarioId={activeScenarioId}
      />

      <div className="flex-1 flex">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          savingsCount={dashboardData?.summary.potential_monthly_savings || 0}
        />

        <main className="flex-1 p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
          {dashboardData && (
            <>
              {currentTab === 'overview' && (
                <Overview
                  data={dashboardData}
                  onNavigateToGuardian={() => setCurrentTab('guardian')}
                  onNavigateToShopping={() => setCurrentTab('shopping')}
                />
              )}

              {currentTab === 'transactions' && (
                <Transactions
                  transactions={dashboardData.recent_transactions}
                  activeUserId={activeUserId}
                  onDataUpdated={() => loadDashboard(activeUserId)}
                />
              )}

              {currentTab === 'nearby' && (
                <NearbySavings
                  activeUserId={activeUserId}
                  onSelectForCheckout={handleSelectProductForCheckout}
                />
              )}

              {currentTab === 'savings' && (
                <SavingsInsights
                  activeUserId={activeUserId}
                  onSelectForCheckout={handleSelectProductForCheckout}
                  onNavigateToGuardian={() => setCurrentTab('guardian')}
                />
              )}

              {currentTab === 'income' && (
                <Income activeUserId={activeUserId} />
              )}

              {currentTab === 'guardian' && (
                <Guardian
                  dashboardData={dashboardData}
                  activeUserId={activeUserId}
                />
              )}

              {currentTab === 'automation' && (
                <Automation />
              )}

              {currentTab === 'shopping' && (
                <Shopping
                  onSelectForCheckout={handleSelectProductForCheckout}
                  activeUserId={activeUserId}
                />
              )}

              {currentTab === 'payments' && (
                <Payments
                  selectedProduct={selectedProduct}
                  activeUserId={activeUserId}
                  onClearSelectedProduct={() => setSelectedProduct(null)}
                />
              )}

              {currentTab === 'connections' && (
                <Connections activeUserId={activeUserId} />
              )}

              {currentTab === 'settings' && (
                <SettingsPage
                  activeUserId={activeUserId}
                  onSelectUser={handleSelectUser}
                  onScenarioActivated={handleScenarioActivated}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
